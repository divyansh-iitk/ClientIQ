# import os
# import sys

# print("Executable:", sys.executable)
# print("CWD:", os.getcwd())
# print("sys.path:")
# for p in sys.path:
#     print(" ", p)



from langchain.messages import HumanMessage
import streamlit as st
from agentic.agents_state import AgentState
from agentic.graph import graph
    
    
st.title("Echo Bot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # response = f"Echo: {prompt}"
    state = AgentState(
    {"messages": [
        HumanMessage(content={prompt})
    ],
     "retry_count": 0})
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.write_stream(message_chunk.content async for message_chunk, metadata in graph.astream(state, stream_mode="messages",))
    # Add assistant response to chat history
    # st.session_state.messages.append({"role": "assistant", "content": response})