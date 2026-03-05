from typing import TypedDict, Any, Annotated
import operator

class AgentState(TypedDict):
    """全局状态定义"""
    user_query: str
    intermediate_result: str
    tool_result: str
    final_report: str
