# Olist E-Commerce Performance Analysis

## Problem Statement

What are the key drivers of sales performance and customer retention across regions in Brazilian e-commerce, and how can the business optimize pricing, delivery efficiency, and customer targeting to maximize revenue?

## Project Overview

This project analyzes a real-world e-commerce dataset to understand customer behavior, delivery performance, and sales trends. The objective is to generate actionable insights that support business decision-making.

The analysis is conducted using Python for data processing and statistical analysis, and Tableau for visualization.

## Dataset

Source: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

The dataset consists of multiple relational tables including orders, customers, payments, products, sellers, and reviews.

Key characteristics:

- Over 100,000 records
- Contains missing values and inconsistencies
- Requires data cleaning and table joins
- Covers full order lifecycle

## Repository Structure

```
Hopper-Debugger_oky_EcommerceAnalytics/
├── README.md
├── data/
│   ├── raw/                            # Original datasets
│   │   ├── olist_customers_dataset.csv
│   │   ├── olist_geolocation_dataset.csv
│   │   ├── olist_order_items_dataset.csv
│   │   ├── olist_order_payments_dataset.csv
│   │   ├── olist_order_reviews_dataset.csv
│   │   ├── olist_orders_dataset.csv
│   │   ├── olist_products_dataset.csv
│   │   ├── olist_sellers_dataset.csv
│   │   └── product_category_name_translation.csv
│   └── processed/                      # Cleaned and transformed data
├── docs/
│   ├── data_dictionary.md              # Data schema documentation
│   └── gate1_submission.md             # Submission documentation
├── notebooks/                          # Jupyter notebooks for analysis
├── reports/                            # Generated reports and findings
├── scripts/
│   └── etl_pipeline.py                 # Data processing and ETL scripts
└── tableau/
    ├── dashboard_links.md              # Links to Tableau dashboards
    └── screenshots/                    # Dashboard screenshots
```

## Approach

- Data cleaning and transformation in Python
- Exploratory data analysis (EDA)
- Statistical analysis and KPI development
- Tableau dashboard for visualization
- Business insights and recommendations

## Tools Used

- Python (Pandas, NumPy, Matplotlib, Seaborn)
- Jupyter Notebook
- Tableau Public
- GitHub

## Status

- Dataset selection completed
- Data dictionary prepared
- Gate 1 submission in progress

## Team

| Name     | Role                         |
| -------- | ---------------------------- |
| Member 1 | ETL & Data Cleaning          |
| Member 2 | EDA & Statistical Analysis   |
| Member 3 | Tableau Dashboard            |
| Member 4 | KPI Design & Report Writing  |
| Member 5 | Presentation & Documentation |
