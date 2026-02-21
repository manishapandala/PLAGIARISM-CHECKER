# Import required libraries
import psycopg2
from psycopg2 import sql


def _normalize_table_name(table_name):
    """
    Normalize table names so unquoted references in tester SQL keep working.
    """
    return table_name.lower()


def point_query(parent_partition_table_name, utc_val, save_table_name, connection):
    """
    Use this function to perform a point query on the given table.
    The table input is either range (range_part) or round-robin (rrobin_part) partitioned.
    The output is saved in a table with the name save_table_name.
    """
    parent_table = _normalize_table_name(parent_partition_table_name)
    output_table = _normalize_table_name(save_table_name)

    with connection.cursor() as cursor:
        cursor.execute(
            sql.SQL("DROP TABLE IF EXISTS {} CASCADE;").format(
                sql.Identifier(output_table)
            )
        )
        cursor.execute(
            sql.SQL(
                """
                CREATE TABLE {} AS
                SELECT *
                FROM {}
                WHERE created_utc = %s
                ORDER BY created_utc ASC;
                """
            ).format(sql.Identifier(output_table), sql.Identifier(parent_table)),
            (utc_val,),
        )
    connection.commit()


def range_query(parent_partition_table_name, utc_min_val, utc_max_val, save_table_name, connection):
    """
    Use this function to perform a range query on the given table.
    The table input is either range (range_part) or round-robin (rrobin_part) partitioned.
    The output is saved in a table with the name save_table_name.
    Range filter is (utc_min_val, utc_max_val].
    """
    parent_table = _normalize_table_name(parent_partition_table_name)
    output_table = _normalize_table_name(save_table_name)

    with connection.cursor() as cursor:
        cursor.execute(
            sql.SQL("DROP TABLE IF EXISTS {} CASCADE;").format(
                sql.Identifier(output_table)
            )
        )
        cursor.execute(
            sql.SQL(
                """
                CREATE TABLE {} AS
                SELECT *
                FROM {}
                WHERE created_utc > %s
                  AND created_utc <= %s
                ORDER BY created_utc ASC;
                """
            ).format(sql.Identifier(output_table), sql.Identifier(parent_table)),
            (utc_min_val, utc_max_val),
        )
    connection.commit()
