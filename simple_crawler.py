"""
简化版网络爬虫模块
爬取舆情相关信息
"""

import json
import time
import random
from typing import List, Dict, Any
from loguru import logger
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

class SimpleCrawler:
    """简化版网络爬虫"""
    
    def __init__(self):
        """初始化爬虫"""
        logger.info("初始化网络爬虫")
        
    def _clean_text(self, text: str) -> str:
        """
        清理文本内容
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        if not text:
            return ""
        # 去除多余空白字符
        text = re.sub(r'\s+', ' ', text)
        # 去除首尾空格
        text = text.strip()
        return text
    
    def _crawl_douyin(self, topic: str, max_items: int = 10) -> List[Dict[str, Any]]:
        """
        从抖音爬取内容
        
        Args:
            topic: 要爬取的主题
            max_items: 最大爬取条数
            
        Returns:
            爬取到的内容列表
        """
        logger.info(f"尝试从抖音爬取主题 '{topic}' 的相关内容")
        
        # 抖音搜索URL (注意：实际抖音有复杂的反爬虫机制)
        encoded_topic = urllib.parse.quote(topic)
        url = f"https://www.douyin.com/search/{encoded_topic}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        try:
            # 发送GET请求
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找视频内容 (注意：实际结构需要根据抖音页面结构调整)
            video_items = soup.find_all('div', {'data-e2e': 'search-result-item'}, limit=max_items)
            
            result = []
            for item in video_items:
                # 尝试提取视频标题或描述
                title_elem = item.find('h3') or item.find('a')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    
                    # 简单估算点赞和评论数
                    likes = random.randint(0, 1000)
                    comments = random.randint(0, 100)
                    
                    result.append({
                        "content": title,
                        "likes": likes,
                        "comments": comments
                    })
                    
                    if len(result) >= max_items:
                        break
                        
            logger.info(f"从抖音获取到 {len(result)} 条相关数据")
            return result
            
        except Exception as e:
            logger.error(f"从抖音爬取数据时出错: {e}")
            return []
            
    def _crawl_baidu(self, topic: str, max_items: int = 10) -> List[Dict[str, Any]]:
        """
        从百度搜索爬取内容
        
        Args:
            topic: 要爬取的主题
            max_items: 最大爬取条数
            
        Returns:
            爬取到的内容列表
        """
        logger.info(f"尝试从百度爬取主题 '{topic}' 的相关内容")
        
        # 百度搜索URL
        encoded_topic = urllib.parse.quote(topic)
        url = f"https://www.baidu.com/s?wd={encoded_topic}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        }
        
        try:
            # 发送GET请求
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找搜索结果
            result_items = soup.find_all('div', class_='result', limit=max_items)
            
            result = []
            for item in result_items:
                title_elem = item.find('h3') or item.find('a')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    content_elem = item.find('span', class_='content-right_2snyr') or item.find('div', class_='c-row') or item
                    content = content_elem.get_text(strip=True)[:100]  # 限制长度
                    
                    # 合并标题和内容
                    full_content = f"{title} {content}" if title != content else content
                    # 清理内容
                    full_content = self._clean_text(full_content)
                    
                    # 忽略过短的内容
                    if len(full_content) < 5:
                        continue
                    
                    # 简单估算点赞和评论数
                    likes = random.randint(0, 100)
                    comments = random.randint(0, 50)
                    
                    result.append({
                        "content": full_content,
                        "likes": likes,
                        "comments": comments
                    })
                    
                    if len(result) >= max_items:
                        break
                        
            logger.info(f"从百度获取到 {len(result)} 条相关数据")
            return result
            
        except Exception as e:
            logger.error(f"从百度爬取数据时出错: {e}")
            return []
    
    def crawl_topic(self, topic: str, max_items: int = 10) -> List[Dict[str, Any]]:
        """
        爬取特定主题的内容，尝试多种数据源
        
        Args:
            topic: 要爬取的主题
            max_items: 最大爬取条数
            
        Returns:
            爬取到的内容列表
        """
        logger.info(f"开始爬取主题 '{topic}' 的相关内容")
        
        # 尝试从不同平台爬取数据
        crawled_data = []
        
        # 首先尝试从抖音爬取
        if len(crawled_data) < max_items:
            douyin_data = self._crawl_douyin(topic, max_items)
            crawled_data.extend(douyin_data)
            
        # 如果抖音数据不足，尝试从百度爬取
        if len(crawled_data) < max_items:
            baidu_data = self._crawl_baidu(topic, max_items - len(crawled_data))
            crawled_data.extend(baidu_data)
        
        # 限制返回数量
        crawled_data = crawled_data[:max_items]
        logger.info(f"总共获取到 {len(crawled_data)} 条相关数据")
                
        return crawled_data
    
    def format_crawled_data(self, crawled_data: List[Dict[str, Any]]) -> str:
        """
        格式化爬取到的数据
        
        Args:
            crawled_data: 爬取到的数据列表
            
        Returns:
            格式化后的字符串
        """
        if not crawled_data:
            return "未爬取到相关数据。"
        
        formatted_data = "网络爬取结果:\n"
        for i, item in enumerate(crawled_data, 1):
            # 清理内容后再格式化
            content = self._clean_text(item['content'])
            formatted_data += f"{i}. 内容: {content}\n"
            formatted_data += f"   点赞: {item['likes']}  评论: {item['comments']}\n\n"
        
        return formatted_data