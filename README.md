# Data Crawler API

数据查询 API 服务 - 提供 Steam / XD（心动）游戏数据的查询接口。

## 功能特性

- Steam 地区排名查询
- Steam 玩家峰值数据查询
- Steam 推荐评价数据查询
- XD 游戏列表与赛季配置查询
- 区域代码名称映射
- 内存缓存（1 小时 TTL）
- 异步 MySQL 数据库访问

## 技术栈

- **Python 3.11+**
- **FastAPI** - 高性能 Web 框架
- **aiomysql** - 异步 MySQL 驱动
- **httpx** - 异步 HTTP 客户端
- **BeautifulSoup4 / lxml** - HTML 解析
- **Pydantic / pydantic-settings** - 数据验证与配置管理
- **tenacity** - 重试机制

## 快速开始

### 环境要求

- Python >= 3.11
- MySQL 数据库

### 安装

```bash
# 克隆项目
git clone https://github.com/horgrix/data-crawler-api.git
cd data-crawler-api

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 安装依赖
pip install -e .

# 安装开发依赖（可选）
pip install -e ".[dev]"
```

### 配置

在项目根目录创建 `.env` 文件：

```env
DB_HOST=your_mysql_host
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_DATABASE=data_crawler
DB_CHARSET=utf8mb4
```

### 运行

```bash
# 开发模式运行
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/docs 查看 Swagger API 文档。

## 项目结构

```
data-crawler-api/
├── src/
│   ├── main.py              # FastAPI 应用入口 + 生命周期管理
│   ├── config.py            # 配置管理（pydantic-settings）
│   ├── db.py                # MySQL 连接池管理
│   ├── api/
│   │   ├── routes.py        # 基础路由（健康检查）
│   │   ├── steam_api.py     # Steam 数据 API（/steam 前缀）
│   │   └── xd_api.py        # XD 数据 API（/xd 前缀 + 缓存层）
│   └── models/
│       └── schemas.py       # Pydantic 数据模型
├── prompt/
│   ├── api.md               # Steam API 需求文档
│   └── api-xd.md            # XD API 需求文档
├── pyproject.toml
├── .gitignore
└── README.md
```

## API 接口

所有接口前缀: `/api/v1`

### 系统

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |

### Steam 数据 (`/steam`)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/steam/region_rank` | 查询 Steam 地区排名 |
| GET | `/steam/players` | 查询 Steam 玩家峰值数据 |
| GET | `/steam/recommendations` | 查询 Steam 推荐评价数据 |
| GET | `/steam/region_mapping` | 查询区域代码名称映射 |

### XD 数据 (`/xd`)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/xd/games` | 查询心动在 Steam 的所有游戏 |
| GET | `/xd/games/torchlight/season/configs` | 查询火炬之光赛季配置 |
| GET | `/xd/games/torchlight/seasons/players` | 查询赛季游戏峰值玩家 |
| GET | `/xd/region_mapping` | 查询区域代码名称映射 |

## License

MIT