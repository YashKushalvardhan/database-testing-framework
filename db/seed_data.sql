-- ============================================
-- Seed Data for ecommerce_test_db
-- Run AFTER schema.sql
-- ============================================

INSERT INTO categories (name) VALUES
('Electronics'),
('Clothing'),
('Books');

INSERT INTO users (name, email, password_hash) VALUES
('Yash Kushal', 'yash@test.com', 'hashed_pw_1'),
('Priya Sharma', 'priya@test.com', 'hashed_pw_2'),
('Rahul Verma', 'rahul@test.com', 'hashed_pw_3');

INSERT INTO products (name, price, stock_qty, category_id) VALUES
('iPhone 15', 79999.00, 50, 1),
('T-Shirt', 499.00, 200, 2),
('SQL Basics Book', 599.00, 100, 3);

INSERT INTO orders (user_id, status, total_amount) VALUES
(1, 'pending', 80498.00);

INSERT INTO order_items (order_id, product_id, quantity, price_at_order) VALUES
(1, 1, 1, 79999.00),
(1, 2, 1, 499.00);
