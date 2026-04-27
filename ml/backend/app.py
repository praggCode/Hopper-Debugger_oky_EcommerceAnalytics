from __future__ import annotations

from pathlib import Path
import sys

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import uvicorn


ML_ROOT = Path(__file__).resolve().parents[1]
ML_SRC = ML_ROOT / "src"
if str(ML_SRC) not in sys.path:
    sys.path.insert(0, str(ML_SRC))

from inference import predict_customer_segment, predict_late_delivery


app = FastAPI(title="Olist ML Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




class LateDeliveryRequest(BaseModel):
    customerState: str
    sellerState: str
    paymentType: str
    paymentInstallments: float
    totalItems: float
    totalOrderValue: float
    totalFreight: float
    productWeightG: float
    orderMonth: str
    productCategory: str | None = "bed_bath_table"


class CustomerSegmentRequest(BaseModel):
    totalOrders: float
    totalSpent: float
    avgReviewScore: float
    avgDelay: float
    lateDeliveryRate: float
    paymentInstallments: float


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/predict/late-delivery")
def late_delivery_prediction(request: LateDeliveryRequest) -> dict:
    return predict_late_delivery(request.model_dump())


@app.post("/predict/customer-segment")
def customer_segment_prediction(request: CustomerSegmentRequest) -> dict:
    return predict_customer_segment(request.model_dump())


@app.get("/")
def read_root():
    return {"message": "Olist ML Backend is running"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
