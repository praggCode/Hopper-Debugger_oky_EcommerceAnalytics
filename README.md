# Olist E-Commerce Performance Analytics

> **DVA Course Project** — Data Analytics on the Brazilian Olist E-Commerce Dataset  
> Sector: E-Commerce / Retail | Period Covered: 2016–2018 | Records: ~100,000 orders

---

## Problem Statement

> *What are the key drivers of sales performance and customer retention across regions in Brazilian e-commerce, and how can the business optimize pricing, delivery efficiency, and customer targeting to maximize revenue?*

---

## Project Overview

This project performs end-to-end analytics on the real-world **Olist Brazilian E-Commerce** dataset — from raw data ingestion through statistical analysis, Tableau dashboards, and a deployed machine learning layer with a live prediction UI.

The work is structured in three layers:

1. **Analytics Layer** — ETL pipeline, EDA, and statistical analysis in Python/Jupyter
2. **Visualization Layer** — Tableau dashboard covering KPIs, sales trends, regional orders, and revenue breakdowns
3. **ML Layer** — Two from-scratch ML models (late delivery prediction + customer segmentation) served via a FastAPI backend and a React/Vite frontend

---

## Repository Structure

```
Hopper-Debugger_oky_EcommerceAnalytics/
├── data/
│   ├── raw/                            # 9 original Olist CSV files (not tracked)
│   └── processed/
│       └── olist_master_cleaned.csv    # Final merged + engineered dataset (ETL output)
│
├── notebooks/
│   ├── 01_extraction.ipynb             # Load and inspect all 9 raw tables
│   ├── 02_cleaning.ipynb               # Data cleaning and quality checks
│   ├── 03_eda.ipynb                    # Full exploratory data analysis + visualizations
│   ├── 04_statistical_analysis.ipynb   # Statistical tests and KPI derivation
│   └── 05_final_load_prep.ipynb        # Final dataset preparation for Tableau + ML
│
├── scripts/
│   └── etl_pipeline.py                 # 13-step production ETL pipeline
│
├── ml/
│   ├── src/
│   │   ├── late_delivery_prediction.py # Logistic regression model training
│   │   ├── customer_segmentation.py    # K-Means clustering
│   │   ├── inference.py                # Prediction + segmentation inference logic
│   │   ├── ml_utils.py                 # Custom implementations (sigmoid, kmeans, standardize)
│   │   └── run_ml_pipeline.py          # Entry point to train both models
│   ├── backend/
│   │   └── app.py                      # FastAPI server exposing ML endpoints
│   ├── frontend/
│   │   └── src/
│   │       ├── App.jsx                 # Main React app (4 tabs)
│   │       ├── components/             # MetricCard, SectionCard, BarViz
│   │       ├── data/mlData.js          # Static ML result data for display
│   │       ├── services/api.js         # API calls to FastAPI backend
│   │       └── styles.css              # App styling
│   └── requirements.txt
│
├── tableau/
│   ├── dashboard_links.md              # Google Drive link to .twbx file
│   └── screenshots/                   # Dashboard screenshots (7 views)
│       ├── Dashboard.png
│       ├── KPI's.png
│       ├── SalesTrendChart.png
│       ├── OrdersByStateChart.png
│       ├── OrdersByStateMap.png
│       ├── RevenueByPaymentChart.png
│       └── RevenueByProductCategoryChart.png
│
├── docs/
│   ├── data_dictionary.md              # Full schema for all 9 tables + data quality notes
│   └── gate1_submission.md             # Gate 1 submission document
│
├── reports/
│   ├── DVA_Report.pdf                  # Full project report
│   └── DVA_Ppt.pdf                     # Project presentation slides
│
└── README.md
```

---

## Dataset

**Source:** [Kaggle — Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

The dataset consists of **9 relational CSV tables** covering the complete order lifecycle:

| Table | Description |
|---|---|
| `olist_orders_dataset.csv` | Order status, timestamps, delivery dates |
| `olist_order_items_dataset.csv` | Products, sellers, prices, freight per order |
| `olist_customers_dataset.csv` | Customer location and unique identity |
| `olist_order_payments_dataset.csv` | Payment type, installments, amounts |
| `olist_order_reviews_dataset.csv` | Review scores and timestamps |
| `olist_products_dataset.csv` | Product dimensions, weight, category |
| `olist_sellers_dataset.csv` | Seller location |
| `olist_geolocation_dataset.csv` | Zip code lat/lng coordinates |
| `product_category_name_translation.csv` | Portuguese → English category names |

Full schema and known data quality issues are documented in [`docs/data_dictionary.md`](docs/data_dictionary.md).

---

## ETL Pipeline

**Script:** `scripts/etl_pipeline.py`

A 13-step pipeline that transforms all 9 raw tables into a single analysis-ready master dataset:

| Step | Action |
|---|---|
| 1 | Load all 9 raw CSVs |
| 2 | Convert 5 datetime columns |
| 3 | Filter to delivered orders only |
| 4 | Fix invalid payment installment values (0 → 1), drop `not_defined` payments |
| 5 | Rename typo columns, join English category names, impute missing product dimensions with median |
| 6 | Standardize city names to lowercase |
| 7 | Deduplicate geolocation (mean lat/lng per zip) |
| 8 | Keep only `review_score` column, deduplicate per order |
| 9 | Aggregate order items → total_items, total_price, total_freight per order |
| 10 | Merge all tables into one master DataFrame with a row-count validation assert |
| 11 | Engineer 7 derived features (see below) |
| 12 | Fill remaining nulls, drop rows with critical missing fields, assert zero critical nulls |
| 13 | Export to `data/processed/olist_master_cleaned.csv` |

**Derived Features Engineered:**

| Feature | Formula |
|---|---|
| `delivery_time_days` | `order_delivered_customer_date − order_purchase_timestamp` |
| `delivery_delay_days` | `order_delivered_customer_date − order_estimated_delivery_date` |
| `is_late_delivery` | `delivery_delay_days > 0` |
| `total_order_value` | `total_price + total_freight` |
| `customer_repeat_flag` | `True` if `customer_unique_id` has more than 1 order |
| `order_month` | Month period string from purchase timestamp |
| `order_year` | Year integer from purchase timestamp |

---

## Jupyter Notebooks

| Notebook | Purpose |
|---|---|
| `01_extraction.ipynb` | Load and inspect all 9 raw tables, check shapes and nulls |
| `02_cleaning.ipynb` | Data cleaning, null treatment, type correction |
| `03_eda.ipynb` | Full EDA — distributions, time trends, regional breakdowns, payment patterns, delivery analysis |
| `04_statistical_analysis.ipynb` | KPI derivation, statistical tests, correlation analysis |
| `05_final_load_prep.ipynb` | Prepare final dataset for Tableau export and ML input |

---

## Tableau Dashboard

**Download the .twbx file:** [Google Drive Link](https://drive.google.com/drive/folders/1Cs8mYVkxS_saj8eMwJsHd703f6lK-St0?usp=drive_link)

The Tableau workbook contains 7 views:

| View | Description |
|---|---|
| **Dashboard** | Main overview combining all KPIs and charts |
| **KPIs** | High-level KPI summary cards |
| **Sales Trend Chart** | Monthly revenue trend over 2016–2018 |
| **Orders by State (Chart)** | Bar chart of order volume by Brazilian state |
| **Orders by State (Map)** | Geographic map of order density |
| **Revenue by Payment Type** | Revenue split across credit card, boleto, voucher, debit |
| **Revenue by Product Category** | Top-performing product categories by revenue |

Screenshots are available in `tableau/screenshots/`.

---

## Machine Learning Layer

Both ML models are implemented **from scratch** using only NumPy and Pandas — no scikit-learn or external ML libraries.

### Model 1 — Late Delivery Prediction

**Type:** Logistic Regression (custom implementation with class weighting and threshold tuning)

**Goal:** Predict whether an order will be delivered late, enabling early operational intervention.

**Features used:**
- Customer state, seller state
- Payment type, payment installments
- Total items, total order value, freight value
- Product weight, order month and year
- Product category

**Results:**

| Metric | Value |
|---|---|
| Training rows | 77,255 |
| Test rows | 19,214 |
| Accuracy | **79.36%** |
| Precision | 16.63% |
| Recall | **51.94%** |
| F1-Score | 25.20% |

The model is optimized for recall — catching late deliveries is more valuable than avoiding false positives. Threshold is tuned via F1-score sweep across [0.15, 0.60].

**Output per prediction:**
- Risk label: `High Risk`, `Medium Risk`, or `Low Risk`
- Probability score (0–1)
- Top 5 feature drivers with contribution weights

---

### Model 2 — Customer Segmentation

**Type:** K-Means Clustering (custom implementation with standardization)

**Goal:** Group customers into actionable segments for targeted retention and marketing.

**Features used:**
- Total orders, total spent
- Average review score
- Average delivery delay, late delivery rate
- Payment installments

**4 Customer Segments:**

| Segment | Description | Recommended Action |
|---|---|---|
| **High Value Loyalists** | High spend, high satisfaction, low delay | Protect with premium support and faster service |
| **Stable Everyday Buyers** | Moderate spend, consistent behavior | Target with repeat purchase and cross-sell offers |
| **At-Risk Delay Hit Customers** | Low satisfaction, high delay exposure | Service recovery and delay prevention programs |
| **Low Value Occasional Buyers** | Low spend, infrequent orders | Lightweight onboarding and simple offers |

---

### FastAPI Backend

**File:** `ml/backend/app.py`

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Health check |
| `/predict/late-delivery` | POST | Returns risk label, probability, and top drivers |
| `/predict/customer-segment` | POST | Returns segment name, action, and profile stats |

---

### React/Vite Frontend

**Directory:** `ml/frontend/`

A 4-tab dashboard that connects to the FastAPI backend for live predictions:

| Tab | Description |
|---|---|
| **Overview** | Summary metrics, state-level risk bar chart, all customer segments |
| **Delivery Check** | Input form for order details → live late delivery prediction with risk label and driver chart |
| **Customer Groups** | Input form for customer profile → live segment assignment with group stats |
| **Model Summary** | Delivery model performance metrics and top feature importances |

Quick-fill presets are provided for both tools (Low Risk / High Risk examples and High Value / At-Risk customer examples).

---

## How to Run

### 1. ETL Pipeline

```bash
cd scripts
python etl_pipeline.py
```

Output: `data/processed/olist_master_cleaned.csv`

---

### 2. ML Models (Training)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r ml/requirements.txt
python3 ml/src/run_ml_pipeline.py
```

---

### 3. FastAPI Backend

```bash
source .venv/bin/activate
cd ml/backend
uvicorn app:app --reload --port 8000
```

API available at: `http://localhost:8000`

---

### 4. React Frontend

```bash
cd ml/frontend
npm install
npm run dev
```

Frontend available at: `http://localhost:5173`

> **Note:** Start the backend before using the frontend to get live predictions.

---

## Key Findings

- **São Paulo (SP)** accounts for the largest share of both orders and revenue across all Brazilian states.
- **Credit card** is the dominant payment method by revenue; installments correlate with higher order values.
- **Late deliveries** are significantly higher for orders shipped from northern and northeastern states to distant customer locations — product weight and seller-customer distance are strong predictors.
- **~97% of customers are one-time buyers** — customer repeat rate is extremely low, making retention strategy critical.
- **At-Risk Delay Hit Customers** cluster shows the lowest review scores and highest delivery delay exposure, directly linking logistics failures to customer dissatisfaction.
- Peak order volume occurred in **late 2017 through mid-2018**, with November showing Black Friday spikes.

---

## Tools & Technologies

| Area | Tools |
|---|---|
| Data Processing | Python, Pandas, NumPy |
| Analysis & EDA | Jupyter Notebook, Matplotlib, Seaborn |
| ETL | Custom Python pipeline (`scripts/etl_pipeline.py`) |
| Visualization | Tableau Public |
| ML Models | Custom Logistic Regression + K-Means (NumPy/Pandas only) |
| ML Backend | FastAPI, Uvicorn, Pydantic |
| ML Frontend | React, Vite |
| Version Control | GitHub |

---

## Reports

| File | Description |
|---|---|
| [`reports/DVA_Report.pdf`](reports/DVA_Report.pdf) | Full written project report |
| [`reports/DVA_Ppt.pdf`](reports/DVA_Ppt.pdf) | Project presentation slides |
| [`docs/data_dictionary.md`](docs/data_dictionary.md) | Schema and data quality documentation for all 9 tables |

---

## Dataset Source

Olist Brazilian E-Commerce Public Dataset  
[https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
