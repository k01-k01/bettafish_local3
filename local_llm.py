"""
本地LLM客户端，用于替代各种在线API调用
"""

import json
import os
import warnings
from typing import Dict, Any, List, Optional
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from loguru import logger
from config import Settings

# 设置环境变量以禁用transformers库的警告
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
# 过滤掉特定的警告信息
warnings.filterwarnings("ignore")

class LocalLLMClient:
    """本地LLM客户端"""
    
    def __init__(self, config: Settings):
        """
        初始化本地LLM客户端
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.model_path = config.LOCAL_LLM_PATH
        
        logger.info(f"正在加载本地模型: {self.model_path}")
        try:
            # 加载tokenizer和model
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path, 
                trust_remote_code=True,
                padding_side='left'  # 设置padding_side为left
            )
            # 为tokenizer设置pad_token
            if self.tokenizer.pad_token is None:
                if self.tokenizer.unk_token is not None:
                    self.tokenizer.pad_token = self.tokenizer.unk_token
                elif self.tokenizer.eos_token is not None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                else:
                    self.tokenizer.add_special_tokens({'pad_token': '[PAD]'})
            
            # 加载模型，使用更多优化参数减少内存使用
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto",
                trust_remote_code=True,
                low_cpu_mem_usage=True,  # 减少CPU内存使用
                load_in_8bit=True if torch.cuda.is_available() else False,  # 如果有GPU则使用8位量化
            )
            
            logger.info("本地模型加载成功")
        except Exception as e:
            logger.error(f"本地模型加载失败: {e}")
            raise
    
    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        模拟OpenAI的chat.completion接口
        
        Args:
            messages: 对话历史消息列表
            
        Returns:
            模拟的OpenAI响应格式
        """
        try:
            # 构造prompt
            prompt = self._build_prompt(messages)
            
            # 编码输入，包含attention_mask
            inputs = self.tokenizer(
                prompt, 
                return_tensors="pt", 
                padding=True,
                truncation=True,
                max_length=512
            ).to(self.model.device)
            
            # 确保有attention_mask
            if 'attention_mask' not in inputs:
                inputs['attention_mask'] = torch.ones_like(inputs['input_ids'])
            
            # 设置默认参数和覆盖特定参数，优化处理速度
            generation_kwargs = {
                "max_new_tokens": kwargs.get("max_new_tokens", self.config.LLM_MAX_TOKENS),
                "do_sample": kwargs.get("do_sample", self.config.LLM_DO_SAMPLE),
                "temperature": kwargs.get("temperature", self.config.LLM_TEMPERATURE),
                "pad_token_id": self.tokenizer.pad_token_id,
                "eos_token_id": self.tokenizer.eos_token_id
            }
            
            logger.debug(f"模型生成参数: {generation_kwargs}")
            
            # 生成回复，使用更高效的参数
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    **generation_kwargs
                )
            
            # 解码输出
            response_text = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
            
            return {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": response_text
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": inputs.input_ids.shape[1],
                    "completion_tokens": outputs.shape[1] - inputs.input_ids.shape[1],
                    "total_tokens": outputs.shape[1]
                }
            }
        except Exception as e:
            logger.error(f"本地模型调用失败: {e}")
            return {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": f"抱歉，处理您的请求时出现了错误: {str(e)}"
                    },
                    "finish_reason": "error"
                }],
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            }
    
    def _build_prompt(self, messages: List[Dict[str, str]]) -> str:
        """
        构建prompt字符串
        
        Args:
            messages: 消息列表
            
        Returns:
            构建好的prompt字符串
        """
        # 只使用最新的用户消息和系统消息，避免历史对话干扰
        system_message = ""
        user_message = ""
        
        for message in messages:
            role = message.get("role", "")
            content = message.get("content", "")
            if role == "system":
                system_message = content
            elif role == "user":
                user_message = content
        
        # 构建简洁的prompt，避免引入无关上下文
        prompt = f"<|system|>\n{system_message}<|end|>\n<|user|>\n{user_message}<|end|>\n<|assistant|>\n"
        return prompt

# 全局实例
local_llm_client: Optional[LocalLLMClient] = None

def get_local_llm_client(config: Settings) -> LocalLLMClient:
    """
    获取本地LLM客户端单例
    
    Args:
        config: 配置对象
        
    Returns:
        LocalLLMClient实例
    """
    global local_llm_client
    if local_llm_client is None:
        local_llm_client = LocalLLMClient(config)
    return local_llm_client