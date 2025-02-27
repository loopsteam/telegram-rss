# run.py
import os
import logging
from setup import setup_project

if __name__ == "__main__":
    # 初始化项目结构
    setup_project()

    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/app.log'),
            logging.StreamHandler()
        ]
    )

    # 修改运行方式
    import uvicorn

    uvicorn.run(
        "app.main:app",  # 使用导入字符串而不是直接传递 app 对象
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True,
        workers=1
    )