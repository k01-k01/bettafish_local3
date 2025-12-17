"""
简化版数据库模块
使用SQLite数据库存储分析结果
"""

import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Any
from loguru import logger

class SimpleDatabase:
    """简化版数据库操作类"""
    
    def __init__(self, db_path: str = "bettafish_local3.db"):
        """
        初始化数据库
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 创建分析记录表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS analysis_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        topic TEXT NOT NULL,
                        crawled_data TEXT,
                        insight_result TEXT,
                        report TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 创建爬虫数据表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS crawled_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        topic TEXT NOT NULL,
                        content TEXT NOT NULL,
                        likes INTEGER DEFAULT 0,
                        comments INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
                logger.info("数据库初始化完成")
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise
    
    def save_analysis_record(self, topic: str, crawled_data: str, 
                           insight_result: str, report: str) -> bool:
        """
        保存分析记录
        
        Args:
            topic: 分析主题
            crawled_data: 爬虫数据
            insight_result: 洞察结果
            report: 最终报告
            
        Returns:
            是否保存成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO analysis_records 
                    (topic, crawled_data, insight_result, report)
                    VALUES (?, ?, ?, ?)
                ''', (topic, crawled_data, insight_result, report))
                conn.commit()
                logger.info(f"分析记录已保存到数据库: {topic}")
                return True
        except Exception as e:
            logger.error(f"保存分析记录失败: {e}")
            return False
    
    def save_crawled_data(self, topic: str, data_list: List[Dict[str, Any]]) -> bool:
        """
        保存爬虫数据
        
        Args:
            topic: 主题
            data_list: 爬虫数据列表
            
        Returns:
            是否保存成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for item in data_list:
                    cursor.execute('''
                        INSERT INTO crawled_data (topic, content, likes, comments)
                        VALUES (?, ?, ?, ?)
                    ''', (topic, item.get("content", ""), 
                          item.get("likes", 0), item.get("comments", 0)))
                conn.commit()
                logger.info(f"爬虫数据已保存到数据库: {topic}")
                return True
        except Exception as e:
            logger.error(f"保存爬虫数据失败: {e}")
            return False
    
    def get_analysis_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取分析历史记录
        
        Args:
            limit: 限制返回记录数
            
        Returns:
            历史记录列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, topic, created_at FROM analysis_records 
                    ORDER BY created_at DESC LIMIT ?
                ''', (limit,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"获取分析历史记录失败: {e}")
            return []
    
    def get_analysis_record(self, record_id: int) -> Dict[str, Any]:
        """
        获取特定分析记录的详细信息
        
        Args:
            record_id: 记录ID
            
        Returns:
            记录详细信息
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM analysis_records WHERE id = ?
                ''', (record_id,))
                row = cursor.fetchone()
                return dict(row) if row else {}
        except Exception as e:
            logger.error(f"获取分析记录详情失败: {e}")
            return {}

# 全局数据库实例
_database_instance = None

def get_database() -> SimpleDatabase:
    """
    获取数据库实例（单例模式）
    
    Returns:
        SimpleDatabase实例
    """
    global _database_instance
    if _database_instance is None:
        _database_instance = SimpleDatabase()
    return _database_instance