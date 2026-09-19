import os

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.config import settings
from src.api.routes import persons
from src.api.routes import network
from src.api.routes import graph
from src.api.routes import intelligence
from src.api.routes import cases
from src.api.routes import agents
from src.api.routes import evidence
from src.api.routes import graph_rag
from src.api.routes import investigation
from src.api.routes import anomalies
from src.api.routes import transactions
from src.api.routes import documents
from src.api.routes import search
from src.api.routes import auth
from src.api.routes import workspace
from src.api.routes import review_queue

app = FastAPI(
    title="CNAS API",
    description="Criminal Network Analysis System",
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": "The request payload or query parameters are invalid.",
            "details": exc.errors(),
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "http_error",
            "message": exc.detail if isinstance(exc.detail, str) else "Request failed.",
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected server error occurred. Please try again later.",
        },
    )


app.include_router(persons.router)
app.include_router(network.router)
app.include_router(graph.router)
app.include_router(intelligence.router)
app.include_router(cases.router)
app.include_router(agents.router)
app.include_router(evidence.router)
app.include_router(graph_rag.router)
app.include_router(investigation.router)
app.include_router(anomalies.router)
app.include_router(transactions.router)
app.include_router(documents.router)
app.include_router(search.router)
app.include_router(auth.router)
app.include_router(workspace.router)
app.include_router(review_queue.router)


# Some FastAPI router wrappers (used internally) may nest route lists under an
# object that does not expose a `path` attribute. For tests and tooling that
# expect `APIRoute` entries directly on `app.routes`, flatten any such
# wrappers by recursively expanding `routes` attributes. This avoids relying
# on private FastAPI internals while making the final route list discoverable.
def _flatten(routes):
    out = []
    for r in routes:
        # FastAPI may wrap an APIRouter in an internal `_IncludedRouter` which
        # exposes the original router under `original_router`. Prefer that
        # when present so we can expand the underlying `routes` list.
        if hasattr(r, "original_router"):
            try:
                out.extend(_flatten(r.original_router.routes))
                continue
            except Exception:
                pass

        # Fallback: if the object exposes a `routes` attribute and does not
        # represent a concrete route (no `path`), expand it recursively.
        if hasattr(r, "routes") and getattr(r, "path", None) is None:
            try:
                out.extend(_flatten(r.routes))
                continue
            except Exception:
                pass

        out.append(r)
    return out


try:
    app.router.routes = _flatten(app.router.routes)
except Exception:
    # Non-fatal: leave routes as-is if flattening fails
    pass


@app.get("/")
def root():
    return {
        "name": "CNAS",
        "status": "running",
        "version": settings.app_version,
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "cnas-api",
        "version": settings.app_version,
        "components": {
            "neo4j": bool(settings.neo4j_uri),
            "pinecone": bool(settings.pinecone_api_key),
            "google": bool(settings.google_api_key),
            "frontend": bool(settings.allowed_origins),
        },
        "environment": settings.environment,
    }


@app.get("/api/health")
def api_health():
    return health()
