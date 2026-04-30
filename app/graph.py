# complete graph 

from langgraph.graph import StateGraph,START,END
from agents.extraction_agent import extraction_agent
from agents.query_gen_agent import query_generator_agent
from agents.summary_agent import summary_agent
from agents.drug_checker_agent import check_medics,drug_checker_agent
from state.state import AgentState

graph = StateGraph(AgentState)

# add node 
graph.add_node('extraction_agent',extraction_agent)
graph.add_node('query_generator_agent',query_generator_agent)
graph.add_node('summary_agent',summary_agent)
graph.add_node('drug_checker_agent',drug_checker_agent)


# add edge
graph.add_edge(START,'extraction_agent') 

graph.add_conditional_edges(
    'extraction_agent',
    check_medics,
    {
        "drug_checker_agent": "drug_checker_agent",
        "query_generator_agent": "query_generator_agent"
    }
)

graph.add_edge('drug_checker_agent','query_generator_agent')
# graph.add_edge('extraction_agent','query_generator_agent')
graph.add_edge('query_generator_agent','summary_agent')
graph.add_edge('summary_agent',END) 

# compile
workflow = graph.compile()

print(workflow)

# print(type(extraction_agent))

final_state = workflow.invoke(
    {
    "input_type": "pdf",
    'input_data': 'input_data/sample_pdf2.pdf',
    'file_name': 'sample_pdf2',
    
    "medications": [
        {"name": "Crocin"},
        {"name": "Metformin"},
        {"name": "Telma-AM"}
    ]}
    )

print(final_state,end="\n\n\n\t\n")
print(final_state['extracted_text'],end="\n\n\n\t\n")
print(final_state['medications'],end="\n\n\n\t\n")
print(final_state['conditions'],end="\n\n\n\t\n")
print(final_state['lab_values'],end="\n\n\n\t\n")

print(f"---------------rag-context-------------\n{final_state['rag_context']}\n\n\n")
print("---------------end of rag-context-------------\n\n\n")

print (f"complete final state : \n\n\n{final_state}\n\n\t\n")


print(f" ----- IMPORTANT QUESTIONS TO ASK -------\n\n\n\t\t\n{final_state['doctor_questions']} ")

print(f"------ SUMMARY ---------\n\n\n\t{final_state['summary']}")

print(f"-------------drug checker values \n\n\n\n\t{final_state['side_effects']},{final_state['drug_warnings']},{final_state['drug_interactions']}")



