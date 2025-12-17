"""
简化版BettaFish Web应用
提供基于Flask的Web界面
"""

import os
import json
from flask import Flask, render_template, request, jsonify
from loguru import logger

from config import Settings
from simple_crawler import SimpleCrawler
from local_llm import get_local_llm_client
from analyzer import Analyzer
from reporter import Reporter
from db import get_database

# 创建Flask应用
app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')

# 全局变量存储引擎实例
config = None
database = None

def initialize_app():
    """初始化应用"""
    global config, database
    
    if config is None:
        config = Settings()
    
    if database is None:
        database = get_database()
        
    logger.info("应用初始化完成")

@app.route('/')
def index():
    """主页路由"""
    initialize_app()
    history = database.get_analysis_history()
    return render_template('index.html', history=history)

@app.route('/analyze', methods=['POST'])
def analyze():
    """分析请求处理"""
    logger.info("收到新的分析请求")
    
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            logger.warning("请求中没有JSON数据")
            return jsonify({
                'status': 'error',
                'message': '请求格式错误，需要JSON数据'
            }), 400
            
        topic = data.get('topic', '').strip()
        
        if not topic:
            logger.warning("未提供分析主题")
            return jsonify({
                'status': 'error',
                'message': '未提供分析主题'
            }), 400
        
        logger.info(f"开始分析主题: {topic}")
        
        # 初始化组件
        initialize_app()
        crawler = SimpleCrawler()
        llm_client = get_local_llm_client(config)
        analyzer = Analyzer(llm_client)
        reporter = Reporter(llm_client)
        
        # 第一步：网络爬虫
        logger.info("启动网络爬虫...")
        crawled_data = crawler.crawl_topic(topic)
        crawled_content = crawler.format_crawled_data(crawled_data)
        logger.info(f"网络爬虫获取到 {len(crawled_data)} 条相关数据")
        
        # 保存爬虫数据到数据库
        try:
            database.save_crawled_data(topic, crawled_data)
            logger.info("爬虫数据已保存到数据库")
        except Exception as e:
            logger.exception(f"保存爬虫数据到数据库时发生错误: {str(e)}")
        
        # 第二步：洞察分析
        logger.info("执行洞察分析...")
        try:
            insight_result = analyzer.analyze(topic, crawled_content)
            logger.info("洞察分析成功完成")
        except Exception as e:
            logger.exception(f"洞察分析过程中发生错误: {str(e)}")
            return jsonify({'status': 'error', 'message': f'洞察分析失败: {str(e)}'}), 500

        # 第三步：生成报告
        logger.info("生成综合报告...")
        try:
            report_result = reporter.generate(topic, crawled_content, insight_result)
            logger.info("报告生成成功")
        except Exception as e:
            logger.exception(f"报告生成过程中发生错误: {str(e)}")
            return jsonify({'status': 'error', 'message': f'报告生成失败: {str(e)}'}), 500
        
        # 保存分析记录到数据库
        try:
            database.save_analysis_record(
                topic, 
                crawled_content, 
                insight_result, 
                report_result
            )
            logger.info("分析记录已保存到数据库")
        except Exception as e:
            logger.exception(f"保存分析记录到数据库时发生错误: {str(e)}")
        
        # 返回成功响应
        return jsonify({
            'status': 'success',
            'topic': topic,
            'crawled_content': crawled_content,
            'insight_result': insight_result,
            'report': report_result
        })
        
    except Exception as e:
        logger.exception(f"分析请求处理过程中发生未预期的错误: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'分析请求处理失败: {str(e)}'
        }), 500

@app.route('/history/<int:record_id>')
def get_history_record(record_id):
    """获取历史记录详情"""
    try:
        initialize_app()
        record = database.get_analysis_record(record_id)
        if not record:
            return jsonify({
                'status': 'error',
                'message': '未找到指定的历史记录'
            }), 404
            
        return jsonify({
            'status': 'success',
            'record': record
        })
        
    except Exception as e:
        logger.exception(f"获取历史记录详情时发生错误: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'获取历史记录详情失败: {str(e)}'
        }), 500

if __name__ == '__main__':
    initialize_app()
    app.run(host='0.0.0.0', port=5000, debug=True)