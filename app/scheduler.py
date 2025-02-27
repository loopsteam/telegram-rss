from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging
from datetime import datetime, timedelta
import pytz
import asyncio

logger = logging.getLogger(__name__)


class FeedScheduler:
    def __init__(self, telegram_client):
        self.telegram_client = telegram_client
        self.scheduler = AsyncIOScheduler()
        self.cached_messages = []
        self.last_update = None
        self._setup_scheduler()

    def _setup_scheduler(self):
        """配置调度器"""
        self.scheduler.add_job(
            self.update_feed,
            IntervalTrigger(hours=1),
            next_run_time=datetime.now(pytz.UTC),  # 立即执行一次
            max_instances=1,  # 防止重复执行
            coalesce=True,  # 合并错过的任务
            misfire_grace_time=None  # 错过的任务立即执行
        )

    async def update_feed(self):
        """更新订阅内容"""
        try:
            logger.info(f"Starting feed update at {datetime.now(pytz.UTC)}")

            # 获取新消息
            new_messages = await self.telegram_client.get_new_messages()

            if new_messages:
                # 更新缓存
                self.cached_messages = new_messages
                self.last_update = datetime.now(pytz.UTC)
                logger.info(f"Feed updated successfully, got {len(new_messages)} messages")
            else:
                logger.warning("No new messages found during update")

        except Exception as e:
            logger.error(f"Error updating feed: {e}")
            # 可以在这里添加重试逻辑

    def start(self):
        """启动调度器"""
        try:
            self.scheduler.start()
            logger.info("Scheduler started successfully")
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise

    def stop(self):
        """停止调度器"""
        try:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")

    def _clean_expired_messages(self):
        """清理超过24小时的消息"""
        now = datetime.now(pytz.UTC)
        self.cached_messages = [
            msg for msg in self.cached_messages 
            if now - msg['date'] < timedelta(hours=24)
        ]

    def get_cached_messages(self):
        """获取缓存的消息并清理过期消息"""
        self._clean_expired_messages()
        return self.cached_messages

    def get_last_update_time(self):
        """获取最后更新时间"""
        return self.last_update