import streamlit as st
from app import run_blog_gen
from search_tool import run_search_tool

# Page config must be the first Streamlit command, and only called once!
st.set_page_config(layout="wide", page_title="AI Multi-Tool Dashboard", page_icon="🛠️")

st.sidebar.title("🛠️ Project Hub")
project = st.sidebar.radio("Select a Project:", ["AI Blog Generator", "Review Search Tool"])

st.sidebar.divider()

if project == "AI Blog Generator":
    run_blog_gen()
else:
    run_search_tool()