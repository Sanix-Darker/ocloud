# coding: utf-8
import os
import json
from fastapi import APIRouter, FastAPI, UploadFile, Form, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import logging

from ocloud.utils import (
    JSON_MAPS_FOLDER,
    get_file,
    proceed_chunk,
    proceed_file,
)

_LOGGER = logging.getLogger(__name__)
_API_VERSION = "/api/v1"

app = FastAPI()
api_rooter = APIRouter(prefix=_API_VERSION)

# Point Jinja2Templates to the directory containing your HTML templates
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


def build_response(data, status="success", **kwargs):
    response_data = {"status": status, **data, **kwargs}
    return JSONResponse(content=response_data)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


@api_rooter.get("/")
async def api():
    return {
        "author": "sanix-darker (github.com/sanix-darker)",
        "documentation": "https://documenter.getpostman.com/view/2696027/SzYgRaw1?version=latest",
        "message": "Welcome to Ocloud API.",
    }


@api_rooter.get("/count")
async def count_files():
    # TODO: a  method to return this value
    count = len(os.listdir(JSON_MAPS_FOLDER))
    return build_response({"count": count})


@api_rooter.get("/checkfile/{file_key}")
async def check_file(file_key: str):
    # FIXME: should not be odne here.
    json_file = f"m_{file_key}.json"
    file_path = os.path.join(JSON_MAPS_FOLDER, json_file)

    if os.path.exists(file_path):
        with open(file_path) as f:
            file_data = json.load(f)
        response_data = {
            "file_name": file_data["file"]["file_name"],
            "chunks": len(file_data["cloud_map"]),
        }
        return build_response(response_data)
    else:
        return build_response({"message": "File not found."}, status="error")


@api_rooter.get("/file/{file_key}")
async def get_file_from_key(file_key: str):
    json_map_file = f"./json_maps/m_{file_key}.json"

    if not os.path.exists(json_map_file):
        return build_response(
            {"file_key": file_key, "message": "File not found."}, status="error"
        )
    else:
        file_path = get_file(json_map_file)
        if os.path.exists(file_path):
            return FileResponse(
                file_path.replace("./ocloud/server/", ""),
                media_type="application/octet-stream",
            )
        else:
            raise HTTPException(status_code=404, detail="File not found.")


@api_rooter.post("/uploadchunk")
async def upload_chunk(chunk: UploadFile = Form(...), chat_id: str = Form(...)):
    try:
        response = proceed_chunk(chunk.file, chat_id)
    except Exception:
        return {
            "status": "error",
            "message": "An error occurred on the server. Please check your requirements.",
        }

    return response


@api_rooter.post("/upload")
async def upload(chat_id: int = Form(...), file_: UploadFile = Form(...)):
    try:
        _LOGGER.info("INPUT /api/upload")
        _LOGGER.info(file_)
        _LOGGER.info(chat_id)
        response = proceed_file(file_.file, int(chat_id))
    except Exception:
        return {
            "status": "error",
            "message": "Request Entity Too Large: The data value transmitted exceeds the capacity limit.",
        }
    return response

app.include_router(api_rooter)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9432, log_level=3)
