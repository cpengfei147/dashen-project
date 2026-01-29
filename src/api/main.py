"""
FastAPI应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import CORS_ORIGINS
from src.api.routes import router
from src.models.database import init_db

# 创建应用
app = FastAPI(
    title="搬家助手 API",
    description="智能搬家助手MVP-0 API接口",
    version="0.1.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    init_db()


@app.get("/")
async def root():
    """健康检查"""
    return {"status": "ok", "message": "搬家助手API运行中"}


@app.get("/health")
async def health():
    """健康检查接口"""
    return {"status": "healthy"}
