# app/__init__.py
from .telegram_client import TelegramFeedClient
from .feed_generator import RSSFeedGenerator
from .scheduler import FeedScheduler

__version__ = "1.0.0"