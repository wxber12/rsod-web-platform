# RSOD 遥感目标检测平台 (RSOD Detection Platform)

RSOD 遥感目标检测平台是一个全栈式 Web 应用，专门用于对遥感影像（如卫星图、无人机航拍图）进行智能目标检测。平台基于强大的 YOLO 系列模型，支持图片、批量图片及视频的目标检测，并提供了完整的用户管理与检测历史记录功能。

## 🌟 核心特性

- **多模态检测**：支持单张图片、批量图片、以及视频流的目标检测。
- **动态模型切换**：支持后台无缝加载和切换多个 `.pt` 模型（如 `best_rsod.pt`, `best_plant_village.pt`）。
- **完整业务流**：包含用户注册、登录、找回密码（邮件通知），以及个人检测历史记录的管理与查询。
- **高性能架构**：
  - **后端**：FastAPI 提供高性能异步 API，PostgreSQL 持久化业务数据，Redis 缓存加速，MinIO 负责海量图像与视频结果的云原生对象存储。
  - **算法**：基于 Ultralytics YOLO 的快速推理，通过 OpenCV-headless 处理图像和视频帧。
  - **前端**：Vue 3 + Vite + Element Plus + Pinia，提供丝滑的响应式 UI 交互。
- **现代化部署**：完善的 Docker Compose 编排，支持源码一键构建以及离线镜像包（.tar）一键导入部署，极致“开箱即用”。

---

## 🏗️ 架构与技术栈

### Backend (后端)
- **框架**: FastAPI (Python 3.11)
- **数据库**: PostgreSQL 15 (数据) + Redis 7 (缓存)
- **存储**: MinIO (对象存储，兼容 S3 协议)
- **AI/CV**: Ultralytics YOLO, OpenCV-headless
- **安全与工具**: PyJWT, Bcrypt, SQLAlchemy, Pydantic

### Frontend (前端)
- **框架**: Vue 3 (Composition API)
- **构建工具**: Vite
- **UI 组件库**: Element Plus
- **状态管理**: Pinia
- **HTTP 客户端**: Axios

---

## 🚀 快速启动 (本地开发)

确保你本地已经安装了 Node.js、Python 3.11+ 以及 Docker Desktop。

### 1. 启动基础设施 (数据库与存储)
```bash
# 在项目根目录下，启动 PostgreSQL, Redis, MinIO
docker compose -f docker-compose.prod.yml up -d postgres redis minio
```

### 2. 配置环境变量
在 `backend` 目录下，确认存在 `.env` 文件。该文件包含数据库连接、JWT 密钥、MinIO 和 SMTP 邮件配置。大部分配置项已有合理的默认值。

### 3. 一键启动前后端服务
项目根目录提供了一个自动化启动脚本 `run.py`，它会自动进行端口检查、启动 Docker 服务、激活后端虚拟环境并启动前端页面：
```bash
python run.py
```
- 前端访问地址：`http://localhost:5173`
- 后端 API 文档：`http://localhost:8000/docs`
- 默认管理员账号：`admin` / `123456`

*(注意：运行前请确保 `.pt` 模型文件已放置在 `backend/app/models/` 目录下)*

---

## 🐳 Docker 生产部署

平台提供了高度优化的 Docker 生产部署配置。后端镜像通过多阶段构建与剔除多余的 CUDA 依赖，镜像体积从约 10GB 缩减至不到 2GB。

### 方式一：基于源码直接构建与部署
```bash
# 在项目根目录下执行
docker compose -f docker-compose.prod.yml up -d --build
```

### 方式二：离线打包与部署 (推荐用于生产环境)
如果你需要在无互联网环境或者不希望在服务器上暴露源码，可以使用此方式。

**1. 在开发机打包所有镜像:**
```bash
docker save -o rsod_all_images.tar postgres:15 redis:7 minio/minio:latest rsod-web-platform-frontend:latest rsod-web-platform-backend:latest
```

**2. 在目标服务器导入并启动:**
将生成的 `rsod_all_images.tar` 以及项目里的 `docker-compose.deploy.yml` 拷贝到服务器上：
```bash
# 导入镜像
docker load -i rsod_all_images.tar

# 使用专属的部署编排文件启动服务
docker compose -f docker-compose.deploy.yml up -d
```

---

## 📂 目录结构说明

```text
rsod-web-platform/
├── backend/                  # 后端源码
│   ├── app/                  # 核心业务逻辑 (api, models, services, utils)
│   ├── main.py               # FastAPI 入口文件
│   ├── database.py           # 数据库连接与初始化脚本
│   ├── requirements.txt      # Python 依赖清单
│   └── Dockerfile            # 后端容器构建脚本
├── frontend/                 # 前端源码
│   ├── src/                  # Vue 源码 (components, views, store, router)
│   ├── package.json          # Node 依赖清单
│   ├── nginx.conf            # 生产环境 Nginx 代理配置
│   └── Dockerfile            # 前端容器构建脚本 (多阶段构建)
├── storage/                  # 挂载的本地数据卷 (PostgreSQL, Redis, MinIO)
├── docker-compose.prod.yml   # 生产环境编译构建编排
├── docker-compose.deploy.yml # 生产环境纯镜像离线部署编排
└── run.py                    # 本地开发一键启动脚手架
```

## 📜 许可证

MIT License. See `LICENSE` for more information.
