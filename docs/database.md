# Database

PostgreSQL in Docker (SQLite when `DATABASE_URL` is unset). Tables follow the specification:

- `products` (id, name, brand, category, price nullable, old_price, description, rating, stock, source, url, image_url, created_at, updated_at)
- `product_specifications` (id, product_id, key, value as JSON text)
- `reviews` (id, product_id, review_text, rating, source, created_at)
- `users` (id, session_id, created_at)
- `user_preferences` (budget, preferred_brands, preferred_categories, must_have_features, priority_features, updated_at)
- `search_history` (query, category, created_at, response_time, cache_hit) plus `brand`, `intent`
- `comparison_history` (product_ids, selected_product_id, created_at)
- `chat_messages` (added for real session history: role, content, payload JSON)

`price` is nullable on purpose: a missing price is represented as missing, never guessed.
