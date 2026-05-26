from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.api.v1.auth import router as auth_router
from app.api.v1.upload import router as upload_router
from app.core.config import settings
from app.middleware.cors import add_cors

app = FastAPI(
    title="GST Reconciliation System API",
    description="Enterprise GST reconciliation platform — compares invoices against GSTR2B data.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

add_cors(app)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(upload_router, prefix="/api/v1")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "env": settings.APP_ENV, "mock_services": settings.USE_MOCK_SERVICES}
