# app/main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, ORJSONResponse

from app.api.router import api
from app.errors import DomainError, InfraError
from app.middleware.request_id import RequestIDMiddleware

app = FastAPI(title="rt-pipeline", default_response_class=ORJSONResponse)
app.add_middleware(RequestIDMiddleware)
app.include_router(api)

@app.exception_handler(DomainError)
async def domain_error_handler(_: Request, e: DomainError):
    return JSONResponse({"error": "domain_error", "detail": str(e)}, status_code=400)

@app.exception_handler(InfraError)
async def infra_error_handler(_: Request, e: InfraError):
    return JSONResponse({"error": "infra_error", "detail": str(e)}, status_code=502)