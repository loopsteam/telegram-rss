from feedgen.feed import FeedGenerator
from datetime import datetime
import pytz
import logging

logger = logging.getLogger(__name__)


class RSSFeedGenerator:
    def __init__(self, base_url):
        self.base_url = base_url
        self.fg = FeedGenerator()
        self.setup_feed()

    def setup_feed(self):
        """设置基本的Feed信息"""
        self.fg.title('DuanJu Quark Channel')
        self.fg.link(href=self.base_url)
        self.fg.description('Telegram DuanJu Quark Channel RSS Feed')
        self.fg.language('zh-CN')
        self.fg.lastBuildDate(datetime.now(pytz.UTC))
        self.fg.generator('Telegram RSS Bot')

    def add_entries(self, messages):
        """添加订阅条目"""
        try:
            for message in messages:
                fe = self.fg.add_entry()
                fe.id(str(message['id']))
                fe.title(message['title'])
                
                # 构建简化的内容
                content = self.build_content(message)
                fe.content(content, type='text')
                
                fe.link(href=f"https://t.me/{message.get('channel', 'DuanJuQuark')}/{message['id']}")
                fe.published(message['date'])

            logger.debug(f"Added {len(messages)} entries to feed")
        except Exception as e:
            logger.error(f"Error adding entries to feed: {e}")

    def build_content(self, message):
        """构建简化的消息内容格式"""
        content_parts = [
            message['date'].strftime('%a, %d %b %Y %H:%M:%S +0000'),
            message['title']
        ]
        
        if message['quark_link']:
            content_parts.append(f"夸克网盘：{message['quark_link']}")
        if message['baidu_link']:
            content_parts.append(f"百度网盘：{message['baidu_link']}")
            
        content_parts.append(str(message['id']))
        
        return '\n'.join(content_parts)

    def get_feed(self, format='rss'):
        """获取指定格式的feed内容"""
        try:
            if format == 'atom':
                return self.fg.atom_str(pretty=True)
            return self.fg.rss_str(pretty=True)
        except Exception as e:
            logger.error(f"Error generating {format} feed: {e}")
            return ""