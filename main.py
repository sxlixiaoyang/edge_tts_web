from fastapi import FastAPI, Request, Form, File
from fastapi.responses import JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import edge_tts
import asyncio
import hashlib
import datetime
import os
import tempfile

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# 创建mp3目录
output_dir = os.path.join(os.path.dirname(__file__), "mp3")
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 挂载静态文件目录
app.mount("/mp3", StaticFiles(directory=output_dir), name="mp3")


async def my_function(text, output, voice, rate):
    volume = '+0%'
    try:
        tts = edge_tts.Communicate(text=text, voice=voice, rate=rate, volume=volume)
        await tts.save(output)
        return True
    except Exception as e:
        print(f"TTS Error: {e}")
        return False


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/synthesize")
async def synthesize(request: Request):
    try:
        data = await request.json()
        text = data.get("text", "").strip()
        voice = data.get("voice", "zh-CN-XiaoxiaoNeural")
        rate = data.get("rate", "+0%")
        
        if not text:
            return JSONResponse(
                content={"message": "error", "error": "文本不能为空"},
                status_code=400
            )

        # 构造文件名
        now = datetime.datetime.now()
        filename_base = hashlib.md5((text[:5] + str(now.timestamp())).encode()).hexdigest()
        filename = filename_base + ".mp3"
        filepath = os.path.join(output_dir, filename)

        # 使用临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3", dir=output_dir) as temp_file:
            temp_filename = temp_file.name
        
        # 生成语音
        success = await my_function(text, temp_filename, voice, rate)
        
        if not success:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
            return JSONResponse(
                content={"message": "error", "error": "语音合成失败"},
                status_code=500
            )

        # 将临时文件转存为指定的输出文件
        os.rename(temp_filename, filepath)

        # 返回包含下载链接的响应
        return JSONResponse(content={
            "message": "success",
            "download_link": f"/mp3/{filename}"
        })
    
    except Exception as e:
        print(f"Synthesize Error: {e}")
        return JSONResponse(
            content={"message": "error", "error": str(e)},
            status_code=500
        )


@app.get("/download")
async def download(filename: str):
    try:
        # 安全检查：防止目录遍历攻击
        filename = os.path.basename(filename)
        file_path = os.path.join(output_dir, filename)
        
        # 确保文件在允许的目录内
        real_file_path = os.path.realpath(file_path)
        real_output_dir = os.path.realpath(output_dir)
        
        if not real_file_path.startswith(real_output_dir):
            return JSONResponse(
                content={"message": "error", "error": "非法文件路径"},
                status_code=403
            )
        
        if not os.path.exists(file_path):
            return JSONResponse(
                content={"message": "error", "error": "文件不存在"},
                status_code=404
            )
            
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="audio/mpeg"
        )
    except Exception as e:
        return JSONResponse(
            content={"message": "error", "error": str(e)},
            status_code=500
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
