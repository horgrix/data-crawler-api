# Data Crawler API

数据爬虫 API 服务 - 提供数据采集、解析与查询接口。

## 功能特性

- 异步数据采集与解析
- RESTful API 接口
- 可配置的爬虫规则
- 数据存储与检索

## 技术栈

- **Python 3.11+**
- **FastAPI** - 高性能 Web 框架
- **httpx** - 异步 HTTP 客户端
- **BeautifulSoup4 / lxml** - HTML 解析
- **Pydantic** - 数据验证

## 快速开始

### 环境要求

- Python >= 3.11

### 安装

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 安装依赖
pip install -e .

# 安装开发依赖（可选）
pip install -e ".[dev]"
```

### 运行

```bash
# 开发模式运行
uvicorn data_crawler_api.main:app --reload --host 0.0.0.0 --port 8000

# 或使用生产模式
python -m data_crawler_api
```

访问 http://localhost:8000/docs 查看 API 文档。

## 项目结构

```
data-crawler-api/
├── src/
│   └── data_crawler_api/
│       ├── __init__.py
│       ├── main.py          # FastAPI 应用入口
│       ├── config.py        # 配置管理
│       ├── api/
│       │   ├── __init__.py
│       │   └── routes.py    # API 路由
│       ├── crawlers/
│       │   ├── __init__.py
│       │   └── base.py      # 爬虫基类
│       └── models/
│           ├── __init__.py
│           └── schemas.py   # Pydantic 模型
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── pyproject.toml
├── .gitignore
└── README.md
```

## License

MIT