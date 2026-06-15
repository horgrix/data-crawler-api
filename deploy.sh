#!/bin/bash
set -e

# ============================================================
# Data Crawler API 部署脚本
# 适用于 Ubuntu 系统
# ============================================================

PROJECT_DIR="/home/ubuntu/projects/data-crawler/data-crawler-api"
GIT_URL="https://github.com/horgrix/data-crawler-api.git"
NGINX_CONF="/etc/nginx/conf.d/data-crawler-api.conf"
SERVICE_NAME="data-crawler-api"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

echo "========================================"
echo "  Data Crawler API 部署脚本"
echo "========================================"

# ==================== 1. 从 Git 仓库获取代码 ====================

echo ""
echo "[1/6] 获取代码..."

if [ -d "$PROJECT_DIR/.git" ]; then
    echo "  代码库已存在，执行 git pull..."
    cd "$PROJECT_DIR"
    git pull origin master
else
    echo "  克隆代码库..."
    mkdir -p "$(dirname "$PROJECT_DIR")"
    git clone "$GIT_URL" "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi

# ==================== 2. 创建 .env 配置文件 ====================

echo ""
echo "[2/6] 配置环境变量..."

ENV_FILE="$PROJECT_DIR/.env"
> "$ENV_FILE"  # 清空/创建文件

configure_env_var() {
    local var_name=$1
    local env_value="${!var_name}"  # 从系统环境变量取值

    if [ -n "$env_value" ]; then
        echo "  环境变量 $var_name 已存在: $env_value"
        read -p "  输入 $var_name [默认: $env_value]: " user_input
        if [ -n "$user_input" ]; then
            echo "${var_name}=${user_input}" >> "$ENV_FILE"
        else
            echo "${var_name}=${env_value}" >> "$ENV_FILE"
        fi
    else
        read -p "  请输入 $var_name: " user_input
        while [ -z "$user_input" ]; do
            read -p "  $var_name 不能为空，请重新输入: " user_input
        done
        echo "${var_name}=${user_input}" >> "$ENV_FILE"
    fi
}

echo "  配置数据库连接信息："
configure_env_var "DB_HOST"
configure_env_var "DB_PORT"
configure_env_var "DB_USER"
configure_env_var "DB_PASSWORD"
configure_env_var "DB_DATABASE"
configure_env_var "DB_CHARSET"

echo "  .env 文件已生成。"

# ==================== 3. 创建虚拟环境并安装依赖 ====================

echo ""
echo "[3/6] 创建虚拟环境并安装依赖..."

cd "$PROJECT_DIR"

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "  虚拟环境已创建。"
else
    echo "  虚拟环境已存在，跳过创建。"
fi

.venv/bin/pip install --upgrade pip -q
.venv/bin/pip install -e . -q
echo "  依赖安装完成。"

# ==================== 4. 创建 systemd 服务 ====================

echo ""
echo "[4/6] 创建 systemd 服务..."

# 确保日志目录存在
mkdir -p "$PROJECT_DIR/log"

sudo tee "$SERVICE_FILE" > /dev/null << SERVICEEOF
[Unit]
Description=data-crawler-api
After=network.target mysql.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=${PROJECT_DIR}
ExecStart=${PROJECT_DIR}/.venv/bin/python3 ${PROJECT_DIR}/src/main.py
Restart=always
RestartSec=10
StandardOutput=append:${PROJECT_DIR}/log/data-crawler-api.log
StandardError=append:${PROJECT_DIR}/log/data-crawler-api_error.log

[Install]
WantedBy=multi-user.target
SERVICEEOF

echo "  服务文件已创建: $SERVICE_FILE"

# ==================== 5. 配置 NGINX ====================

echo ""
echo "[5/6] 配置 NGINX..."

if [ -f "$NGINX_CONF" ]; then
    BACKUP="${NGINX_CONF}.backup.$(date +%Y%m%d%H%M%S)"
    sudo cp "$NGINX_CONF" "$BACKUP"
    echo "  已备份原配置: $BACKUP"
fi

sudo tee "$NGINX_CONF" > /dev/null << NGINXEOF
# Data Crawler API - NGINX 配置

# 缓存设置
proxy_cache_path /var/cache/nginx/data_crawler_api levels=1:2 keys_zone=crawler_cache:10m max_size=100m inactive=60m;
proxy_cache_key "\$scheme\$request_method\$host\$request_uri";

server {
    listen 80;

    location /api/v1/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # 缓存设置
        proxy_cache crawler_cache;
        proxy_cache_valid 200 10m;
        proxy_cache_bypass \$http_cache_control;
        add_header X-Cache-Status \$upstream_cache_status;
    }
}
NGINXEOF

echo "  NGINX 配置已写入: $NGINX_CONF"

# 测试配置
echo "  测试 NGINX 配置..."
if sudo nginx -t 2>&1; then
    echo "  NGINX 配置测试通过。"
else
    echo "  [错误] NGINX 配置测试失败，请检查配置文件。"
    exit 1
fi

# 重新加载
sudo nginx -s reload
echo "  NGINX 已重新加载。"

# ==================== 6. 重载并启动服务 ====================

echo ""
echo "[6/6] 启动服务..."

sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

echo "  服务已启动。"

# ==================== 验证部署 ====================

echo ""
echo "========================================"
echo "  验证部署..."
echo "========================================"

sleep 2

HEALTH_RESPONSE=$(curl -s --connect-timeout 5 http://127.0.0.1/api/v1/health 2>/dev/null || echo "")

if echo "$HEALTH_RESPONSE" | grep -q '"status":"ok"'; then
    echo ""
    echo "  ✓ 部署成功！"
    echo "  健康检查响应: $HEALTH_RESPONSE"
else
    echo ""
    echo "  ✗ 健康检查失败，请检查日志："
    echo "    journalctl -u ${SERVICE_NAME} -n 50 --no-pager"
    echo "    或: tail -f ${PROJECT_DIR}/log/data-crawler-api.log"
    exit 1
fi

echo ""
echo "========================================"
echo "  部署完成！"
echo "========================================"