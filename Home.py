import streamlit as st

# Set page configuration
st.set_page_config(page_title="BSE Scraper App Selector", page_icon="📈", layout="centered")

# Main Title
st.title("📊 Welcome to the BSE Scraper Dashboard")


st.markdown("---")


st.markdown("""
Welcome to the **BSE Scraper Dashboard** — your one-stop tool for accessing company financial data from the Bombay Stock Exchange.

Use the sidebar to choose your desired analysis mode:
""")

# Styled navigation instructions
st.markdown("""
### 🔍 Navigation Options:
- 🗓️ **Quarterly** — Dive into recent quarterly financial data.
- 📅 **Annual** — Explore yearly financial performance trends.
""")

# Footer note or welcome tip
st.info("Tip: Use the sidebar on the left to begin. Happy analyzing! 📈")
