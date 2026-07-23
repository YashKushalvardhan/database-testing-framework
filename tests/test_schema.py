def test_users_table_has_correct_columns(db_cursor):
    """Verify users table has exactly the expected columns."""
    db_cursor.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'users';
    """)
    columns = {row[0] for row in db_cursor.fetchall()}
    expected_columns = {"id", "name", "email", "password_hash", "created_at"}
    assert columns == expected_columns


def test_email_column_is_unique(db_cursor):
    """Verify email column has a UNIQUE constraint."""
    db_cursor.execute("""
        SELECT constraint_type FROM information_schema.table_constraints
        WHERE table_name = 'users' AND constraint_type = 'UNIQUE';
    """)
    result = db_cursor.fetchone()
    assert result is not None, "Expected a UNIQUE constraint on users table"


def test_order_items_has_foreign_keys(db_cursor):
    """Verify order_items has foreign key constraints to orders and products."""
    db_cursor.execute("""
        SELECT COUNT(*) FROM information_schema.table_constraints
        WHERE table_name = 'order_items' AND constraint_type     = 'FOREIGN KEY';
    """)
    fk_count = db_cursor.fetchone()[0]
    assert fk_count == 2  # order_id -> orders, product_id -> products