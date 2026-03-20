import requests
from typing import List, Dict
import config

class LLMClient:
    def __init__(self, api_base: str = None, model: str = None):
        self.api_base = api_base or config.API_BASE_URL
        self.model = model or config.MODEL_NAME
        self.chat_endpoint = f"{self.api_base}/chat/completions"
        self.models_endpoint = f"{self.api_base}/models"

    def check_connection(self) -> bool:
        try:
            response = requests.get(self.models_endpoint, timeout=5)
            return response.status_code == 200
        except:
            return False

    def get_available_models(self) -> List[str]:
        try:
            response = requests.get(self.models_endpoint, timeout=5)
            if response.status_code == 200:
                models = response.json()
                return [m['id'] for m in models.get('data', [])]
        except Exception as e:
            print(f"获取模型列表失败: {e}")
        return []

    def generate(self, messages: List[Dict], temperature: float = None,
                 max_tokens: int = None) -> str:
        temperature = temperature or config.TEMPERATURE
        max_tokens = max_tokens or config.MAX_TOKENS

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }

        try:
            response = requests.post(self.chat_endpoint, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except requests.exceptions.RequestException as e:
            return f"API请求失败: {e}"
        except KeyError as e:
            return f"响应解析失败: {e}"

    def chat(self, user_input: str, system_prompt: str = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_input})
        return self.generate(messages)
