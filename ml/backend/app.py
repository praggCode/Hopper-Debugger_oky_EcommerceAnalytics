from __future__ import annotations

from pathlib import Path
import sys

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
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

# --- Frontend Integration ---
# Calculate path to frontend/dist relative to this file
FRONTEND_DIST = Path(__file__).resolve().parents[1] / "frontend" / "dist"


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


# Mount frontend static files
# We check if the directory exists first to avoid errors during development if not built yet
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")
else:
    @app.get("/")
    def read_root():
        return {"message": "Frontend not built. Run 'npm run build' in ml/frontend."}


@app.exception_handler(404)
async def catch_all_handler(request, exc):
    # If the request is for an API route, return 404 as usual
    if request.url.path.startswith("/predict") or request.url.path.startswith("/health"):
        return JSONResponse(status_code=404, content={"detail": "Not Found"})
    
    # Otherwise, serve index.html for SPA support
    if FRONTEND_DIST.exists():
        return FileResponse(FRONTEND_DIST / "index.html")
    return JSONResponse(status_code=404, content={"detail": "Not Found"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
