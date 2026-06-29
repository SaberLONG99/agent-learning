import os


# 当前项目目录，也就是这个 config.py 所在的目录
CURRENT_DIR = os.path.dirname(__file__)

# 长期记忆文件：保存用户明确要求 Agent 记住的信息
MEMORY_FILE = os.path.join(CURRENT_DIR, "memory.json")

# 知识库目录：里面可以放多个 .txt 文件
KNOWLEDGE_DIR = os.path.join(CURRENT_DIR, "knowledge")

# 日志文件：记录用户输入、工具调用、工具结果、助手回答
LOG_FILE = os.path.join(CURRENT_DIR, "agent.log")

# 每次用户提问，Agent 最多行动 5 次，防止无限循环
MAX_AGENT_STEPS = 5
