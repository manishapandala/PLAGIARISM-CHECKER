import json
import math
import os
from typing import Iterable, List, Tuple


def _read_header_spec(header_file: str) -> List[Tuple[str, str]]:
    """
    Read header_file JSON and return ordered (column_name, postgres_type) pairs.

    Expected primary format:
        {"col1": "type1", "col2": "type2", ...}

    Also accepts list formats for compatibility:
        [{"name": "col1", "type": "type1"}, ...]
        [["col1", "type1"], ["col2", "type2"], ...]
    """
    with open(header_file, "r", encoding="utf-8") as fp:
        spec = json.load(fp)

    if isinstance(spec, dict):
        return [(str(col), str(col_type)) for col, col_type in spec.items()]

    if isinstance(spec, list):
        parsed: List[Tuple[str, str]] = []
        for item in spec:
            if isinstance(item, dict):
                # Accept common aliases for flexibility
                col_name = item.get("name") or item.get("column") or item.get("field")
                col_type = item.get("type") or item.get("datatype")
                if col_name is None or col_type is None:
                    raise ValueError("Invalid header spec entry in list[dict] format.")
                parsed.append((str(col_name), str(col_type)))
            elif isinstance(item, (list, tuple)) and len(item) == 2:
                parsed.append((str(item[0]), str(item[1])))
            else:
                raise ValueError("Unsupported list item in header spec.")
        return parsed

    raise ValueError("Unsupported JSON format for header specification.")


def _qident(identifier: str) -> str:
    """Safely quote a SQL identifier."""
    return '"' + str(identifier).replace('"', '""') + '"'


def _build_create_table_sql(table_name: str, columns: Iterable[Tuple[str, str]]) -> str:
    column_defs = [f"{_qident(col_name)} {col_type}" for col_name, col_type in columns]
    return f"CREATE TABLE {_qident(table_name)} ({', '.join(column_defs)})"


def _table_exists(connection, table_name: str) -> bool:
    with connection.cursor() as cursor:
        cursor.execute("SELECT to_regclass(%s);", (table_name,))
        return cursor.fetchone()[0] is not None


def load_data(table_name, csv_path, connection, header_file):
    """
    Load a CSV file into table_name using PostgreSQL COPY.

    If table_name does not already exist, it will be created using header_file.
    """
    columns = _read_header_spec(header_file)
    column_names = [name for name, _ in columns]

    with connection.cursor() as cursor:
        if not _table_exists(connection, table_name):
            cursor.execute(_build_create_table_sql(table_name, columns))

        copy_stmt = (
            f"COPY {_qident(table_name)} "
            f"({', '.join(_qident(col) for col in column_names)}) "
            "FROM STDIN WITH (FORMAT CSV, HEADER TRUE)"
        )

        resolved_csv_path = os.path.abspath(csv_path)
        with open(resolved_csv_path, "r", encoding="utf-8") as csv_file:
            cursor.copy_expert(copy_stmt, csv_file)

    connection.commit()


def range_partition(
    data_table_name,
    partition_table_name,
    num_partitions,
    header_file,
    column_to_partition,
    connection,
):
    """
    Create range partitions for column_to_partition and route all rows from data_table_name.

    Child partition names:
        <partition_table_name>0, <partition_table_name>1, ... <partition_table_name>N-1
    """
    if num_partitions <= 0:
        raise ValueError("num_partitions must be > 0")

    columns = _read_header_spec(header_file)

    with connection.cursor() as cursor:
        cursor.execute(f"DROP TABLE IF EXISTS {_qident(partition_table_name)} CASCADE")

        create_parent_sql = _build_create_table_sql(partition_table_name, columns)
        create_parent_sql = "{} PARTITION BY RANGE ({})".format(
            create_parent_sql, _qident(column_to_partition)
        )
        cursor.execute(create_parent_sql)

        cursor.execute(
            "SELECT MIN({0}), MAX({0}) FROM {1}".format(
                _qident(column_to_partition),
                _qident(data_table_name),
            )
        )
        min_val, max_val = cursor.fetchone()

        if min_val is None or max_val is None:
            # Empty source table: create empty uniform partitions [0,1), [1,2), ...
            min_val = 0
            max_val = num_partitions - 1

        partition_gap = int(math.ceil((max_val - min_val + 1) / float(num_partitions)))
        if partition_gap <= 0:
            partition_gap = 1

        for i in range(num_partitions):
            lower_bound = min_val + (i * partition_gap)
            upper_bound = min_val + ((i + 1) * partition_gap)

            cursor.execute(
                "CREATE TABLE {0} PARTITION OF {1} FOR VALUES FROM (%s) TO (%s)".format(
                    _qident(f"{partition_table_name}{i}"),
                    _qident(partition_table_name),
                ),
                (lower_bound, upper_bound),
            )

        cursor.execute(
            "INSERT INTO {0} SELECT * FROM {1}".format(
                _qident(partition_table_name),
                _qident(data_table_name),
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
    """
    Create round-robin partitions using inheritance and a BEFORE INSERT trigger.

    Child partition names:
        <partition_table_name>0, <partition_table_name>1, ... <partition_table_name>N-1
    """
    if num_partitions <= 0:
        raise ValueError("num_partitions must be > 0")

    columns = _read_header_spec(header_file)
    column_names = [name for name, _ in columns]

    trigger_function_name = f"{partition_table_name}_rr_insert_fn"
    trigger_name = f"{partition_table_name}_rr_insert_trigger"

    with connection.cursor() as cursor:
        cursor.execute(f"DROP TABLE IF EXISTS {_qident(partition_table_name)} CASCADE")
        cursor.execute(f"DROP FUNCTION IF EXISTS {_qident(trigger_function_name)}() CASCADE")

        cursor.execute(_build_create_table_sql(partition_table_name, columns))

        for i in range(num_partitions):
            cursor.execute(
                "CREATE TABLE {} () INHERITS ({})".format(
                    _qident(f"{partition_table_name}{i}"),
                    _qident(partition_table_name),
                )
            )

        # Initial round-robin load using row_number + modulo.
        columns_sql = ", ".join(_qident(c) for c in column_names)
        for i in range(num_partitions):
            cursor.execute(
                """
                INSERT INTO {child} ({cols})
                SELECT {cols}
                FROM (
                    SELECT {cols}, ROW_NUMBER() OVER () AS rn
                    FROM {src}
                ) AS numbered_rows
                WHERE MOD(rn - 1, %s) = %s
                """.format(
                    child=_qident(f"{partition_table_name}{i}"),
                    cols=columns_sql,
                    src=_qident(data_table_name),
                ),
                (num_partitions, i),
            )

        cursor.execute(
            """
            CREATE FUNCTION {}()
            RETURNS TRIGGER AS $$
            DECLARE
                partition_prefix TEXT := TG_ARGV[0];
                partition_count  INTEGER := TG_ARGV[1]::INTEGER;
                target_partition TEXT := NULL;
                current_partition TEXT;
                current_count BIGINT;
                min_count BIGINT := NULL;
                i INTEGER;
            BEGIN
                FOR i IN 0..partition_count - 1 LOOP
                    current_partition := partition_prefix || i::TEXT;
                    EXECUTE format('SELECT COUNT(*) FROM %I', current_partition)
                        INTO current_count;

                    IF min_count IS NULL OR current_count < min_count THEN
                        min_count := current_count;
                        target_partition := current_partition;
                    END IF;
                END LOOP;

                EXECUTE format('INSERT INTO %I SELECT ($1).*', target_partition) USING NEW;
                RETURN NULL;
            END;
            $$ LANGUAGE plpgsql
            """.format(
                _qident(trigger_function_name)
            )
        )

        cursor.execute(
            """
            CREATE TRIGGER {}
            BEFORE INSERT ON {}
            FOR EACH ROW
            EXECUTE FUNCTION {}(%s, %s)
            """.format(
                _qident(trigger_name),
                _qident(partition_table_name),
                _qident(trigger_function_name),
            ),
            (partition_table_name, num_partitions),
        )

    connection.commit()
