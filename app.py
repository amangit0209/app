import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

st.title("📊 Screener.in Financial Data Scraper")

symbols_input = st.text_area("Enter Company Symbols (comma separated or one per line):")

excel_filename = "Screener_Financials.xlsx"

if st.button("Scrape and Download"):
    if symbols_input.strip():
        symbols = [s.strip().upper() for s in symbols_input.replace(',', '\n').split('\n') if s.strip()]
        st.write(f"Found {len(symbols)} symbols to process.")

        all_data = []

        for idx, symbol in enumerate(symbols, 1):
            st.info(f"🔄 Processing ({idx}/{len(symbols)}): {symbol}")
            try:
                url = f"https://www.screener.in/company/{symbol}/consolidated/"
                headers = {"User-Agent": "Mozilla/5.0"}
                response = requests.get(url, headers=headers)

                if response.status_code != 200:
                    st.warning(f"⚠️ Failed to fetch page for {symbol}. Skipping.")
                    continue

                soup = BeautifulSoup(response.text, "html.parser")

                company_name_tag = soup.find("h1")
                company_name = company_name_tag.text.strip() if company_name_tag else symbol

                table = soup.find("table", {"class": "ranges-table"})
                if not table:
                    st.warning(f"⚠️ No financials table found for {symbol}. Skipping.")
                    continue

                rows = table.find_all("tr")
                financial_data = {"Company Name": company_name}

                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) > 1:
                        metric_name = cols[0].text.strip()
                        latest_value = cols[1].text.strip()
                        financial_data[metric_name] = latest_value

                all_data.append(financial_data)

            except Exception as e:
                st.error(f"Error processing {symbol}: {e}")

        if all_data:
            df = pd.DataFrame(all_data)
            df.to_excel(excel_filename, index=False)

            st.success(f"✅ Scraped {len(all_data)} companies successfully!")

            with open(excel_filename, "rb") as file:
                st.download_button(
                    label="📥 Download Excel File",
                    data=file,
                    file_name=excel_filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.warning("No data to save!")

    else:
        st.warning("Please enter at least one symbol.")
