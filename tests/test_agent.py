from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from personal_assistant.agent import MaxStepsExceededError, run_tool_loop
import pytest

class FakeLLM:
    """Returns scripted replies, one per invoke()."""
    
    def __init__(self, replies:list[AIMessage])->None:
        self._replies = list(replies)
        
    def bind_tools(self, tools):
        return self
    
    def invoke(self, messages):
        return self._replies.pop(0)
    
@tool
def add(a:int,b:int)->int:
    """Add two integers."""
    return a+b

def tool_request(name:str, args:dict)->AIMessage:
    return AIMessage(content="", tool_calls=[{"name" : name , "args" : args, "id" : "call-1"}])

def test_runs_tool_then_return_final_answer()->None:
    llm = FakeLLM([
        tool_request("add", {"a":5 , "b":3}),
        AIMessage(content="The answer is 8.")
    ])
    
    result = run_tool_loop(llm,[add],[HumanMessage("5 plus 3")])
    
    assert isinstance(result[2],ToolMessage)
    assert result[2].content == "8"
    assert result[-1].content == "The answer is 8."
    
def test_unknown_tool_becomes_error_message()->None:
    llm = FakeLLM([
        tool_request("nonexistent", {"a":5 , "b":3}),
        AIMessage(content="The tool doesnot exits")
    ])
        
    result = run_tool_loop(llm,[add],[HumanMessage("5 plus 3")])
    
    assert isinstance(result[2], ToolMessage)
    assert "does not exist" in result[2].content
    
def test_step_limit_raises()->None:
    llm = FakeLLM([
        tool_request("add", {"a": 5, "b": 3}),
        tool_request("add", {"a": 5, "b": 3}),
        tool_request("add", {"a": 5, "b": 3}),
        AIMessage(content="The answer is 8.")
    ])
    
    with pytest.raises(MaxStepsExceededError):
        run_tool_loop(llm,[add],[HumanMessage("5 plus 3")],2)
        
@tool
def explode(a: int) -> int:
    """Always fails."""
    raise ValueError("boom")


def test_tool_failure_becomes_message() -> None:
    llm = FakeLLM([
        tool_request("explode", {"a": 1}),
        AIMessage(content="Sorry, the tool failed."),
    ])

    result = run_tool_loop(llm, [explode], [HumanMessage("do it")])

    assert isinstance(result[2], ToolMessage)
    assert "failed" in result[2].content
    assert "boom" in result[2].content
    