import os

from config import KNOWLEDGE_DIR


def extract_keywords(query):
    """
    从用户问题中提取用于检索的关键词。

    :param query: 用户问题或模型给出的搜索词
    :return: 关键词列表
    """

    query_lower = query.lower()

    # 保存最终要用于搜索的关键词
    keywords = []

    # 常见无意义词，搜索时可以忽略
    stop_words = [
        "我的",
        "有哪些",
        "是什么",
        "是啥",
        "请问",
        "一下",
        "帮我",
        "查询",
        "搜索",
    ]

    # 英文或带空格的问题，先按空格切分
    for word in query_lower.split():
        word = word.strip()

        if not word:
            continue

        if word in stop_words:
            continue

        keywords.append(word)

    # 中文经常没有空格，所以手动识别一些常见关键词
    important_words = [
        "agent",
        "项目",
        "方向",
        "学习",
        "目标",
        "deepseek",
        "python",
        "知识库",
        "助手",
        "日报",
        "周报",
        "研究",
    ]

    for word in important_words:
        if word in query_lower and word not in keywords:
            keywords.append(word)

    # 如果没有提取出关键词，就用完整 query 兜底
    if not keywords:
        keywords = [query_lower]

    return keywords


def search_knowledge(query):
    """
    从 knowledge 文件夹中的多个 .txt 文件里按段落搜索相关内容。

    :param query: 用户的问题或关键词
    :return: 搜索到的相关知识段落
    """

    # 如果 knowledge 文件夹不存在，就告诉 Agent
    if not os.path.exists(KNOWLEDGE_DIR):
        return "知识库文件目录 knowledge 不存在。"

    # 先从问题中提取关键词
    keywords = extract_keywords(query)

    # 用来保存带分数的搜索结果
    scored_results = []

    # 遍历 knowledge 文件夹里的所有文件
    for filename in os.listdir(KNOWLEDGE_DIR):
        # 只处理 txt 文件
        if not filename.endswith(".txt"):
            continue

        # 拼出文件完整路径
        file_path = os.path.join(KNOWLEDGE_DIR, filename)

        # 如果不是普通文件，就跳过
        if not os.path.isfile(file_path):
            continue

        # 读取当前知识库文件
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        # 按空行切分段落
        paragraphs = content.split("\n\n")

        # 遍历每一个段落
        for paragraph_index, paragraph in enumerate(paragraphs, start=1):
            paragraph_text = paragraph.strip()

            # 空段落跳过
            if not paragraph_text:
                continue

            # 第一行作为标题，后面作为正文
            paragraph_lines = paragraph_text.splitlines()
            title = paragraph_lines[0].strip()
            body = "\n".join(paragraph_lines[1:]).strip()

            # 如果没有正文，就把标题也当成正文
            if not body:
                body = title

            # 用整个段落参与搜索，标题和正文都能命中
            paragraph_lower = paragraph_text.lower()

            # 计算当前段落命中了几个关键词
            score = 0
            for keyword in keywords:
                if keyword in paragraph_lower:
                    score += 1

            # 至少命中 1 个关键词，才算搜索结果
            if score > 0:
                scored_results.append(
                    {
                        "score": score,
                        "filename": filename,
                        "paragraph_index": paragraph_index,
                        "title": title,
                        "body": body,
                    }
                )

    # 没有任何结果时，返回固定文本，主程序会识别这句话
    if not scored_results:
        return "没有在知识库中找到相关内容。"

    # 按相关分数从高到低排序
    scored_results.sort(key=lambda item: item["score"], reverse=True)

    # 只取前 5 条，避免返回太多内容
    top_results = scored_results[:5]

    # 把结果整理成适合模型阅读和引用的格式
    result_texts = []

    for item in top_results:
        result_texts.append(
            f"来源：{item['filename']} 第{item['paragraph_index']}段\n"
            f"标题：{item['title']}\n"
            f"内容：{item['body']}"
        )

    return "\n\n".join(result_texts)
