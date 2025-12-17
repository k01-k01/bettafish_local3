"""
分析器模块
使用本地LLM对爬取的数据进行分析
"""

from typing import Dict, Any
from loguru import logger
from local_llm import LocalLLMClient

class Analyzer:
    """数据分析器"""
    
    def __init__(self, llm_client: LocalLLMClient):
        """
        初始化分析器
        
        Args:
            llm_client: 本地LLM客户端
        """
        self.llm_client = llm_client
        logger.info("数据分析器初始化完成")
    
    def analyze(self, topic: str, crawled_content: str) -> str:
        """
        分析指定主题的爬取内容
        
        Args:
            topic: 分析的主题
            crawled_content: 爬取的内容
            
        Returns:
            分析结果
        """
        logger.info(f"开始分析主题: {topic}")
        
        # 构造分析提示词，明确输出格式并严格限定范围
        messages = [
            {
                "role": "system",
                "content": (
                    "你是一位专业的舆情分析师，请根据提供的网络内容进行简明扼要的分析。\n"
                    "请严格按照以下格式输出：\n"
                    "主要观点：[总结主要观点，严格基于提供内容]\n"
                    "公众情绪：[总结公众情绪，严格基于提供内容]\n"
                    "注意：只分析提供的内容，不要添加任何额外信息，不要回答其他问题，不要引入任何外部对话或内容。"
                )
            },
            {
                "role": "user",
                "content": f"请分析以下关于'{topic}'的网络内容，总结主要观点和公众情绪:\n\n{crawled_content}\n\n请用中文回答，按照指定格式输出，总字数不超过200字。只输出分析结果，不要包含任何其他内容。"
            }
        ]
        
        # 调用本地LLM进行分析
        response = self.llm_client.chat_completion(messages)
        
        if response["choices"][0]["finish_reason"] == "error":
            error_msg = response["choices"][0]["message"]["content"]
            logger.error(f"分析过程中发生错误: {error_msg}")
            return f"分析过程中发生错误: {error_msg}"
        
        analysis_result = response["choices"][0]["message"]["content"]
        logger.info(f"主题分析完成: {topic}")
        
        return analysis_result