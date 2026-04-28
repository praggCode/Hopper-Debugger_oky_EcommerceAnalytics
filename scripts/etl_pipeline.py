import pandas as pd
import numpy as np
import os

RAW_PATH       = "../data/raw/"
PROCESSED_PATH = "../data/processed/"

os.makedirs(PROCESSED_PATH, exist_ok=True)

print("[STEP 1] Loading raw datasets...")

orders               = pd.read_csv(RAW_PATH + "olist_orders_dataset.csv")
order_items          = pd.read_csv(RAW_PATH + "olist_order_items_dataset.csv")
customers            = pd.read_csv(RAW_PATH + "olist_customers_dataset.csv")
payments             = pd.read_csv(RAW_PATH + "olist_order_payments_dataset.csv")
reviews              = pd.read_csv(RAW_PATH + "olist_order_reviews_dataset.csv")
products             = pd.read_csv(RAW_PATH + "olist_products_dataset.csv")
sellers              = pd.read_csv(RAW_PATH + "olist_sellers_dataset.csv")
geolocation          = pd.read_csv(RAW_PATH + "olist_geolocation_dataset.csv")
category_translation = pd.read_csv(RAW_PATH + "product_category_name_translation.csv")

print(f"  ✓ All 9 tables loaded successfully")

print("[STEP 2] Converting datetime columns...")

datetime_cols = [
    'order_purchase_timestamp',
    'order_approved_at',
    'order_delivered_carrier_date',
    'order_delivered_customer_date',
    'order_estimated_delivery_date'
]
for col in datetime_cols:
    orders[col] = pd.to_datetime(orders[col])

print(f"  ✓ 5 datetime columns converted")

print("[STEP 3] Filtering delivered orders...")

before = len(orders)
orders_clean = orders[orders['order_status'] == 'delivered'].copy()
after = len(orders_clean)

print(f"  ✓ Delivered orders: {after:,} / {before:,} (dropped {before - after:,})")

print("[STEP 4] Cleaning payments...")

invalid = payments[payments['payment_installments'] == 0].shape[0]
payments['payment_installments'] = payments['payment_installments'].replace(0, 1)
print(f"  ✓ Fixed {invalid} invalid installment values")

not_def = payments[payments['payment_type'] == 'not_defined'].shape[0]
payments = payments[payments['payment_type'] != 'not_defined']
print(f"  ✓ Dropped {not_def} not_defined payment rows")

payments_agg = payments.groupby('order_id').agg(
    total_payment_value  = ('payment_value', 'sum'),
    payment_installments = ('payment_installments', 'max'),
    payment_type         = ('payment_type', lambda x: x.mode()[0])
).reset_index()

print(f"  ✓ Payments aggregated to {len(payments_agg):,} unique orders")

print("[STEP 5] Cleaning products...")

products = products.rename(columns={
    'product_name_lenght'       : 'product_name_length',
    'product_description_lenght': 'product_description_length'
})

products = products.merge(category_translation, on='product_category_name', how='left')
products['product_category_name_english'] = (
    products['product_category_name_english'].fillna('unknown')
)

for col in ['product_weight_g', 'product_length_cm',
            'product_height_cm', 'product_width_cm']:
    missing = products[col].isnull().sum()
    products[col] = products[col].fillna(products[col].median())
    if missing > 0:
        print(f"  ✓ {col}: filled {missing} nulls with median")

print(f"  ✓ Products cleaned — shape: {products.shape}")

print("[STEP 6] Standardizing city names...")

customers['customer_city'] = customers['customer_city'].str.lower().str.strip()
sellers['seller_city']     = sellers['seller_city'].str.lower().str.strip()

print(f"  ✓ City names standardized to lowercase")

print("[STEP 7] Deduplicating geolocation...")

before_geo = len(geolocation)
geo_clean = geolocation.groupby('geolocation_zip_code_prefix').agg(
    geolocation_lat   = ('geolocation_lat', 'mean'),
    geolocation_lng   = ('geolocation_lng', 'mean'),
    geolocation_city  = ('geolocation_city', 'first'),
    geolocation_state = ('geolocation_state', 'first')
).reset_index()

print(f"  ✓ Reduced {before_geo:,} → {len(geo_clean):,} unique zip codes")

print("[STEP 8] Cleaning reviews...")

reviews_clean = reviews[['order_id', 'review_score']].copy()
dupes = reviews_clean.duplicated(subset='order_id').sum()
reviews_clean = reviews_clean.drop_duplicates(subset='order_id', keep='first')

print(f"  ✓ Kept review_score only — removed {dupes} duplicate reviews")

print("[STEP 9] Aggregating order items...")

order_items_agg = order_items.groupby('order_id').agg(
    total_items   = ('order_item_id', 'count'),
    total_price   = ('price', 'sum'),
    total_freight = ('freight_value', 'sum'),
    seller_id     = ('seller_id', 'first'),
    product_id    = ('product_id', 'first')
).reset_index()

print(f"  ✓ Order items aggregated — {len(order_items_agg):,} unique orders")

print("[STEP 10] Merging all tables into master dataset...")

master = orders_clean.merge(customers,       on='customer_id',  how='left')
master = master.merge(order_items_agg,       on='order_id',     how='left')
master = master.merge(payments_agg,          on='order_id',     how='left')
master = master.merge(reviews_clean,         on='order_id',     how='left')
master = master.merge(
    products[['product_id', 'product_category_name_english', 'product_weight_g']],
    on='product_id', how='left'
)
master = master.merge(
    sellers[['seller_id', 'seller_city', 'seller_state']],
    on='seller_id', how='left'
)

assert len(master) == len(orders_clean), \
    f"Row mismatch! Expected {len(orders_clean):,}, got {len(master):,}"
print(f"  ✓ Join validation passed — {len(master):,} rows confirmed")
print(f"  ✓ Final columns: {master.shape[1]}")

print("[STEP 11] Engineering derived features...")

master['delivery_time_days'] = (
    master['order_delivered_customer_date'] - master['order_purchase_timestamp']
).dt.days

master['delivery_delay_days'] = (
    master['order_delivered_customer_date'] - master['order_estimated_delivery_date']
).dt.days

master['is_late_delivery'] = master['delivery_delay_days'] > 0

master['total_order_value'] = master['total_price'] + master['total_freight']

order_counts = master.groupby('customer_unique_id')['order_id'].count()
master['customer_repeat_flag'] = master['customer_unique_id'].map(order_counts > 1)

master['order_month'] = master['order_purchase_timestamp'].dt.to_period('M').astype(str)
master['order_year']  = master['order_purchase_timestamp'].dt.year

print(f"  ✓ 7 derived features created")

print("[STEP 12] Treating remaining nulls...")

median_score = master['review_score'].median()
review_nulls = master['review_score'].isnull().sum()
master['review_score'] = master['review_score'].fillna(median_score)
print(f"  ✓ review_score: filled {review_nulls} nulls with median ({median_score})")

before_drop = len(master)
master = master.dropna(subset=['order_delivered_customer_date', 'total_payment_value'])
print(f"  ✓ Dropped {before_drop - len(master)} rows with critical missing data")

critical_cols = [
    'order_delivered_customer_date',
    'total_payment_value',
    'review_score',
    'delivery_time_days',
    'total_order_value',
    'customer_repeat_flag'
]
remaining_nulls = master[critical_cols].isnull().sum().sum()
print(f"  Critical column nulls: {remaining_nulls}")
assert remaining_nulls == 0, "Null values in critical KPI columns!"
print(f"  ✓ Critical null validation passed")
print(f"  ✓ Null validation passed — dataset is clean")

print("[STEP 13] Exporting final dataset...")

output_path = PROCESSED_PATH + "olist_master_cleaned.csv"
master.to_csv(output_path, index=False)

print(f"\n{'='*50}")
print(f"✓ ETL PIPELINE COMPLETE")
print(f"{'='*50}")
print(f"  Output : {output_path}")
print(f"  Shape  : {master.shape}")
print(f"  Rows   : {master.shape[0]:,}")
print(f"  Columns: {master.shape[1]}")
print(f"\n  Columns list:")
for col in master.columns:
    print(f"    - {col}")