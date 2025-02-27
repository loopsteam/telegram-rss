from telethon import TelegramClient
import configparser
import asyncio
from datetime import datetime
import re
import logging
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TelegramFeedClient:
    def __init__(self):
        # 确保目录存在
        os.makedirs('data/session', exist_ok=True)
        os.makedirs('logs', exist_ok=True)

        config = configparser.ConfigParser()
        config.read('data/config.ini')

        self.api_id = config['Telegram']['api_id']
        self.api_hash = config['Telegram']['api_hash']
        self.channel = config['Telegram']['channel']
        self.last_message_id = int(config['Telegram']['last_message_id'])

        # 初始化客户端
        self.client = TelegramClient('data/session/bot', self.api_id, self.api_hash)

    async def start(self):
        try:
            await self.client.start()
            logger.info("Telegram client started successfully")
        except Exception as e:
            logger.error(f"Failed to start Telegram client: {e}")
            raise

    async def get_new_messages(self):
        try:
            if not self.client.is_connected():
                await self.start()

            channel = await self.client.get_entity(f't.me/{self.channel}')
            messages = []
            seen_links = set()  # 用于去重

            async for message in self.client.iter_messages(channel, min_id=self.last_message_id, limit=50):
                try:
                    if not message.text:
                        continue

                    # 获取评论
                    comments = []
                    async for reply in self.client.iter_messages(channel, reply_to=message.id):
                        comments.append(reply.text)

                    comments_text = "\n".join(comments)

                    # 提取链接
                    all_text = message.text + "\n" + comments_text
                    
                    # 提取链接
                    quark_link = ""
                    baidu_link = ""
                    
                    quark_match = re.search(r'https://pan\.quark\.cn/s/[a-zA-Z0-9]+', all_text)
                    if quark_match:
                        quark_link = quark_match.group(0)

                    baidu_match = re.search(r'https://pan\.baidu\.com/s/[^\s]+', all_text)
                    if baidu_match:
                        baidu_link = baidu_match.group(0)

                    # 如果没有任何有效链接，跳过该消息
                    if not quark_link and not baidu_link:
                        continue
                        
                    # 链接去重
                    link_pair = (quark_link, baidu_link)
                    if link_pair in seen_links:
                        continue
                    seen_links.add(link_pair)

                    # 清理和标准化消息内容
                    content_lines = message.text.split('\n')
                    title = content_lines[0].strip()
                    
                    # 提取描述信息
                    description = ""
                    for line in content_lines[1:]:
                        line = line.strip()
                        if line and not line.startswith('http') and '链接' not in line:
                            if line.startswith('描述：'):
                                description = line[3:].strip()
                                break
                            elif '描述' in line:
                                description = line.split('描述')[-1].strip(':：').strip()
                                break
                    
                    # 如果没有找到描述，使用标题作为描述
                    if not description:
                        description = title

                    # 构建标准化的消息对象
                    message_obj = {
                        'id': message.id,
                        'title': title[:100],  # 限制标题长度
                        'content': f"{title}\n\n描述：{description}",  # 标准化内容格式
                        'date': message.date,
                        'quark_link': quark_link,
                        'baidu_link': baidu_link,
                        'comments': comments_text if comments else ""
                    }

                    messages.append(message_obj)
                    logger.debug(f"Processed message {message.id}")

                except Exception as e:
                    logger.error(f"Error processing message {message.id}: {e}")
                    continue

            logger.info(f"Retrieved {len(messages)} new messages")
            return messages

        except Exception as e:
            logger.error(f"Error fetching messages: {e}")
            return []

    async def stop(self):
        try:
            await self.client.disconnect()
            logger.info("Telegram client stopped")
        except Exception as e:
            logger.error(f"Error stopping client: {e}")