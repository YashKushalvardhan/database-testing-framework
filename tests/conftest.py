import pytest
from utils.db_connection import get_connection

@pytest.fixture
def db_connection():
    conn = get_connection()
    yield conn
    conn.close()


@pytest.fixture
def db_cursor(db_connection):
    """
    Provides a cursor wrapped in a transaction.
    After each test, changes are rolled back automatically —
    so tests never leave leftover data behind.
    """
    cursor = db_connection.cursor()
    yield cursor
    db_connection.rollback()   # undo any INSERT/UPDATE/DELETE done during the test
    cursor.close()