import logging
import os
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, Query, Request
from fastapi.responses import JSONResponse
from httpx import AsyncClient
from niquests import AsyncSession

logger = logging.getLogger("uvicorn.info")


type HTTPClient = AsyncClient | AsyncSession


@asynccontextmanager
async def _lifespan(app_: FastAPI) -> AsyncGenerator[None]:
    logger.info("Starting up...")
    async with (
        AsyncClient() as httpx_client,
        AsyncSession() as niquests_session,
    ):
        app_.state.httpx_client = httpx_client
        app_.state.niquests_session = niquests_session
        logger.info("Server ready")
        yield
    logger.info("Shutting down...")


app = FastAPI(lifespan=_lifespan)


async def _get_client(
    request: Request,
    http_client: Literal["httpx", "niquests"] = Query("httpx"),
) -> AsyncGenerator[HTTPClient]:
    client_to_yield = {
        "httpx": request.app.state.httpx_client,
        "niquests": request.app.state.niquests_session,
    }[http_client]
    yield client_to_yield


HTTPClientDep = Annotated[AsyncClient, Depends(_get_client)]


@app.get("/upstream")
def upstream() -> JSONResponse:
    simulate_failure = True if os.environ["SIMULATE_FAILURE"] == "true" else False
    logger.info("Starting request, simulate failure: %s", simulate_failure)
    if simulate_failure:
        time.sleep(30.0)
        return JSONResponse({}, status_code=408)
    return JSONResponse({"message": "Hello from upstream!"})


@app.get("/main")
async def main(
    http_client: HTTPClientDep,
    *,
    log_exception: bool = Query(default=False, description="Log exception details"),
) -> JSONResponse:
    host = os.environ["UPSTREAM_HOST"]
    url = f"http://{host}:8001/upstream"
    try:
        response = await http_client.get(
            url,
            # "http://host.docker.internal:8001/upstream",
            timeout=2.5,
            headers={"Authorization": "Bearer asdasdasd"},
        )
    except Exception as e:
        if log_exception:
            logger.exception(f"Error during upstream request: {e}")
        raise
        # tb = traceback.format_exc()
        # if "httpx.PoolTimeout" in tb:
        #     logger.error("PoolTimeout occurred")
        #     return JSONResponse({"error": "PoolTimeout"}, status_code=408)
        # return JSONResponse({"error": f"Upstream request failed {e}"}, status_code=500)

    if response.status_code != 200:
        logger.error(f"Failed to get upstream: {response.status_code}")
        return JSONResponse({"error": "Upstream request failed"}, status_code=500)
    data = response.json() | {"and": "from main"}
    return JSONResponse(data)
