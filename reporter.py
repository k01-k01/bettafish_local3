"""
报告生成器模块
使用本地LLM生成舆情分析报告
"""

from typing import Dict, Any
from loguru import logger
from local_llm import LocalLLMClient
import re

class Reporter:
    """报告生成器"""
    
    def __init__(self, llm_client: LocalLLMClient):
        """
        初始化报告生成器
        
        Args:
            llm_client: 本地LLM客户端
        """
        self.llm_client = llm_client
        logger.info("报告生成器初始化完成")
    
    def generate(self, topic: str, crawled_content: str, analysis_result: str) -> str:
        """
        生成舆情分析报告
        
        Args:
            topic: 报告主题
            crawled_content: 爬取的内容
            analysis_result: 分析结果
            
        Returns:
            生成的报告
        """
        logger.info(f"开始生成报告: {topic}")
        
        # 构造报告生成提示词，明确要求输出格式
        messages = [
            {
                "role": "system",
                "content": (
                    "你是一位专业的舆情分析报告撰写专家，请根据提供的材料生成一份结构清晰、内容详实的舆情分析报告。\n"
                    "严格按照以下格式输出：\n"
                    "热点话题：[简述热点话题]\n"
                    "主要观点：[列出主要观点]\n"
                    "公众情绪：[描述公众情绪]\n"
                    "影响程度：[评估影响程度]\n"
                    "应对策略：[提出应对策略]\n"
                    "建议措施：[给出具体建议]\n"
                    "注意：只基于提供的材料生成报告，不要添加任何额外信息，不要回答其他问题，不要引入任何外部对话或内容。"
                )
            },
            {
                "role": "user",
                "content": f"""请基于以下信息生成一份关于"{topic}"的舆情分析报告:

网络爬取内容:
{crawled_content}

分析结果:
{analysis_result}

要求:
1. 报告必须包含以下部分：热点话题、主要观点、公众情绪、影响程度、应对策略、建议措施
2. 每个部分用简练的语言表述，避免使用markdown格式
3. 不要使用特殊符号如#、*等
4. 总字数控制在500字以内
5. 使用中文撰写
6. 严格基于提供的材料，不要添加任何额外信息
7. 只输出报告内容，不要包含任何其他内容
"""
            }
        ]
        
        # 调用本地LLM生成报告
        response = self.llm_client.chat_completion(messages)
        
        if response["choices"][0]["finish_reason"] == "error":
            error_msg = response["choices"][0]["message"]["content"]
            logger.error(f"报告生成过程中发生错误: {error_msg}")
            return f"报告生成过程中发生错误: {error_msg}"
        
        report = response["choices"][0]["message"]["content"]
        logger.info(f"报告生成完成: {topic}")
        
        return report