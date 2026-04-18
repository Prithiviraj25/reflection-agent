# from dotenv import load_dotenv
# load_dotenv()
# from typing import List,Sequence
# from langchain_core.messages import  BaseMessage, HumanMessage

# from langgraph.graph import END,MessageGraph
# from chains import generate_chain,reflection_chain

# REFLECT="reflect"
# GENERATE="generate"


# def generation_node(state:Sequence[BaseMessage]):
#     return generate_chain.invoke({"messages":state})

# def reflection_node(messages:Sequence[BaseMessage]) -> List[BaseMessage]:
#     critique = reflection_chain.invoke({"messages":messages})
#     return [HumanMessage(content=critique.content)]



# builder=MessageGraph()

# builder.add_node(GENERATE,generation_node)
# builder.add_node(REFLECT,reflection_node)
# builder.set_entry_point(GENERATE)


# # function to decide where to stop

# def should_continue(state: List[BaseMessage]):
#     if len(state) > 6:
#         return "stop_execution"
#     return "invoke_reflection"


# builder.add_conditional_edges(GENERATE,should_continue,{"stop_execution": END, "invoke_reflection": REFLECT})

# builder.add_edge(REFLECT,GENERATE)

# graph=builder.compile()

# print(graph.get_graph().draw_mermaid())

from dotenv import load_dotenv
from typing import Annotated, List, TypedDict
import os

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages


# these are the chains that were made earlier using langchain expressions 
from chains import generate_chain, reflection_chain

load_dotenv()
# below is the messagegraph class that is used to store the list of messages those are generated 

class MessageGraph(TypedDict):
    messages: Annotated[List[BaseMessage],add_messages]


REFLECT="reflect"
GENERATE="generate"


def generation_node(state:MessageGraph):
    return {"messages":[generate_chain.invoke({"messages":state["messages"]})]}

def reflection_node(state:MessageGraph):
    critique=reflection_chain.invoke({"messages":state["messages"]})
    return {"messages":[HumanMessage(content=critique.content)]}


def make_graph():
    # this is how we define the graph 
    builder=StateGraph(state_schema=MessageGraph)

    # this is how we add the nodes of the graph
    builder.add_node(GENERATE,generation_node)
    builder.add_node(REFLECT,reflection_node)

    # this is how we set the entry point of the graph
    builder.set_entry_point(GENERATE)


    # lets define a function to be used by a conditional edge
    # it returns a string  
    def should_continue(state:MessageGraph) -> str:
        if len(state["messages"]) > 3:  # also this conditions can we ultimately decided by anothe llm call 
            return "stop_execution"
        return "invoke_reflection"


    #this is how we add the edges of the graph

    builder.add_conditional_edges(GENERATE,should_continue,{"stop_execution": END, "invoke_reflection": REFLECT}) # third arg here is arg map

    builder.add_edge(REFLECT,GENERATE)

    return builder.compile()

def see_graph():
    graph=make_graph()
    print(graph.get_graph().draw_mermaid())

if __name__=="__main__":
    print("Learning Reflection Agent with LangGraph!")
    input_tweet=HumanMessage(content='''
                Make this tweet better:"
                @LangChainAI
                - newly Tool Calling feature is seriously underrated.
                After a long wait, it's here- making the implementation of agents across different models with function calling
                Made a video covering their newest blog post
                ''')
    
    graph=make_graph()
    
    response = graph.invoke({
    "messages": [input_tweet]
})