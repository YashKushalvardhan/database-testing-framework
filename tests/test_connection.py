def test_database_connection_successful(db_connection):
    """Sanity check: can we connect to the database at all?"""
    assert db_connection is not None
    assert db_connection.closed == 0  # 0 means connection is open


def test_users_table_exists(db_cursor):
    """Verify the users table exists in the database."""
    db_cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = 'users'
        );
    """)
    result = db_cursor.fetchone()[0]
    assert result is True