import streamlit as st

st.set_page_config(page_title="BSE Scraper App Selector", page_icon="📈")

st.title("📊 Welcome to BSE Scraper Dashboard")
st.markdown("""
Use the sidebar to navigate to one of the scraper tools:
- **Quarterly Scraper** for quarterly financial data
- **Annual Scraper** for yearly trends
""")