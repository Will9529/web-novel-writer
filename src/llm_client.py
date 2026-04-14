"""
阿里云通义千问 API 客户端
"""
import requests
import hashlib
import hmac
import base64
import time
from datetime import datetime
from typing import Optional, Dict, Any


class AliyunLLMClient:
    """阿里云通义千问 LLM 客户端"""
    
    def __init__(self, api_key: str, model: str = "qwen-plus"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    
    def generate(self, prompt: str, system_prompt: str = "", max_tokens: int = 3000, temperature: float = 0.7) -> str:
        """
        生成文本
        
        Args:
            prompt: 用户输入
            system_prompt: 系统提示词
            max_tokens: 最大生成 token 数
            temperature: 温度参数 (0-1)
        
        Returns:
            生成的文本
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "input": {
                "messages": messages
            },
            "parameters": {
                "max_tokens": max_tokens,
                "temperature": temperature,
                "result_format": "message"
            }
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            if result.get("output") and result["output"].get("choices"):
                return result["output"]["choices"][0]["message"]["content"]
            else:
                return f"[生成失败] {result}"
                
        except requests.exceptions.RequestException as e:
            return f"[API 请求错误] {str(e)}"
    
    def generate_with_retry(self, prompt: str, system_prompt: str = "", max_retries: int = 3) -> str:
        """带重试的生成"""
        for i in range(max_retries):
            result = self.generate(prompt, system_prompt)
            if not result.startswith("["):
                return result
            if i < max_retries - 1:
                time.sleep(2 ** i)  # 指数退避
        return result
