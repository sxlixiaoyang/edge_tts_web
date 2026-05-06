from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import edge_tts
import hashlib
import datetime
import os
import tempfile
import asyncio

app = FastAPI()

# 创建模板目录路径
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)

# 创建mp3目录
output_dir = os.path.join(os.path.dirname(__file__), "mp3")
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 挂载静态文件目录
app.mount("/mp3", StaticFiles(directory=output_dir), name="mp3")

# 语言名称映射
LANGUAGE_NAMES = {
    "af": "南非荷兰语",
    "am": "阿姆哈拉语",
    "ar": "阿拉伯语",
    "az": "阿塞拜疆语",
    "bg": "保加利亚语",
    "bn": "孟加拉语",
    "bs": "波斯尼亚语",
    "ca": "加泰罗尼亚语",
    "cs": "捷克语",
    "cy": "威尔士语",
    "da": "丹麦语",
    "de": "德语",
    "el": "希腊语",
    "en": "英语",
    "es": "西班牙语",
    "et": "爱沙尼亚语",
    "fa": "波斯语",
    "fi": "芬兰语",
    "fil": "菲律宾语",
    "fr": "法语",
    "ga": "爱尔兰语",
    "gl": "加利西亚语",
    "gu": "古吉拉特语",
    "he": "希伯来语",
    "hi": "印地语",
    "hr": "克罗地亚语",
    "hu": "匈牙利语",
    "hy": "亚美尼亚语",
    "id": "印尼语",
    "is": "冰岛语",
    "it": "意大利语",
    "iu": "因纽特语",
    "ja": "日语",
    "jv": "爪哇语",
    "ka": "格鲁吉亚语",
    "kk": "哈萨克语",
    "km": "高棉语",
    "kn": "卡纳达语",
    "ko": "韩语",
    "lo": "老挝语",
    "lt": "立陶宛语",
    "lv": "拉脱维亚语",
    "mk": "马其顿语",
    "ml": "马拉雅拉姆语",
    "mn": "蒙古语",
    "mr": "马拉地语",
    "ms": "马来语",
    "mt": "马耳他语",
    "my": "缅甸语",
    "nb": "挪威语",
    "ne": "尼泊尔语",
    "nl": "荷兰语",
    "pl": "波兰语",
    "ps": "普什图语",
    "pt": "葡萄牙语",
    "ro": "罗马尼亚语",
    "ru": "俄语",
    "si": "僧伽罗语",
    "sk": "斯洛伐克语",
    "sl": "斯洛文尼亚语",
    "so": "索马里语",
    "sq": "阿尔巴尼亚语",
    "sr": "塞尔维亚语",
    "su": "巽他语",
    "sv": "瑞典语",
    "sw": "斯瓦希里语",
    "ta": "泰米尔语",
    "te": "泰卢固语",
    "th": "泰语",
    "tr": "土耳其语",
    "uk": "乌克兰语",
    "ur": "乌尔都语",
    "uz": "乌兹别克语",
    "vi": "越南语",
    "zh": "中文",
    "zu": "祖鲁语"
}


async def get_voices():
    """获取所有语音列表"""
    voices = await edge_tts.list_voices()
    result = {}
    for v in voices:
        locale = v['Locale']
        lang_code = locale.split('-')[0]
        lang_name = LANGUAGE_NAMES.get(lang_code, lang_code)
        
        if lang_name not in result:
            result[lang_name] = {}
        
        # 构建地区显示名称
        region = locale.split('-')[-1] if '-' in locale else locale
        region_display = f"{locale}"
        
        if region_display not in result[lang_name]:
            result[lang_name][region_display] = []
        
        result[lang_name][region_display].append({
            'name': v['ShortName'],
            'gender': '男' if v['Gender'] == 'Male' else '女',
            'display_name': v['ShortName'].split('-')[-1].replace('Neural', '')
        })
    
    return result


async def my_function(text, output, voice, rate):
    volume = '+0%'
    try:
        tts = edge_tts.Communicate(text=text, voice=voice, rate=rate, volume=volume)
        await tts.save(output)
        return True
    except Exception as e:
        print(f"TTS Error: {e}")
        return False


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    template = templates.get_template("index.html")
    html_content = template.render(request=request)
    return HTMLResponse(content=html_content)


@app.get("/api", response_class=HTMLResponse)
async def api_docs(request: Request):
    """API文档页面"""
    template = templates.get_template("api.html")
    html_content = template.render(request=request)
    return HTMLResponse(content=html_content)


@app.get("/api/voices")
async def get_voices_api():
    """API: 获取所有支持的语音列表"""
    try:
        voices = await get_voices()
        return JSONResponse(content={"message": "success", "voices": voices})
    except Exception as e:
        return JSONResponse(
            content={"message": "error", "error": str(e)},
            status_code=500
        )


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
