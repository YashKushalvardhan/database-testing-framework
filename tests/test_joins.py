def test_join_order_with_user_and_products(db_connection, db_cursor):
    """
    Create a full order (user + order + order_items + product),
    then verify a JOIN query returns correctly linked data.
    """
    # Setup: create user
    db_cursor.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s) RETURNING id;",
        ("Join Test User", "jointest@example.com", "hashed_pw")
    )
    user_id = db_cursor.fetchone()[0]

    # Setup: get an existing product dynamically
    db_cursor.execute("SELECT id, name, price FROM products LIMIT 1;")
    product_id, product_name, product_price = db_cursor.fetchone()

    # Setup: create order
    db_cursor.execute(
        "INSERT INTO orders (user_id, status, total_amount) VALUES (%s, %s, %s) RETURNING id;",
        (user_id, "pending", product_price)
    )
    order_id = db_cursor.fetchone()[0]

    # Setup: create order_item
    db_cursor.execute(
        "INSERT INTO order_items (order_id, product_id, quantity, price_at_order) VALUES (%s, %s, %s, %s);",
        (order_id, product_id, 2, product_price)
    )

    # The actual JOIN query being tested
    db_cursor.execute("""
        SELECT u.name, p.name, oi.quantity, oi.price_at_order
        FROM orders o
        JOIN users u ON o.user_id = u.id
        JOIN order_items oi ON oi.order_id = o.id
        JOIN products p ON p.id = oi.product_id
        WHERE o.id = %s;
    """, (order_id,))

    result = db_cursor.fetchone()

    assert result[0] == "Join Test User"
    assert result[1] == product_name
    assert result[2] == 2
    assert result[3] == product_price


def test_user_with_no_orders_not_in_inner_join(db_connection, db_cursor):
    """
    A user with zero orders should NOT appear in an INNER JOIN
    between users and orders (this validates JOIN behavior itself).
    """
    db_cursor.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s) RETURNING id;",
        ("Lonely User", "lonely@example.com", "hashed_pw")
    )
    user_id = db_cursor.fetchone()[0]

    db_cursor.execute("""
        SELECT u.id FROM users u
        JOIN orders o ON o.user_id = u.id
        WHERE u.id = %s;
    """, (user_id,))

    result = db_cursor.fetchone()
    assert result is None  # INNER JOIN excludes users without matching orders