from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, ToolMessage
from langchain_core.tools import BaseTool


class MaxStepsExceededError(Exception):
    """The model still wanted tools after the step limit"""


def run_tool_loop(
    llm: BaseChatModel, tools: list[BaseTool], messages: list[BaseMessage], max_steps: int = 5
) -> list[BaseMessage]:
    """Run the model until it stops requesting tools. Return the full conversation"""

    messages = list(messages)
    tools_by_name = {t.name: t for t in tools}
    llm_with_tools = llm.bind_tools(tools)

    for _ in range(max_steps):
        reply = llm_with_tools.invoke(messages)
        messages.append(reply)
        if not reply.tool_calls:
            break

        for call in reply.tool_calls:
            tool_fn = tools_by_name.get(call["name"])

            if tool_fn is None:
                result = (
                    f"Tool '{call['name']}' does not exist. "
                    f"Available tools: {', '.join(tools_by_name)}"
                )
            else:
                try:
                    result = tool_fn.invoke(call["args"])
                except Exception as exc:
                    result = f"Tool '{call['name']}' failed: {exc}"

            messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))

    else:
        raise MaxStepsExceededError(f"Stopped: model still wanted tools after {max_steps} steps")

    return messages
