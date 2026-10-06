"""Application entrypoint, middleware, static files, and route registration."""

from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.api.v1.router import api_v1_router
from src.core.config import settings
from src.core.exceptions import LinkOQRException, linkoqr_exception_handler

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-grade, memory-efficient URL to QR code generation service.",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers
app.add_exception_handler(LinkOQRException, linkoqr_exception_handler)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Normalize Pydantic validation errors for consistent API contracts."""
    errors = []
    for err in exc.errors():
        field_loc = " -> ".join([str(loc) for loc in err["loc"] if loc != "body"])
        errors.append({"field": field_loc, "message": err["msg"]})

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "success": False,
            "error_type": "ValidationError",
            "message": "Input validation failed. Please check the provided values.",
            "details": {"validation_errors": errors},
        },
    )


# Static Files and Templates Mounting
static_dir = BASE_DIR / "static"
templates_dir = BASE_DIR / "templates"

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
templates = Jinja2Templates(directory=str(templates_dir))

# Include API v1 Router
app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/", response_class=HTMLResponse, summary="Serve Web User Interface")
async def index_view(request: Request):
    """Render the primary single-page UI for generating QR codes."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
        },
    )


@app.get("/health", summary="Service Health Check")
async def health_check():
    """Verify service health and readiness."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
