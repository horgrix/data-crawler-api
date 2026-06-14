# Ubuntu 部署Shell脚本

## 项目路径
项目目录：/home/ubuntu/projects/data-crawler/data-crawler-api
git url: https://github.com/horgrix/data-crawler-api.git
NGINX目录：/etc/nginx
NGINX配置文件：/etc/nginx/conf.d/horgrix.conf

## 从Git仓库获取代码
1. 先检查代码库之前是否已经拉取过
2. 如果代码库已经存在，则更新代码
3. 果如不存在，则拉取最新的代码


## 部署 data-crawler-api 应用
1. 进入项目目录
2. 创建 .env 配置文件，里面配置项包含
    DB_HOST
    DB_PORT
    DB_USER
    DB_PASSWORD
    DB_DATABASE
    DB_CHARSET
    从环境变量中照，若有值则做默认值，没有值然后逐个与用户确认，用户可以输入覆盖
3. 创建项目的虚拟环境
4. 安装依赖

## 部署 data-crawler-api.servce 服务
sudo tee /etc/systemd/system/data-crawler-api.servce > /dev/null << SERVICEEOF
[Unit]
Description=data-crawler-api
After=network.target mysql.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=项目目录
ExecStart=项目目录/.venv/bin/python3 项目目录/src/main.py
Restart=always
RestartSec=10
StandardOutput=append:项目目录/log/data-crawler-api.log
StandardError=append:项目目录/log/data-crawler-api_error.log

[Install]
WantedBy=multi-user.target
SERVICEEOF


## 配置 NGINX 服务
1. 先检查配置文件是否存在
2. 存在就先备份
3. 将/api/v1/的请求转发给本机的8000端口，设置缓存
4. 测试配置的准确性
5. 重新加载

## 重载 systemd 守护进程

## 启动 data-crawler-api.servce 服务

## 完成部署
1. 请求 /api/v1/health 若返回{"status":"ok","version":"0.1.0","timestamp":"2026-06-14T20:53:18.458225"}， status=ok 则说明完成部署