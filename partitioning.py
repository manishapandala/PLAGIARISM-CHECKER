import json
import math
from datetime import date, datetime, timedelta

from psycopg2 import sql


def _normalize_header(header_obj):
    if isinstance(header_obj, dict):
        return list(header_obj.items())

    if isinstance(header_obj, list):
        if not header_obj:
            return []

        if all(isinstance(item, (list, tuple)) and len(item) == 2 for item in header_obj):
            return [(item[0], item[1]) for item in header_obj]

        if all(isinstance(item, dict) for item in header_obj):
            pairs = []
            for item in header_obj:
                if len(item) == 1:
                    key = next(iter(item))
                    pairs.append((key, item[key]))
                    continue

                name_key = None
                for key in ("name", "column", "column_name", "field"):
                    if key in item:
                        name_key = key
                        break

                type_key = None
                for key in ("type", "column_type", "data_type"):
                    if key in item:
                        type_key = key
                        break

                if name_key and type_key:
                    pairs.append((item[name_key], item[type_key]))
                else:
                    raise ValueError("Unsupported header format for columns")

            return pairs

    raise ValueError("Unsupported header format")


def _load_header(header_file):
    with open(header_file, "r", encoding="utf-8") as file_handle:
        header_obj = json.load(file_handle)
    return _normalize_header(header_obj)


def _create_table(cursor, table_name, columns, partition_by=None):
    column_defs = sql.SQL(", ").join(
        sql.SQL("{} {}").format(sql.Identifier(col_name), sql.SQL(col_type))
        for col_name, col_type in columns
    )

    if partition_by:
        create_stmt = sql.SQL(
            "CREATE TABLE {} ({}) PARTITION BY RANGE ({})"
        ).format(
            sql.Identifier(table_name),
            column_defs,
            sql.Identifier(partition_by),
        )
    else:
        create_stmt = sql.SQL("CREATE TABLE {} ({})").format(
            sql.Identifier(table_name),
            column_defs,
        )

    cursor.execute(create_stmt)


def _compute_partition_bounds(min_val, max_val, num_partitions):
    if isinstance(min_val, datetime):
        total_seconds = (max_val - min_val).total_seconds()
        gap_seconds = int(
            math.ceil((total_seconds + 1) / float(num_partitions))
        )
        gap_delta = timedelta(seconds=gap_seconds)
        return [
            (min_val + gap_delta * idx, min_val + gap_delta * (idx + 1))
            for idx in range(num_partitions)
        ]

    if isinstance(min_val, date) and not isinstance(min_val, datetime):
        total_days = (max_val - min_val).days
        gap_days = int(math.ceil((total_days + 1) / float(num_partitions)))
        gap_delta = timedelta(days=gap_days)
        return [
            (min_val + gap_delta * idx, min_val + gap_delta * (idx + 1))
            for idx in range(num_partitions)
        ]

    gap = int(
        math.ceil((float(max_val) - float(min_val) + 1) / float(num_partitions))
    )
    return [
        (min_val + gap * idx, min_val + gap * (idx + 1))
        for idx in range(num_partitions)
    ]


def _copy_from_csv(cursor, table_name, csv_path):
    copy_stmt = sql.SQL(
        "COPY {} FROM STDIN WITH (FORMAT csv, HEADER true)"
    ).format(sql.Identifier(table_name))
    with open(csv_path, "r", encoding="utf-8") as file_handle:
        cursor.copy_expert(copy_stmt.as_string(cursor), file_handle)


def _normalize_insert_data(insert_data):
    if isinstance(insert_data, str):
        return json.loads(insert_data)
    return insert_data


def _insert_row(cursor, table_name, insert_data):
    insert_data = _normalize_insert_data(insert_data)
    if isinstance(insert_data, dict):
        columns = list(insert_data.keys())
        values = [insert_data[col] for col in columns]
        columns_sql = sql.SQL(", ").join(
            sql.Identifier(col) for col in columns
        )
        placeholders = sql.SQL(", ").join(
            [sql.Placeholder() for _ in values]
        )
        insert_stmt = sql.SQL(
            "INSERT INTO {} ({}) VALUES ({})"
        ).format(sql.Identifier(table_name), columns_sql, placeholders)
        cursor.execute(insert_stmt, values)
        return

    if isinstance(insert_data, (list, tuple)):
        placeholders = sql.SQL(", ").join(
            [sql.Placeholder() for _ in insert_data]
        )
        insert_stmt = sql.SQL("INSERT INTO {} VALUES ({})").format(
            sql.Identifier(table_name),
            placeholders,
        )
        cursor.execute(insert_stmt, list(insert_data))
        return

    raise ValueError("Unsupported insert data format")


def load_data(table_name, csv_path, connection, header_file):
    columns = _load_header(header_file)
    with connection.cursor() as cursor:
        cursor.execute(
            sql.SQL("DROP TABLE IF EXISTS {} CASCADE").format(
                sql.Identifier(table_name)
            )
        )
        _create_table(cursor, table_name, columns)
        _copy_from_csv(cursor, table_name, csv_path)
    connection.commit()


def range_partition(
    data_table_name,
    partition_table_name,
    num_partitions,
    header_file,
    column_to_partition,
    connection,
):
    columns = _load_header(header_file)
    if num_partitions <= 0:
        raise ValueError("num_partitions must be positive")

    with connection.cursor() as cursor:
        cursor.execute(
            sql.SQL("DROP TABLE IF EXISTS {} CASCADE").format(
                sql.Identifier(partition_table_name)
            )
        )
        _create_table(
            cursor,
            partition_table_name,
            columns,
            partition_by=column_to_partition,
        )

        cursor.execute(
            sql.SQL("SELECT MIN({col}), MAX({col}) FROM {table}").format(
                col=sql.Identifier(column_to_partition),
                table=sql.Identifier(data_table_name),
            )
        )
        min_val, max_val = cursor.fetchone()
        if min_val is None or max_val is None:
            connection.commit()
            return

        bounds = _compute_partition_bounds(min_val, max_val, num_partitions)
        for idx, (lower_bound, upper_bound) in enumerate(bounds):
            child_name = f"{partition_table_name}{idx}"
            cursor.execute(
                sql.SQL(
                    "CREATE TABLE {} PARTITION OF {} "
                    "FOR VALUES FROM (%s) TO (%s)"
                ).format(
                    sql.Identifier(child_name),
                    sql.Identifier(partition_table_name),
                ),
                (lower_bound, upper_bound),
            )

        cursor.execute(
            sql.SQL("INSERT INTO {} SELECT * FROM {}").format(
                sql.Identifier(partition_table_name),
                sql.Identifier(data_table_name),
            )
        )
    connection.commit()


def round_robin_partition(
    data_table_name,
    partition_table_name,
    num_partitions,
    header_file,
    connection,
):
    columns = _load_header(header_file)
    if num_partitions <= 0:
        raise ValueError("num_partitions must be positive")

    column_names = [col for col, _ in columns]
    columns_sql = sql.SQL(", ").join(
        sql.Identifier(col) for col in column_names
    )

    with connection.cursor() as cursor:
        cursor.execute(
            sql.SQL("DROP TABLE IF EXISTS {} CASCADE").format(
                sql.Identifier(partition_table_name)
            )
        )
        _create_table(cursor, partition_table_name, columns)

        for idx in range(num_partitions):
            child_name = f"{partition_table_name}{idx}"
            cursor.execute(
                sql.SQL("CREATE TABLE {} () INHERITS ({})").format(
                    sql.Identifier(child_name),
                    sql.Identifier(partition_table_name),
                )
            )

        for idx in range(num_partitions):
            child_name = f"{partition_table_name}{idx}"
            insert_stmt = sql.SQL(
                "INSERT INTO {child} ({cols}) "
                "SELECT {cols} FROM ("
                "SELECT {cols}, ROW_NUMBER() OVER () AS rn FROM {data}"
                ") AS t "
                "WHERE (t.rn - 1) % %s = %s"
            ).format(
                child=sql.Identifier(child_name),
                cols=columns_sql,
                data=sql.Identifier(data_table_name),
            )
            cursor.execute(insert_stmt, (num_partitions, idx))

        function_name = f"{partition_table_name}_insert_fn"
        trigger_name = f"{partition_table_name}_insert_trigger"

        cursor.execute(
            sql.SQL(
                """
                CREATE OR REPLACE FUNCTION {}()
                RETURNS TRIGGER AS $$
                DECLARE
                    min_count integer;
                    target_partition text;
                    current_count integer;
                    idx integer;
                BEGIN
                    min_count := NULL;
                    target_partition := NULL;
                    FOR idx IN 0..{} LOOP
                        EXECUTE format('SELECT COUNT(*) FROM %I', {} || idx)
                            INTO current_count;
                        IF min_count IS NULL OR current_count < min_count THEN
                            min_count := current_count;
                            target_partition := {} || idx;
                        END IF;
                    END LOOP;

                    EXECUTE format('INSERT INTO %I VALUES ($1.*)', target_partition)
                        USING NEW;
                    RETURN NULL;
                END;
                $$ LANGUAGE plpgsql;
                """
            ).format(
                sql.Identifier(function_name),
                sql.Literal(num_partitions - 1),
                sql.Literal(partition_table_name),
                sql.Literal(partition_table_name),
            )
        )

        cursor.execute(
            sql.SQL("DROP TRIGGER IF EXISTS {} ON {}").format(
                sql.Identifier(trigger_name),
                sql.Identifier(partition_table_name),
            )
        )
        cursor.execute(
            sql.SQL(
                "CREATE TRIGGER {} BEFORE INSERT ON {} "
                "FOR EACH ROW EXECUTE FUNCTION {}()"
            ).format(
                sql.Identifier(trigger_name),
                sql.Identifier(partition_table_name),
                sql.Identifier(function_name),
            )
        )
    connection.commit()


def range_insert(table_name, insert_data, column_to_partition, connection):
    del column_to_partition
    with connection.cursor() as cursor:
        _insert_row(cursor, table_name, insert_data)
    connection.commit()


def round_robin_insert(table_name, insert_data, connection):
    with connection.cursor() as cursor:
        _insert_row(cursor, table_name, insert_data)
    connection.commit()
