"""
配置模块
"""

import os
from typing import Optional

class Settings:
    """应用配置类"""
    
    def __init__(self):
        # 本地LLM模型路径
        self.LOCAL_LLM_PATH: str = r"D:\project\Xianyu_AutoAgent\model\qwen\Qwen2___5-1___5B-Instruct"
        
        # 日志配置
        self.LOG_LEVEL: str = "INFO"
        
        # 爬虫配置
        self.CRAWLER_MAX_ITEMS: int = 10
        
        # LLM配置
        self.LLM_MAX_TOKENS: int = 200
        self.LLM_TEMPERATURE: float = 0.1
        self.LLM_DO_SAMPLE: bool = False
