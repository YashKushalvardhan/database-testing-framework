import pytest
import psycopg2


# ============================================
# INSERT Tests
# ============================================

def test_insert_user_success(db_connection, db_cursor):
    """Insert a new user and verify it's actually saved with correct values."""
    db_cursor.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s) RETURNING id;",
        ("Test User", "testuser@example.com", "hashed_pw")
    )
    new_id = db_cursor.fetchone()[0]

    # Verify by reading it back
    db_cursor.execute("SELECT name, email FROM users WHERE id = %s;", (new_id,))
    result = db_cursor.fetchone()

    assert result[0] == "Test User"
    assert result[1] == "testuser@example.com"


def test_insert_duplicate_email_fails(db_connection, db_cursor):
    """Inserting a duplicate email should raise a UniqueViolation error."""
    with pytest.raises(psycopg2.errors.UniqueViolation):
        db_cursor.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s);",
            ("Duplicate User", "yash@test.com", "hashed_pw")  # already exists from seed data
        )
    db_connection.rollback()  # transaction is aborted after error, must rollback before next query


def test_insert_negative_price_fails(db_connection, db_cursor):
    """Inserting a negative price should raise a CheckViolation error."""
    with pytest.raises(psycopg2.errors.CheckViolation):
        db_cursor.execute(
            "INSERT INTO products (name, price, stock_qty, category_id) VALUES (%s, %s, %s, %s);",
            ("Bad Product", -50.00, 10, 1)
        )
    db_connection.rollback()


def test_insert_invalid_foreign_key_fails(db_connection, db_cursor):
    """Inserting a product with a non-existent category_id should fail."""
    with pytest.raises(psycopg2.errors.ForeignKeyViolation):
        db_cursor.execute(
            "INSERT INTO products (name, price, stock_qty, category_id) VALUES (%s, %s, %s, %s);",
            ("Ghost Product", 100.00, 10, 999)
        )
    db_connection.rollback()


# ============================================
# UPDATE Tests
# ============================================

def test_update_user_name(db_connection, db_cursor):
    """Update a user's name and verify the change persisted, other fields unchanged."""
    # Create our own test user instead of relying on seed data
    db_cursor.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s) RETURNING id;",
        ("Original Name", "updatetest@example.com", "hashed_pw")
    )
    user_id = db_cursor.fetchone()[0]

    db_cursor.execute(
        "UPDATE users SET name = %s WHERE id = %s;",
        ("Updated Name", user_id)
    )

    db_cursor.execute("SELECT name, email FROM users WHERE id = %s;", (user_id,))
    result = db_cursor.fetchone()

    assert result[0] == "Updated Name"
    assert result[1] == "updatetest@example.com"


# ============================================
# DELETE Tests
# ============================================

def test_delete_user(db_connection, db_cursor):
    """Insert a temp user, delete it, verify it's gone."""
    db_cursor.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s) RETURNING id;",
        ("Temp User", "temp@example.com", "hashed_pw")
    )
    temp_id = db_cursor.fetchone()[0]

    db_cursor.execute("DELETE FROM users WHERE id = %s;", (temp_id,))

    db_cursor.execute("SELECT * FROM users WHERE id = %s;", (temp_id,))
    result = db_cursor.fetchone()

    assert result is None


def test_cascade_delete_removes_order_items(db_connection, db_cursor):
    # Create our own user
    db_cursor.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s) RETURNING id;",
        ("Cascade Test User", "cascadetest@example.com", "hashed_pw")
    )
    user_id = db_cursor.fetchone()[0]

    # Fetch any existing valid product_id dynamically instead of hardcoding
    db_cursor.execute("SELECT id FROM products LIMIT 1;")
    row = db_cursor.fetchone()
    assert row is not None, "No products found in DB — seed data missing"
    product_id = row[0]

    db_cursor.execute(
        "INSERT INTO orders (user_id, status, total_amount) VALUES (%s, %s, %s) RETURNING id;",
        (user_id, "pending", 500.00)
    )
    order_id = db_cursor.fetchone()[0]

    db_cursor.execute(
        "INSERT INTO order_items (order_id, product_id, quantity, price_at_order) VALUES (%s, %s, %s, %s);",
        (order_id, product_id, 1, 500.00)
    )

    db_cursor.execute("SELECT COUNT(*) FROM order_items WHERE order_id = %s;", (order_id,))
    assert db_cursor.fetchone()[0] == 1

    db_cursor.execute("DELETE FROM orders WHERE id = %s;", (order_id,))

    db_cursor.execute("SELECT COUNT(*) FROM order_items WHERE order_id = %s;", (order_id,))
    assert db_cursor.fetchone()[0] == 0