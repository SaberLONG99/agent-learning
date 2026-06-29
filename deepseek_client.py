import os

from openai import OpenAI


# 创建 DeepSeek 客户端
# DeepSeek 兼容 OpenAI SDK，所以这里仍然使用 OpenAI 这个类
client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)
