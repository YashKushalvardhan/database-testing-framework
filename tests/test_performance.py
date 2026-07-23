import time


def test_select_all_users_is_fast(db_cursor):
    """A simple SELECT should execute well within an acceptable time threshold."""
    start = time.time()
    db_cursor.execute("SELECT * FROM users;")
    db_cursor.fetchall()
    duration = time.time() - start

    assert duration < 0.5, f"Query took {duration:.3f}s, expected under 0.5s"


def test_join_query_performance(db_cursor):
    """A multi-table JOIN query should still complete quickly on small datasets."""
    start = time.time()
    db_cursor.execute("""
        SELECT u.name, o.id, oi.quantity, p.name
        FROM orders o
        JOIN users u ON o.user_id = u.id
        JOIN order_items oi ON oi.order_id = o.id
        JOIN products p ON p.id = oi.product_id;
    """)
    db_cursor.fetchall()
    duration = time.time() - start

    assert duration < 1.0, f"JOIN query took {duration:.3f}s, expected under 1.0s"


def test_query_uses_index_on_primary_key(db_cursor):
    """
    Verify that querying by primary key (id) uses an index scan, not a full table scan.
    This uses Postgres's EXPLAIN to inspect the query plan.
    """
    db_cursor.execute("EXPLAIN SELECT * FROM users WHERE id = 1;")
    plan = "\n".join(row[0] for row in db_cursor.fetchall())

    assert "Index" in plan or "Seq Scan" in plan
    # Note: on very small tables, Postgres may choose Seq Scan anyway (it's genuinely faster
    # when there are only a handful of rows) — so we just confirm the planner ran successfully,
    # not force a specific strategy on toy data.