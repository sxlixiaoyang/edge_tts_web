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
import logging
import traceback
import sys

# ============ 日志配置 ============
def get_app_dir():
    """获取程序所在目录（兼容 PyInstaller 打包）"""
    import sys
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后的路径
        return os.path.dirname(sys.executable)
    else:
        # 普通 Python 脚本路径
        return os.path.dirname(os.path.abspath(__file__))

def setup_logging():
    """设置日志记录"""
    # 获取程序所在目录
    app_dir = get_app_dir()
    log_dir = os.path.join(app_dir, "logs")
    
    # 创建日志目录
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 日志文件名：edge_tts_web_YYYYMMDD.log
    today = datetime.datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(log_dir, f"edge_tts_web_{today}.log")
    
    # 配置日志格式
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            # 输出到文件
            logging.FileHandler(log_file, encoding='utf-8'),
            # 输出到控制台
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__), log_file, app_dir

# 初始化日志
logger, LOG_FILE, APP_DIR = setup_logging()
logger.info("=" * 50)
logger.info("Edge TTS Web 服务初始化")
logger.info(f"日志文件: {LOG_FILE}")
logger.info(f"程序目录: {APP_DIR}")
logger.info("=" * 50)

app = FastAPI()

# 获取资源目录（兼容 PyInstaller 打包）
def get_resource_path(relative_path):
    """获取资源文件路径（兼容 PyInstaller 打包）"""
    import sys
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后，资源文件在临时目录
        base_path = sys._MEIPASS
    else:
        # 普通 Python 脚本
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# 创建模板目录路径
templates_dir = get_resource_path("templates")
logger.info(f"模板目录路径: {templates_dir}")
logger.info(f"模板目录是否存在: {os.path.exists(templates_dir)}")
if os.path.exists(templates_dir):
    logger.info(f"模板目录内容: {os.listdir(templates_dir)}")

# 使用 FileSystemLoader 替代直接传递目录路径
from jinja2 import FileSystemLoader
templates = Jinja2Templates(directory=templates_dir)

# 创建mp3目录（放在exe所在目录，而不是临时目录）
output_dir = os.path.join(APP_DIR, "mp3")
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


# 语音风格映射
VOICE_STYLES = {
    "general": "普通",
    "assistant": "助手",
    "chat": "聊天",
    "customerservice": "客服",
    "newscast": "新闻播报",
    "affectionate": "亲切",
    "angry": "愤怒",
    "cheerful": "愉快",
    "sad": "悲伤",
    "excited": "兴奋",
    "friendly": "友好",
    "terrified": "恐惧",
    "shouting": "喊叫",
    "whispering": "耳语",
    "hopeful": "充满希望",
    "empathetic": "共情",
    "lyrical": "抒情"
}

async def my_function(text, output, voice, rate, style="general"):
    volume = '+0%'
    try:
        logger.info(f"开始合成语音: voice={voice}, rate={rate}, style={style}, text_length={len(text)}")
        
        # 构建 SSML 以支持语音风格
        if style and style != "general":
            # 使用 SSML 添加语音风格
            ssml_text = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="zh-CN">
                <voice name="{voice}">
                    <mstts:express-as style="{style}">
                        {text}
                    </mstts:express-as>
                </voice>
            </speak>"""
            tts = edge_tts.Communicate(ssml_text, voice=voice, rate=rate, volume=volume)
        else:
            tts = edge_tts.Communicate(text=text, voice=voice, rate=rate, volume=volume)
        
        await tts.save(output)
        logger.info(f"语音合成成功: {output}")
        return True
    except Exception as e:
        logger.error(f"TTS合成失败: {e}")
        logger.error(traceback.format_exc())
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
        return JSONResponse(content={"message": "success", "voices": voices, "styles": VOICE_STYLES})
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
        style = data.get("style", "general")
        
        logger.info(f"收到合成请求: voice={voice}, rate={rate}, style={style}")
        
        if not text:
            logger.warning("文本为空，拒绝请求")
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
        success = await my_function(text, temp_filename, voice, rate, style)
        
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
        logger.error(f"合成请求处理失败: {e}")
        logger.error(traceback.format_exc())
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
    
    print("=" * 50)
    print("  Edge TTS Web 服务启动中...")
    print("=" * 50)
    print()
    print("  启动成功后，请在浏览器中访问：")
    print("  http://localhost:8000")
    print()
    print("  按 Ctrl+C 停止服务")
    print()
    print(f"  日志文件: {LOG_FILE}")
    print("=" * 50)
    print()
    
    logger.info("服务启动中...")
    logger.info(f"Python版本: {sys.version}")
    logger.info(f"工作目录: {os.getcwd()}")
    logger.info(f"程序目录: {APP_DIR}")
    
    try:
        # 直接传递 app 对象，而不是字符串引用
        # 这样在 PyInstaller 打包后也能正常工作
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        logger.info("用户中断，服务停止")
        print()
        print("服务已停止")
    except Exception as e:
        logger.critical(f"服务启动失败: {e}")
        logger.critical(traceback.format_exc())
        print()
        print("=" * 50)
        print("  启动失败！错误信息：")
        print(f"  {e}")
        print()
        print(f"  详细日志请查看: {LOG_FILE}")
        print("=" * 50)
        print()
        input("按回车键退出...")
        sys.exit(1)
