import streamlit as st
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from apikey import openai_api_key

def run_search_tool():
    st.title("📍 Advanced Review Search")
    
    reviews = [
        "Pizza Place: Great thin crust. Wood-fired oven. Expensive.",
        "Coffee Corner: Best cold brew. Good Wi-Fi. Mid-range.",
        "Sushi Spot: Daily imports from Japan. Very fresh. Expensive.",
        "Burger Joint: Casual family vibe. Wagyu beef. Affordable.",
        "Taco Truck: Best street tacos. Open late (3 AM). Budget friendly."
    ]

    if 'vector_store' not in st.session_state:
        if not openai_api_key:
            st.warning("Please provide an API key to continue.")
            return
        embeds = OpenAIEmbeddings(openai_api_key=openai_api_key)
        st.session_state.vector_store = Chroma.from_texts(reviews, embeds)

    llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=openai_api_key, temperature=0)
    
    retriever = st.session_state.vector_store.as_retriever(search_kwargs={"k": 3})

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a local guide. Answer using ONLY the following context: {context}"),
        ("human", "{input}"),
    ])
    
    doc_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, doc_chain)

    query = st.text_input("Ask about local spots (e.g., 'Where can I work late?' or 'Cheap food?'):")
    
    if st.button("Search") and query:
        with st.spinner("Analyzing reviews..."):
            res = rag_chain.invoke({"input": query})
            st.divider()
            st.write(res["answer"])

if __name__ == "__main__":
    run_search_tool()