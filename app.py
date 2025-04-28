import streamlit as st
import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
import time

# Mapping and periods remain same
metric_mapping = {
    "Total Income": "Total Income",
    "Expenditure": "Expenditure",
    "Interest": "Interest",
    "PBDT": "PBDT",
    "Depreciation": "Depreciation",
    "PBT": "PBT",
    "Tax": "Tax",
    "Net Profit": "Net Profit",
    "Equity": "Equity",
    "OPM %": "OPM (%)",
    "NPM %": "NPM (%)"
}

time_periods = ["Dec-24", "Sep-24", "Jun-24", "Mar-24", "Dec-23", "FY 23-24"]

excel_filename = "Financials_Data_Filled.xlsx"

st.title("📊 BSE Financials Scraper (No Selenium Version)")

urls_input = st.text_area("Enter Financials Page URLs (one per line or comma separated):")

if st.button("Scrape All and Save"):
    if urls_input.strip():

        all_new_rows = []

        urls = [url.strip() for url in urls_input.replace(',', '\n').split('\n') if url.strip()]
        st.write(f"Found {len(urls)} URLs to process.")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }

        for idx, url in enumerate(urls, 1):
            st.info(f"🔄 Processing ({idx}/{len(urls)}): {url}")
            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'html.parser')

                # Find the table
                table = soup.find('table', {'ng-bind-html': 'trustAsHtml(reportData.QtlyinCr)'})

                if table is None:
                    st.warning(f"No financial table found for URL: {url}")
                    continue

                data = []
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    cols_text = [col.get_text(strip=True) for col in cols]
                    if any(cols_text):
                        data.append(cols_text)

                if not data:
                    st.warning(f"No data found in table for URL: {url}")
                    continue

                header = data[0]
                data_rows = data[1:]

                df = pd.DataFrame(data_rows, columns=header)

                # Extract company name from title
                company_name_tag = soup.find('title')
                company_name = company_name_tag.get_text(strip=True).split('|')[0].strip() if company_name_tag else "Unknown Company"

                new_row = {"Company Name": company_name}

                for metric, output_prefix in metric_mapping.items():
                    matching_row = df[df[header[0]].str.strip() == metric]

                    if not matching_row.empty:
                        for period in time_periods:
                            try:
                                value = matching_row.iloc[0][period]
                                if value != "":
                                    new_row[f"{output_prefix} ({period})"] = value
                                else:
                                    new_row[f"{output_prefix} ({period})"] = ""
                            except KeyError:
                                new_row[f"{output_prefix} ({period})"] = ""
                    else:
                        for period in time_periods:
                            new_row[f"{output_prefix} ({period})"] = ""

                all_new_rows.append(new_row)

            except Exception as e:
                st.error(f"Error processing URL: {url} → {e}")

        if all_new_rows:
            if os.path.exists(excel_filename):
                existing_df = pd.read_excel(excel_filename)
                updated_df = pd.concat([existing_df, pd.DataFrame(all_new_rows)], ignore_index=True)
            else:
                updated_df = pd.DataFrame(all_new_rows)

            updated_df.to_excel(excel_filename, index=False)
            st.success(f"✅ Saved {len(all_new_rows)} new entries successfully!")

            with open(excel_filename, "rb") as file:
                st.download_button(
                    label="📥 Download Updated Excel",
                    data=file,
                    file_name=excel_filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.warning("No new data to save!")

    else:
        st.warning("Please enter at least one URL!")
