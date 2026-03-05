from langgraph import SubGraph
from state import AgentState

# Create subgraph for module_a
module_a_graph = SubGraph(name="module_a")

def node1(state: AgentState) -> AgentState:
    # 
    user_query = state.get('user_query')
    # LLM logic here
    result = "some result"
    state['intermediate_result'] = result
    return state

def node2(state: AgentState) -> AgentState:
    # 
    intermediate_result = state.get('intermediate_result')
    # Tool logic here
    result = node2(intermediate_result)
    state['tool_result'] = result
    return state

module_a_graph.add_node('node1', node1)
module_a_graph.add_node('node2', node2)
module_a_graph.add_edge('node1', 'node2', condition=lambda state: result == 'success')
module_a_graph.add_edge('node2', 'END')
