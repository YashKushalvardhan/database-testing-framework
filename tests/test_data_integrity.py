import psycopg2
import pytest


def test_no_orphan_order_items(db_cursor):
    """
    Data integrity audit: every order_item must point to a valid order and product.
    This simulates a real-world 'orphan record' check — common in data quality audits.
    """
    db_cursor.execute("""
        SELECT oi.id FROM order_items oi
        LEFT JOIN orders o ON oi.order_id = o.id
        WHERE o.id IS NULL;
    """)
    orphans = db_cursor.fetchall()
    assert len(orphans) == 0, f"Found {len(orphans)} order_items with no matching order"


def test_no_products_with_invalid_category(db_cursor):
    """Every product's category_id (if set) must exist in categories table."""
    db_cursor.execute("""
        SELECT p.id FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.category_id IS NOT NULL AND c.id IS NULL;
    """)
    orphans = db_cursor.fetchall()
    assert len(orphans) == 0, f"Found {len(orphans)} products with invalid category_id"


def test_deleting_category_in_use_fails(db_connection, db_cursor):
    """
    categories -> products has NO cascade rule defined.
    So deleting a category that's still referenced by a product should FAIL,
    protecting existing product data (this is intentional design, not a bug).
    """
    # Create a fresh category and a product using it
    db_cursor.execute("INSERT INTO categories (name) VALUES (%s) RETURNING id;", ("Temp Category",))
    category_id = db_cursor.fetchone()[0]

    db_cursor.execute(
        "INSERT INTO products (name, price, stock_qty, category_id) VALUES (%s, %s, %s, %s);",
        ("Temp Product", 100.00, 5, category_id)
    )

    with pytest.raises(psycopg2.errors.ForeignKeyViolation):
        db_cursor.execute("DELETE FROM categories WHERE id = %s;", (category_id,))

    db_connection.rollback()


def test_deleting_unused_category_succeeds(db_connection, db_cursor):
    """A category with no products attached should delete cleanly."""
    db_cursor.execute("INSERT INTO categories (name) VALUES (%s) RETURNING id;", ("Unused Category",))
    category_id = db_cursor.fetchone()[0]

    db_cursor.execute("DELETE FROM categories WHERE id = %s;", (category_id,))

    db_cursor.execute("SELECT * FROM categories WHERE id = %s;", (category_id,))
    assert db_cursor.fetchone() is None