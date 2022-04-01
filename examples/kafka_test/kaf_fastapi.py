from typing import Optional
import rpcgrid
from rpcgrid.providers.kafka import KafkaProvider
from rpcgrid.server import AsyncServer
from fastapi import FastAPI
import uvicorn
import logging
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles

logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
rpc: AsyncServer = None


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )


@rpcgrid.register
@app.get("/")
def read_root():
    return {"Hello": "World"}


@rpcgrid.register
@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


@app.on_event("startup")
async def startup_event():
    global rpc
    server_provider = KafkaProvider('task_topic', bootstrap_servers='localhost:9091')
    rpc = await rpcgrid.server(server_provider)


@app.on_event("shutdown")
async def startup_event():
    if rpc is not None:
        await rpc.close()


if __name__ == "__main__":
    uvicorn.run("kaf_fastapi:app", host="127.0.0.1", port=5000, log_level="info")
