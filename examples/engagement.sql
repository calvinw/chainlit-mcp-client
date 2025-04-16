-- Database Schema for User Session Analysis

-- Sessions table to store overall session data
CREATE TABLE sessions (
    session_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50),
    session_start TIMESTAMP,
    session_end TIMESTAMP,
    session_duration INT,  -- in seconds
    device_type VARCHAR(20),
    os VARCHAR(50),
    browser VARCHAR(50),
    entry_page VARCHAR(255),
    exit_page VARCHAR(255),
    is_bounce BOOLEAN,
    referrer_source VARCHAR(100),
    utm_source VARCHAR(100),
    utm_medium VARCHAR(100),
    utm_campaign VARCHAR(100)
);

-- Page views within a session
CREATE TABLE page_views (
    page_view_id VARCHAR(50) PRIMARY KEY,
    session_id VARCHAR(50),
    page_url VARCHAR(255),
    page_title VARCHAR(255),
    timestamp TIMESTAMP,
    time_spent INT,  -- in seconds
    scroll_depth FLOAT,  -- percentage from 0 to 1
    previous_page_url VARCHAR(255),
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- User interactions on pages
CREATE TABLE interactions (
    interaction_id VARCHAR(50) PRIMARY KEY,
    session_id VARCHAR(50),
    page_view_id VARCHAR(50),
    interaction_type VARCHAR(50),  -- click, hover, form_submit, etc.
    element_id VARCHAR(100),
    element_type VARCHAR(50),  -- button, link, form, etc.
    timestamp TIMESTAMP,
    additional_data JSON,  -- flexible field for custom event data
    FOREIGN KEY (session_id) REFERENCES sessions(session_id),
    FOREIGN KEY (page_view_id) REFERENCES page_views(page_view_id)
);

-- Conversion events
CREATE TABLE conversions (
    conversion_id VARCHAR(50) PRIMARY KEY,
    session_id VARCHAR(50),
    user_id VARCHAR(50),
    conversion_type VARCHAR(50),  -- purchase, signup, download, etc.
    timestamp TIMESTAMP,
    value DECIMAL(10,2),  -- monetary value if applicable
    product_id VARCHAR(50),  -- if applicable
    conversion_details JSON,  -- flexible field for additional details
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- User profile information
CREATE TABLE users (
    user_id VARCHAR(50) PRIMARY KEY,
    first_seen_date DATE,
    user_segment VARCHAR(50),
    lifetime_value DECIMAL(10,2),
    total_sessions INT,
    total_conversions INT,
    device_preference VARCHAR(20),
    is_returning BOOLEAN
);

-- Sample data inserts

-- Sample sessions
INSERT INTO sessions VALUES 
('s-12345', 'u-789', '2025-04-01 09:32:15', '2025-04-01 09:44:19', 724, 'mobile', 'iOS 18.2', 'Safari', '/landing/spring-promo', '/checkout/confirmation', FALSE, 'google', 'google', 'cpc', 'spring_sale_2025'),
('s-12346', 'u-790', '2025-04-01 10:15:33', '2025-04-01 10:17:12', 99, 'desktop', 'Windows 11', 'Chrome', '/products/category/shoes', '/products/category/shoes', TRUE, 'direct', NULL, NULL, NULL),
('s-12347', 'u-791', '2025-04-01 11:22:45', '2025-04-01 11:48:17', 1532, 'tablet', 'iPadOS 18.1', 'Safari', '/blog/summer-trends', '/products/item/summer-hat', FALSE, 'instagram', 'instagram', 'social', 'influencer_summer25');

-- Sample page views
INSERT INTO page_views VALUES
('pv-001', 's-12345', '/landing/spring-promo', 'Spring Sale - Up to 50% Off', '2025-04-01 09:32:15', 45, 0.8, NULL),
('pv-002', 's-12345', '/products/category/shoes', 'Running Shoes Collection', '2025-04-01 09:33:00', 187, 0.7, '/landing/spring-promo'),
('pv-003', 's-12345', '/products/item/running-shoes-v2', 'Ultra Boost Running Shoes V2', '2025-04-01 09:36:07', 312, 0.9, '/products/category/shoes'),
('pv-004', 's-12345', '/cart', 'Your Shopping Cart', '2025-04-01 09:41:19', 63, 1.0, '/products/item/running-shoes-v2'),
('pv-005', 's-12345', '/checkout', 'Checkout - Payment & Shipping', '2025-04-01 09:42:22', 98, 1.0, '/cart'),
('pv-006', 's-12345', '/checkout/confirmation', 'Order Confirmation', '2025-04-01 09:44:00', 19, 0.3, '/checkout'),
('pv-007', 's-12346', '/products/category/shoes', 'Running Shoes Collection', '2025-04-01 10:15:33', 99, 0.3, NULL),
('pv-008', 's-12347', '/blog/summer-trends', 'Top 10 Summer Fashion Trends 2025', '2025-04-01 11:22:45', 248, 1.0, NULL),
('pv-009', 's-12347', '/products/category/accessories', 'Summer Accessories', '2025-04-01 11:26:53', 325, 0.9, '/blog/summer-trends'),
('pv-010', 's-12347', '/products/item/summer-hat', 'Wide Brim Straw Summer Hat', '2025-04-01 11:32:18', 627, 1.0, '/products/category/accessories');

-- Sample interactions
INSERT INTO interactions VALUES
('i-001', 's-12345', 'pv-001', 'click', 'featured_product_3', 'product_card', '2025-04-01 09:33:01', '{"product_id": "p-567", "position": "featured_carousel", "was_animated": true}'),
('i-002', 's-12345', 'pv-002', 'filter', 'product_filter', 'filter_control', '2025-04-01 09:34:22', '{"filter_value": "running", "category": "shoes", "items_shown": 24}'),
('i-003', 's-12345', 'pv-002', 'sort', 'sort_control', 'dropdown', '2025-04-01 09:35:10', '{"sort_value": "price_high_low", "previous_sort": "relevance"}'),
('i-004', 's-12345', 'pv-003', 'click', 'size_selector', 'size_button', '2025-04-01 09:38:22', '{"size_selected": "10", "in_stock": true}'),
('i-005', 's-12345', 'pv-003', 'click', 'add_to_cart_button', 'button', '2025-04-01 09:39:45', '{"product_id": "p-567", "quantity": 1, "price": 129.99}'),
('i-006', 's-12345', 'pv-004', 'click', 'checkout_button', 'button', '2025-04-01 09:41:01', '{"cart_value": 129.99, "items_count": 1}'),
('i-007', 's-12346', 'pv-007', 'scroll', 'page', 'page', '2025-04-01 10:16:45', '{"scroll_depth": 0.3, "time_on_page": 72}'),
('i-008', 's-12347', 'pv-008', 'click', 'read_more', 'button', '2025-04-01 11:24:32', '{"article_section": "accessories", "position": "middle"}'),
('i-009', 's-12347', 'pv-009', 'filter', 'product_filter', 'filter_control', '2025-04-01 11:28:10', '{"filter_value": "hats", "category": "accessories", "items_shown": 12}'),
('i-010', 's-12347', 'pv-010', 'click', 'add_to_wishlist', 'button', '2025-04-01 11:35:45', '{"product_id": "p-789", "wishlist_count": 3}');

-- Sample conversions
INSERT INTO conversions VALUES
('c-001', 's-12345', 'u-789', 'purchase', '2025-04-01 09:44:15', 129.99, 'p-567', '{"order_id": "ord-5678", "payment_method": "credit_card", "shipping_method": "standard"}'),
('c-002', 's-12347', 'u-791', 'add_to_wishlist', '2025-04-01 11:35:45', 0, 'p-789', '{"wishlist_name": "Summer Shopping", "public": false}');

-- Sample user profiles
INSERT INTO users VALUES
('u-789', '2024-12-15', 'returning_customer', 430.45, 7, 3, 'mobile', TRUE),
('u-790', '2025-04-01', 'new_visitor', 0, 1, 0, 'desktop', FALSE),
('u-791', '2025-02-22', 'browsing_customer', 89.99, 4, 1, 'tablet', TRUE);
