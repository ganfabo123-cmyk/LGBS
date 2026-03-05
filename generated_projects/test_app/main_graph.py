from langgraph import Graph
from state import AgentState
from module_a_graph import module_a_graph

# Create main graph
main_graph = Graph()

main_graph.add_node('module_a', module_a_graph)
