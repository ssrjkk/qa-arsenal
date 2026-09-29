"""Database client utilities."""

import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Optional, List, Dict

from core.config import get_settings
from core.logger import get_logger

logger = get_logger("utils.db")


class DBClient:
    """PostgreSQL client."""

    def __init__(self, dsn: Optional[str] = None):
        self.dsn = dsn or get_settings().db_url

    @contextmanager
    def connection(self):
        """Context manager for DB connection."""
        conn = psycopg2.connect(self.dsn)
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"DB error: {e}")
            raise
        finally:
            conn.close()

    @contextmanager
    def cursor(self, dict_cursor: bool = True):
        """Context manager for cursor."""
        with self.connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor if dict_cursor else None)
            try:
                yield cursor
            finally:
                cursor.close()

    def execute(self, query: str, params: tuple = None) -> List[Dict]:
        """Execute query and fetch results."""
        with self.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    def execute_one(self, query: str, params: tuple = None) -> Optional[Dict]:
        """Execute query and fetch one result."""
        with self.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()

    def execute_write(self, query: str, params: tuple = None) -> int:
        """Execute write query (INSERT/UPDATE/DELETE)."""
        with self.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.rowcount

    def table_exists(self, table_name: str) -> bool:
        """Check if table exists."""
        query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            )
        """
        result = self.execute_one(query, (table_name,))
        return result["exists"] if result else False

    def get_column_names(self, table_name: str) -> List[str]:
        """Get column names for table."""
        query = """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = %s
            ORDER BY ordinal_position
        """
        results = self.execute(query, (table_name,))
        return [r["column_name"] for r in results]

    def row_count(self, table_name: str) -> int:
        """Get row count for table."""
        query = f"SELECT COUNT(*) as cnt FROM {table_name}"
        result = self.execute_one(query)
        return result["cnt"] if result else 0
