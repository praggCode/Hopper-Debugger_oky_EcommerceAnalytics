# Data Dictionary — Olist E-Commerce Dataset

This dataset will be used to analyze sales performance, customer retention, and delivery efficiency in a multi-seller e-commerce environment.

**Source:** https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce  
**Tables:** 9 relational CSV files  
**Total Orders:** ~100,000  
**Period:** 2016–2018  

---

## 1. Orders (`olist_orders_dataset.csv`)

| Column Name | Data Type | Description | Notes |
|---|---|---|---|
| order_id | string | Unique identifier for each order | Primary key |
| customer_id | string | Links to customers table | Foreign key |
| order_status | string | Order status (delivered, shipped, canceled, etc.) | Contains: delivered, shipped, canceled, unavailable, invoiced, processing, created, approved |
| order_purchase_timestamp | datetime | Date and time order was placed | No nulls expected |
| order_approved_at | datetime | Time when payment was approved | Has missing values |
| order_delivered_carrier_date | datetime | When order was handed to carrier | Has missing values |
| order_delivered_customer_date | datetime | When customer received the order | Has missing values — key for delivery delay analysis |
| order_estimated_delivery_date | datetime | Estimated delivery date provided at purchase | Used to compute delivery delay KPI |

---

## 2. Order Items (`olist_order_items_dataset.csv`)

| Column Name | Data Type | Description | Notes |
|---|---|---|---|
| order_id | string | Links to orders table | Foreign key |
| order_item_id | integer | Item sequence within an order | Orders can have multiple items |
| product_id | string | Links to products table | Foreign key |
| seller_id | string | Links to sellers table | Foreign key |
| shipping_limit_date | datetime | Deadline for seller to ship | Used for seller performance analysis |
| price | float | Product price in BRL | Key metric for revenue analysis |
| freight_value | float | Shipping cost in BRL | Used for delivery cost analysis |

---

## 3. Customers (`olist_customers_dataset.csv`)

| Column Name | Data Type | Description | Notes |
|---|---|---|---|
| customer_id | string | Per-order customer identifier | Changes with each new order — not suitable for retention analysis |
| customer_unique_id | string | True unique identifier per customer across all orders | Use this for repeat purchase / retention analysis |
| customer_zip_code_prefix | string | First 5 digits of zip code | Links to geolocation table |
| customer_city | string | Customer city | May have inconsistent casing |
| customer_state | string | Customer state (2-letter code) | Used for regional analysis |

---

## 4. Payments (`olist_order_payments_dataset.csv`)

| Column Name | Data Type | Description | Notes |
|---|---|---|---|
| order_id | string | Links to orders table | Foreign key |
| payment_sequential | integer | Payment sequence number | Orders can be paid in multiple parts |
| payment_type | string | Payment method (credit_card, boleto, voucher, debit_card) | Used for payment behavior analysis |
| payment_installments | integer | Number of installments chosen | payment_installments contains invalid 0 values — requires correction |
| payment_value | float | Amount paid in BRL | Aggregate per order for revenue KPIs |

---

## 5. Reviews (`olist_order_reviews_dataset.csv`)

| Column Name | Data Type | Description | Notes |
|---|---|---|---|
| review_id | string | Unique identifier for review | Primary key |
| order_id | string | Links to orders table | Foreign key |
| review_score | integer | Customer rating (1–5 stars) | Key satisfaction metric — no nulls |
| review_comment_title | string | Short title of review | Mostly null — not used in analysis |
| review_comment_message | string | Full review text | Mostly null — text analysis optional |
| review_creation_date | datetime | When review form was sent | — |
| review_answer_timestamp | datetime | When review was submitted | Used for response time analysis |

---

## 6. Products (`olist_products_dataset.csv`)

| Column Name | Data Type | Description | Notes |
|---|---|---|---|
| product_id | string | Unique identifier for product | Primary key |
| product_category_name | string | Category name in Portuguese | Has missing values — join with translation table |
| product_name_length | integer | Character count of product name | Has missing values |
| product_description_length | integer | Character count of description | Has missing values |
| product_photos_qty | integer | Number of product photos | Has missing values |
| product_weight_g | float | Weight in grams | Has missing values — needed for freight analysis |
| product_length_cm | float | Length in cm | Has missing values |
| product_height_cm | float | Height in cm | Has missing values |
| product_width_cm | float | Width in cm | Has missing values |

---

## 7. Sellers (`olist_sellers_dataset.csv`)

| Column Name | Data Type | Description | Notes |
|---|---|---|---|
| seller_id | string | Unique identifier for seller | Primary key |
| seller_zip_code_prefix | string | First 5 digits of zip code | Links to geolocation table |
| seller_city | string | City of seller | Inconsistent casing — needs standardization |
| seller_state | string | State of seller (2-letter code) | Used for regional seller analysis |

---

## 8. Geolocation (`olist_geolocation_dataset.csv`)

| Column Name | Data Type | Description | Notes |
|---|---|---|---|
| geolocation_zip_code_prefix | string | Zip code prefix (5 digits) | Has duplicate entries per zip code |
| geolocation_lat | float | Latitude coordinate | Use average per zip for mapping |
| geolocation_lng | float | Longitude coordinate | Use average per zip for mapping |
| geolocation_city | string | City name | Inconsistent — has accented characters |
| geolocation_state | string | State (2-letter code) | — |

---

## 9. Category Translation (`product_category_name_translation.csv`)

| Column Name | Data Type | Description | Notes |
|---|---|---|---|
| product_category_name | string | Category name in Portuguese | Join key with products table |
| product_category_name_english | string | Category name in English | Use this in all analysis and dashboard |

---

## Known Data Quality Issues

| Table | Issue | Planned Treatment |
|---|---|---|
| Orders | Null delivery timestamps for non-delivered orders | Filter or flag by order_status |
| Products | Missing category, weight, dimensions | Impute or drop depending on analysis |
| Payments | payment_installments contains invalid 0 values — requires correction | Treat as single payment |
| Customers | customer_id resets per order | Always use customer_unique_id for retention |
| Geolocation | Duplicate zip code entries | Deduplicate using mean lat/lng per zip |
| Reviews | Mostly null comment fields | Exclude from analysis unless doing NLP |
| Sellers / Customers | Inconsistent city name casing | Standardize to lowercase in cleaning step |

---

## Planned Derived Features

| Feature Name | Formula | Purpose |
|---|---|---|
| delivery_time | order_delivered_customer_date − order_purchase_timestamp | Measure actual delivery duration |
| delivery_delay | order_delivered_customer_date − order_estimated_delivery_date | Identify late deliveries |
| total_order_value | SUM(payment_value) per order_id | Compute true revenue per order |
| customer_repeat_flag | COUNT(orders) per customer_unique_id > 1 | Identify returning customers for retention analysis |