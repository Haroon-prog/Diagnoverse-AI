# complete graph 

from langgraph.graph import StateGraph,START,END
from agents.extraction_agent import extraction_agent
from state.state import AgentState

graph = StateGraph(AgentState)

# add node 
graph.add_node('extraction_agent',extraction_agent)

# add edge
graph.add_edge(START,'extraction_agent') 
graph.add_edge('extraction_agent',END) 

# compile
workflow = graph.compile()

print(workflow)

# print(type(extraction_agent))

final_state = workflow.invoke(
    {
    "input_type": "pdf",
    'input_data': 'data/sample_pdf2.pdf',
    'file_name': 'sample_pdf2'}
    )

print(final_state,end="\n\n\n\t\n")
print(final_state['extracted_text'],end="\n\n\n\t\n")
print(final_state['medications'],end="\n\n\n\t\n")
print(final_state['conditions'],end="\n\n\n\t\n")
print(final_state['lab_values'],end="\n\n\n\t\n")

