from fastapi import FastAPI, Request, Form, File
from fastapi.responses import JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
import edge_tts
import asyncio
import hashlib
import datetime
import os
import tempfile
import pygame.mixer

pygame.mixer.init()


async def my_function(text, output, voice, rate):
    volume = '+0%'
    tts = edge_tts.Communicate(text=text, voice=voice, rate=rate, volume=volume)
    await tts.save(output)


app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})



@app.post("/synthesize")
async def synthesize(request: Request):
    data = await request.json()
    text = data.get("text")
    voice = data.get("voice")
    rate = data.get("rate")
    output_dir = os.path.join(os.path.dirname(__file__), "mp3")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 构造文件名
    now = datetime.datetime.now()

    filename_base = hashlib.md5((text[:5] + str(now.timestamp())).encode()).hexdigest()
    filename = os.path.join(output_dir, filename_base + ".mp3")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3", dir=output_dir) as temp_file:
        temp_filename = temp_file.name
    await my_function(text, temp_filename, voice, rate)


    # 将临时文件转存为指定的输出文件
    os.rename(temp_filename, filename)

    # 返回包含下载链接的响应
    return JSONResponse(content={"message": "success", "download_link": f"/download?filename={filename}"})


@app.get("/download")
async def download(filename: str):
    file_path = os.path.join(app.root_path, filename)
    return FileResponse(path=file_path, filename=filename, media_type="application/octet-stream")
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)