from fastapi import FastAPI, Response, HTTPException
from .telegram_client import TelegramFeedClient
from .feed_generator import RSSFeedGenerator
from .scheduler import FeedScheduler
import uvicorn
import logging
import sys
from datetime import datetime
import pytz

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Telegram RSS Feed",
    description="RSS feed for Telegram channel DuanJuQuark",
    version="1.0.0"
)

# 初始化客户端和调度器
telegram_client = TelegramFeedClient()
feed_scheduler = FeedScheduler(telegram_client)
base_url = "http://localhost:8000"  # 本地开发用


@app.on_event("startup")
async def startup_event():
    """启动时初始化服务"""
    try:
        await telegram_client.start()
        feed_scheduler.start()
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)


@app.on_event("shutdown")
async def shutdown_event():
    """关闭时清理资源"""
    try:
        await telegram_client.stop()
        feed_scheduler.stop()
        logger.info("Application shutdown successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


@app.get("/rss")
async def get_rss():
    """获取RSS格式的订阅"""
    try:
        messages = feed_scheduler.get_cached_messages()
        if not messages:
            logger.warning("No messages available in cache")

        feed_gen = RSSFeedGenerator(base_url)
        feed_gen.add_entries(messages)

        return Response(
            content=feed_gen.get_feed(),
            media_type="application/xml"
        )
    except Exception as e:
        logger.error(f"Error generating RSS feed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/atom")
async def get_atom():
    """获取Atom格式的订阅"""
    try:
        messages = feed_scheduler.get_cached_messages()
        if not messages:
            logger.warning("No messages available in cache")

        feed_gen = RSSFeedGenerator(base_url)
        feed_gen.add_entries(messages)

        return Response(
            content=feed_gen.get_feed(format='atom'),
            media_type="application/xml"
        )
    except Exception as e:
        logger.error(f"Error generating Atom feed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(pytz.UTC).isoformat(),
        "cached_messages_count": len(feed_scheduler.get_cached_messages())
    }


@app.get("/update")
async def force_update():
    """强制更新订阅内容"""
    try:
        await feed_scheduler.update_feed()
        return {
            "status": "success",
            "timestamp": datetime.now(pytz.UTC).isoformat(),
            "message": "Feed updated successfully"
        }
    except Exception as e:
        logger.error(f"Error during force update: {e}")
        raise HTTPException(status_code=500, detail="Update failed")


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)