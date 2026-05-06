# Edge TTS Web 🌐

> A free, open-source online Text-to-Speech web application powered by Microsoft Edge's TTS service. Supports **75 languages** and **322+ voices** with a beautiful multilingual interface.

[中文文档](#中文文档) | [English](#english)

---

<a id="english"></a>

## ✨ Features

- 🌍 **75 Languages** — Covers most languages worldwide
- 🎙️ **322+ Voices** — Male and female voices with regional variants
- 🚀 **Free & No API Key** — Powered by Microsoft Edge's online TTS service, no registration required
- 🎨 **Multilingual UI** — Interface supports Chinese, English, Japanese, Korean, Vietnamese, and Hindi
- ⚡ **Speed Control** — Adjustable speech rate from -100% to +100%
- 🎧 **Online Preview** — Listen to generated audio directly in the browser
- 📥 **Download** — Download generated MP3 files
- 🔒 **Secure** — Path traversal protection on file downloads
- 📱 **Responsive** — Works on desktop and mobile devices

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python + FastAPI |
| TTS Engine | edge-tts |
| Frontend | HTML + jQuery + Bootstrap 5 |
| Template Engine | Jinja2 |
| Server | Uvicorn |

## 📦 Installation

### Prerequisites

- Python 3.8+
- pip

### Steps

1. **Clone the repository**

```bash
git clone https://github.com/sxlixiaoyang/edge_tts_web.git
cd edge_tts_web
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Run the server**

```bash
python main.py
```

4. **Open in browser**

Visit [http://localhost:8000](http://localhost:8000)

## 📁 Project Structure

```
edge_tts_web/
├── main.py              # FastAPI application (backend)
├── requirements.txt     # Python dependencies
├── README.md            # Documentation
├── templates/
│   └── index.html       # Frontend page (multilingual UI)
└── mp3/                 # Generated audio files (auto-created)
```

## 🔗 API Reference

### `GET /`

Returns the main web page.

### `GET /api/voices`

Returns all available voices grouped by language.

**Response:**
```json
{
  "message": "success",
  "voices": {
    "Chinese": {
      "zh-CN": [
        {"name": "zh-CN-XiaoxiaoNeural", "gender": "Female", "display_name": "Xiaoxiao"},
        {"name": "zh-CN-YunjianNeural", "gender": "Male", "display_name": "Yunjian"}
      ]
    }
  }
}
```

### `POST /synthesize`

Synthesize text to speech.

**Request Body:**
```json
{
  "text": "Hello, world!",
  "voice": "en-US-JennyNeural",
  "rate": "+0%"
}
```

**Response:**
```json
{
  "message": "success",
  "download_link": "/mp3/abc123.mp3"
}
```

### `GET /download?filename=xxx.mp3`

Download a generated audio file.

## 🌍 Supported Languages

| Region | Languages |
|--------|-----------|
| East Asia | Chinese, Japanese, Korean, Mongolian |
| Southeast Asia | Vietnamese, Thai, Khmer, Lao, Indonesian, Filipino, Malay, Burmese, Javanese, Sundanese |
| South Asia | Hindi, Bengali, Tamil, Telugu, Urdu, Marathi, Gujarati, Kannada, Malayalam, Punjabi, Nepali, Sinhala |
| Europe | English, French, German, Spanish, Italian, Portuguese, Dutch, Russian, Polish, Swedish, Norwegian, Danish, Finnish, Czech, Greek, Hungarian, Romanian, Bulgarian, Slovak, Ukrainian, Croatian, Serbian, Slovenian, Estonian, Latvian, Lithuanian, Icelandic, Irish, Welsh, Catalan, Galician, Basque, Albanian, Macedonian, Bosnian, Maltese |
| Middle East | Arabic, Hebrew, Persian, Turkish, Azerbaijani, Georgian, Armenian, Pashto, Kurdish, Urdu |
| Africa | Afrikaans, Swahili, Zulu, Amharic, Somali |
| Other | Inuktitut, Kazakh, Uzbek |

## 🚀 Deployment

### Local

```bash
python main.py
```

### Docker (coming soon)

```bash
docker build -t edge-tts-web .
docker run -p 8000:8000 edge-tts-web
```

### Cloud Platforms

This project can be deployed on any platform that supports Python:
- **Railway** / **Render** / **Fly.io**
- **Vercel** (with Python serverless functions)
- **VPS** with Nginx reverse proxy

## 📄 License

MIT License

## 🙏 Credits

- [edge-tts](https://github.com/rany2/edge-tts) — Microsoft Edge TTS Python library
- [FastAPI](https://fastapi.tiangolo.com/) — Modern Python web framework
- [Bootstrap](https://getbootstrap.com/) — CSS framework

---

<a id="中文文档"></a>

## ✨ 功能特性

- 🌍 **75种语言** — 覆盖全球大部分语言
- 🎙️ **322+种音源** — 男声和女声，包含各地区变体
- 🚀 **完全免费** — 基于微软Edge在线TTS服务，无需注册，无需API密钥
- 🎨 **多语言界面** — 支持中文、英语、日语、韩语、越南语、印地语6种界面语言
- ⚡ **语速调节** — 支持 -100% 到 +100% 的语速调节
- 🎧 **在线试听** — 在浏览器中直接播放生成的语音
- 📥 **下载功能** — 支持下载生成的MP3文件
- 🔒 **安全防护** — 文件下载接口防止目录遍历攻击
- 📱 **响应式设计** — 适配桌面端和移动端

## 🛠️ 技术栈

| 组件 | 技术 |
|------|------|
| 后端 | Python + FastAPI |
| 语音引擎 | edge-tts |
| 前端 | HTML + jQuery + Bootstrap 5 |
| 模板引擎 | Jinja2 |
| 服务器 | Uvicorn |

## 📦 安装部署

### 环境要求

- Python 3.8+
- pip

### 安装步骤

1. **克隆仓库**

```bash
git clone https://github.com/sxlixiaoyang/edge_tts_web.git
cd edge_tts_web
```

2. **安装依赖**

```bash
pip install -r requirements.txt
```

3. **启动服务**

```bash
python main.py
```

4. **打开浏览器**

访问 [http://localhost:8000](http://localhost:8000)

## 📁 项目结构

```
edge_tts_web/
├── main.py              # FastAPI 应用（后端）
├── requirements.txt     # Python 依赖
├── README.md            # 项目文档
├── templates/
│   └── index.html       # 前端页面（多语言UI）
└── mp3/                 # 生成的音频文件（自动创建）
```

## 🔗 API 接口文档

### `GET /`

返回主页。

### `GET /api/voices`

获取所有可用语音列表，按语言分组。

**响应示例：**
```json
{
  "message": "success",
  "voices": {
    "中文": {
      "zh-CN": [
        {"name": "zh-CN-XiaoxiaoNeural", "gender": "女", "display_name": "小小"},
        {"name": "zh-CN-YunjianNeural", "gender": "男", "display_name": "云剑"}
      ]
    }
  }
}
```

### `POST /synthesize`

文本转语音合成。

**请求体：**
```json
{
  "text": "你好，世界！",
  "voice": "zh-CN-XiaoxiaoNeural",
  "rate": "+0%"
}
```

**响应示例：**
```json
{
  "message": "success",
  "download_link": "/mp3/abc123.mp3"
}
```

### `GET /download?filename=xxx.mp3`

下载生成的音频文件。

## 🌍 支持的语言

| 地区 | 语言 |
|------|------|
| 东亚 | 中文、日语、韩语、蒙古语 |
| 东南亚 | 越南语、泰语、高棉语、老挝语、印尼语、菲律宾语、马来语、缅甸语、爪哇语、巽他语 |
| 南亚 | 印地语、孟加拉语、泰米尔语、泰卢固语、乌尔都语、马拉地语、古吉拉特语、卡纳达语、马拉雅拉姆语、旁遮普语、尼泊尔语、僧伽罗语 |
| 欧洲 | 英语、法语、德语、西班牙语、意大利语、葡萄牙语、荷兰语、俄语、波兰语、瑞典语、挪威语、丹麦语、芬兰语、捷克语、希腊语、匈牙利语、罗马尼亚语、保加利亚语、斯洛伐克语、乌克兰语、克罗地亚语、塞尔维亚语、斯洛文尼亚语、爱沙尼亚语、拉脱维亚语、立陶宛语、冰岛语、爱尔兰语、威尔士语、加泰罗尼亚语、加利西亚语、巴斯克语、阿尔巴尼亚语、马其顿语、波斯尼亚语、马耳他语 |
| 中东 | 阿拉伯语、希伯来语、波斯语、土耳其语、阿塞拜疆语、格鲁吉亚语、亚美尼亚语、普什图语、库尔德语 |
| 非洲 | 南非荷兰语、斯瓦希里语、祖鲁语、阿姆哈拉语、索马里语 |
| 其他 | 因纽特语、哈萨克语、乌兹别克语 |

## 🚀 部署方式

### 本地运行

```bash
python main.py
```

### Docker 部署（即将支持）

```bash
docker build -t edge-tts-web .
docker run -p 8000:8000 edge-tts-web
```

### 云平台部署

本项目可部署在任何支持 Python 的云平台上：
- **Railway** / **Render** / **Fly.io**
- **Vercel**（Python Serverless Functions）
- **VPS** + Nginx 反向代理

## 📄 开源协议

MIT License

## 🙏 致谢

- [edge-tts](https://github.com/rany2/edge-tts) — 微软Edge TTS Python库
- [FastAPI](https://fastapi.tiangolo.com/) — 现代Python Web框架
- [Bootstrap](https://getbootstrap.com/) — CSS框架
