"""Класс для безопасного выполнения запросов PostgreSQL."""
import psycopg2
from psycopg2.extras import RealDictCursor

class Database:
    def __init__(self, settings):
        self.settings = settings

    def _run(self, sql, params=None, fetch=None):
        connection = psycopg2.connect(**self.settings)
        try:
            with connection:
                with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(sql, params or ())
                    if fetch == "one":
                        return cursor.fetchone()
                    if fetch == "all":
                        return cursor.fetchall()
            return None
        finally:
            connection.close()

    def fetch_all(self, sql, params=None):
        return self._run(sql, params, "all")

    def fetch_one(self, sql, params=None):
        return self._run(sql, params, "one")

    def execute(self, sql, params=None):
        return self._run(sql, params)
