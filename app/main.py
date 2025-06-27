from fastapi import FastAPI
from app.api.endpoints import company, metrics, financials

# Initialize FastAPI application
app = FastAPI(
    title="Stock Data and Analysis API",
    description="An API to fetch and process stock data from Finnhub.",
    version="0.1.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc" # ReDoc documentation
)

# Include API routers from your endpoints
app.include_router(company.router, prefix="/api", tags=["Company"])
app.include_router(metrics.router, prefix="/api", tags=["Metrics"])
app.include_router(financials.router, prefix="/api", tags=["Financials"])

@app.get("/")
async def read_root():
    """
    Root endpoint for the API.
    """
    return {"message": "Welcome to the Finnhub Stock Data API! Visit /docs for API documentation."}
