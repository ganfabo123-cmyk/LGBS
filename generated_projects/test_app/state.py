from typing import TypedDict, Any
import operator

class AgentState(TypedDict):
    user_query: str
    intermediate_result: str
    tool_result: str
    final_report: str

# Reducers
