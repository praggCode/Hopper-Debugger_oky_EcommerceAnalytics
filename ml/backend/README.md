# Olist ML Backend

FastAPI service that provides machine learning predictions for late delivery and customer segmentation.

## Prerequisites

- Python 3.9+
- A virtual environment (recommended)

## Setup

1. **Navigate to the backend directory:**
   ```bash
   cd ml/backend
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Server

Start the FastAPI server using `uvicorn`:

```bash
uvicorn app:app --reload --port 8000
```
OR 
# 3. Run using the direct python command (more stable than the uvicorn CLI)
python app.py

The API will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Endpoints

- `GET /health`: Health check
- `POST /predict/late-delivery`: Predicts the risk of late delivery based on order details.
- `POST /predict/customer-segment`: Predicts the customer segment based on behavior metrics.
