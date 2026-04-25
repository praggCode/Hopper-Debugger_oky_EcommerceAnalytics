# ML Extension

This folder contains the machine learning layer added on top of the Olist e-commerce analytics project.

Two ML workflows are implemented:

- `late_delivery_prediction`
- `customer_segmentation`

## Structure

```text
ml/
├── README.md
└── src/
    ├── customer_segmentation.py
    ├── late_delivery_prediction.py
    ├── ml_utils.py
    └── run_ml_pipeline.py
```

## How to Run

Create and activate a virtual environment first:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python3 -m pip install -r ml/requirements.txt
```

Then run from the project root:

```bash
python3 ml/src/run_ml_pipeline.py
```

Or from inside `ml/src/`:

```bash
python3 run_ml_pipeline.py
```

When you are done, deactivate the environment:

```bash
deactivate
```

## 1. Late Delivery Prediction

This workflow predicts whether an order is likely to be delivered late.

Features used include:

- customer state
- seller state
- payment type
- payment installments
- total items
- total order value
- freight value
- product weight
- order month
- order year

Model summary:

- Dataset used: `96,469` orders
- Training rows: `77,255`
- Test rows: `19,214`
- Accuracy: `79.36%`
- Precision: `16.63%`
- Recall: `51.94%`
- F1-score: `25.20%`

Main insight:

- delivery risk changes across time periods, regions, and logistics-related variables such as product weight and seller location

Business use:

- identify risky shipments early
- prioritize operations follow-up for high-risk orders
- reduce customer dissatisfaction caused by late deliveries

## 2. Customer Segmentation

This workflow groups customers into practical business segments using clustering.

Clustering features include:

- total orders
- total spent
- average review score
- average delay
- late delivery rate
- payment installments

The segmentation produces 4 practical customer groups:

1. `High Value Loyalists`
2. `Stable Everyday Buyers`
3. `At-Risk Delay Hit Customers`
4. `Low Value Occasional Buyers`

Main insight:

- the at-risk delay-hit group stands out with poor logistics experience and low review scores, while high-value loyalists need premium retention and service protection

Business use:

- retention campaigns
- premium customer targeting
- service differentiation by value and delivery experience