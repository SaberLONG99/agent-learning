import json

from config import MAX_AGENT_STEPS
from deepseek_client import client
from logger_utils import write_log
from prompts import create_messages
from tool_functions import execute_tool
from tool_schemas import tools


def chat():
    """
    Agent 主循环。

    这个函数负责：
    1. 接收用户输入
    2. 请求大模型
    3. 执行工具调用
    4. 把工具结果交回模型
    5. 打印最终回答
    """

    # 创建新的对话历史
    messages = create_messages()

    # 外层循环：一轮一轮接收用户输入
    while True:
        user_input = input("\n你：").strip()

        # 用户输入 exit 或 quit 时退出程序
        if user_input.lower() in {"exit", "quit"}:
            print("对话结束")
            break

        # 如果用户什么都没输入，就重新等待输入
        if not user_input:
            continue

        # 把用户消息加入对话历史
        messages.append(
            {
                "role": "user",
                "content": user_input
            }
        )

        # 写入日志，方便之后排查 Agent 行为
        write_log(f"用户输入：{user_input}")

        # 本轮对话的行动次数
        step_count = 0

        # 本轮知识库搜索失败次数
        knowledge_miss_count = 0

        # 内层循环：Agent 可以多次调用工具
        while step_count < MAX_AGENT_STEPS:
            step_count += 1
            print(f"\n[Agent 步骤 {step_count}/{MAX_AGENT_STEPS}]")

            try:
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=messages,
                    tools=tools
                )
            except Exception as e:
                print(f"\nAPI 请求失败：{e}")
                write_log(f"API 请求失败：{e}")
                break

            # 取出模型返回的 assistant 消息
            assistant_message = response.choices[0].message

            # assistant 消息必须放进 messages
            # 如果它里面有 tool_calls，后面必须补对应的 tool 消息
            messages.append(assistant_message)

            # 如果模型没有调用工具，说明已经给出最终回答
            if not assistant_message.tool_calls:
                print(f"\n助手：{assistant_message.content}")
                write_log(f"助手回答：{assistant_message.content}")
                break

            # 是否需要停止本轮 Agent 行动
            should_stop = False

            # 遍历模型要求调用的所有工具
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments or "{}")

                print(f"\n[调用工具] {function_name}, 参数：{arguments}")
                write_log(f"[调用工具] {function_name}, 参数：{arguments}")

                try:
                    tool_result = execute_tool(function_name, arguments)
                except Exception as e:
                    tool_result = f"工具执行失败：{e}"
                    write_log(f"[工具执行失败] {function_name}：{e}")

                tool_result = str(tool_result)
                print(f"[工具结果] {tool_result}")
                write_log(f"[工具结果] {tool_result}")

                # 知识库搜索失败时，允许模型换关键词再试一次
                if (
                    function_name == "search_knowledge"
                    and "没有在知识库中找到相关内容" in tool_result
                ):
                    knowledge_miss_count += 1

                    # 第一次没找到：告诉模型换一个更短的关键词
                    if knowledge_miss_count < 2:
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": (
                                    "没有在知识库中找到相关内容。"
                                    "请换一个更短、更核心的关键词重新调用 search_knowledge。"
                                )
                            }
                        )
                        continue

                    # 第二次没找到：也必须先补 tool 消息，避免 API 报错
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": "没有在知识库中找到相关内容。"
                        }
                    )

                    print("\n助手：知识库中没有找到相关资料。")
                    write_log("助手回答：知识库中没有找到相关资料。")

                    should_stop = True
                    break

                # 正常工具结果追加到 messages
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result
                    }
                )

            # 如果代码判断必须停止，就跳出内层 while
            if should_stop:
                break


if __name__ == "__main__":
    chat()
