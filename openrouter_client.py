import requests
import os
import time
from dotenv import load_dotenv


# 在文件开头加载.env文件
load_dotenv()

def call_llm(prompt, model="deepseek/deepseek-chat-v3-0324:free", temperature=0.7, max_retries=3, retry_delay=1):
    """
    调用OpenRouter LLM的简化函数，支持重试机制和温度参数
    
    Args:
        prompt (str): 用户提示词
        model (str): 模型名称，默认为deepseek/deepseek-chat-v3-0324
        temperature (float): 温度参数，控制输出的随机性，范围0-2，默认0.7
        max_retries (int): 最大重试次数，默认3次
        retry_delay (float): 重试间隔时间（秒），默认1秒
    
    Returns:
        str: LLM的回复内容
    """
    api_key = os.getenv('OPENROUTER_API_KEY')
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature
    }
    
    # 重试机制
    for attempt in range(max_retries + 1):
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            elif response.status_code == 429:  # 速率限制
                if attempt < max_retries:
                    wait_time = retry_delay * (2 ** attempt)  # 指数退避
                    print(f"遇到速率限制，等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
            elif response.status_code >= 500:  # 服务器错误
                if attempt < max_retries:
                    wait_time = retry_delay * (2 ** attempt)
                    print(f"服务器错误，等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
            
            # 其他错误直接抛出
            raise Exception(f"API调用失败: {response.status_code} - {response.text}")
            
        except requests.exceptions.RequestException as e:
            if attempt < max_retries:
                wait_time = retry_delay * (2 ** attempt)
                print(f"网络错误，等待 {wait_time} 秒后重试: {e}")
                time.sleep(wait_time)
                continue
            else:
                raise Exception(f"网络请求失败: {e}")
    
    raise Exception(f"重试 {max_retries} 次后仍然失败")