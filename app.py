#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化版BettaFish项目主应用
整合爬虫、本地LLM分析和报告生成功能
"""

import os
import sys
import argparse
from loguru import logger

from config import Settings
from simple_crawler import SimpleCrawler
from local_llm import LocalLLMClient
from analyzer import Analyzer
from reporter import Reporter

def setup_logging():
    """设置日志配置"""
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    logger.info("日志系统初始化完成")

def analyze_topic(topic: str, config: Settings):
    """
    分析指定主题
    
    Args:
        topic: 要分析的主题
        config: 配置对象
    """
    logger.info(f"开始分析主题: {topic}")
    
    # 初始化组件
    crawler = SimpleCrawler()
    llm_client = LocalLLMClient(config)
    analyzer = Analyzer(llm_client)
    reporter = Reporter(llm_client)
    
    # 1. 网络爬虫阶段
    logger.info("启动网络爬虫...")
    crawled_data = crawler.crawl_topic(topic)
    crawled_content = crawler.format_crawled_data(crawled_data)
    logger.info(f"网络爬虫完成，获取到 {len(crawled_data)} 条数据")
    
    # 2. 分析阶段
    logger.info("开始分析数据...")
    analysis_result = analyzer.analyze(topic, crawled_content)
    logger.info("数据分析完成")
    
    # 3. 生成报告阶段
    logger.info("生成分析报告...")
    report = reporter.generate(topic, crawled_content, analysis_result)
    logger.info("报告生成完成")
    
    # 输出结果
    print("\n" + "="*50)
    print(f"主题: {topic}")
    print("="*50)
    print("\n[网络爬虫结果]")
    print(crawled_content)
    print("\n[分析结果]")
    print(analysis_result)
    print("\n[分析报告]")
    print(report)
    print("="*50)
    
    logger.info(f"主题 {topic} 分析完成")

def main():
    """主函数"""
    setup_logging()
    
    parser = argparse.ArgumentParser(description="简化版BettaFish舆情分析工具")
    parser.add_argument("topic", nargs="?", help="要分析的主题")
    parser.add_argument("--config", help="配置文件路径")
    
    args = parser.parse_args()
    
    # 加载配置
    config = Settings()
    logger.info("配置加载完成")
    
    if args.topic:
        # 直接分析指定主题
        analyze_topic(args.topic, config)
    else:
        # 交互式模式
        print("欢迎使用简化版BettaFish舆情分析工具！")
        print("输入主题开始分析，输入 'quit' 或 'exit' 退出程序。")
        
        while True:
            try:
                topic = input("\n请输入要分析的主题: ").strip()
                if topic.lower() in ['quit', 'exit', '']:
                    print("感谢使用，再见！")
                    break
                
                analyze_topic(topic, config)
                
            except KeyboardInterrupt:
                print("\n\n程序被用户中断")
                break
            except Exception as e:
                logger.exception(f"分析过程中发生错误: {e}")
                print(f"发生错误: {e}")

if __name__ == "__main__":
    main()