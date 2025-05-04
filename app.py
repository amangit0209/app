import streamlit as st
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Default mappings and periods
default_metric_mapping = {
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

default_time_periods = ["Dec-24", "Sep-24", "Jun-24", "Mar-24", "Dec-23", "FY 23-24"]

excel_filename = "Financials_Data_Filled.xlsx"

st.title("📊 BSE Financials Scraper")

# Metric selection
selected_metrics = st.multiselect("Select metrics to extract:", options=list(default_metric_mapping.keys()), default=list(default_metric_mapping.keys()))
additional_metric = st.text_input("Add more metrics (comma-separated)")

if additional_metric:
    for metric in [m.strip() for m in additional_metric.split(',') if m.strip()]:
        if metric not in selected_metrics:
            selected_metrics.append(metric)

# Generate metric mapping dynamically
metric_mapping = {metric: default_metric_mapping.get(metric, metric) for metric in selected_metrics}

# Time period selection
selected_time_periods = st.multiselect("Select time periods to extract:", options=default_time_periods, default=default_time_periods)
additional_period = st.text_input("Add more time periods (comma-separated)")

if additional_period:
    for period in [p.strip() for p in additional_period.split(',') if p.strip()]:
        if period not in selected_time_periods:
            selected_time_periods.append(period)

urls_input = st.text_area("Enter Financials Page URLs (one per line or comma separated):")

if st.button("Scrape All and Save"):
    if urls_input.strip():
        # Setup selenium once
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)

        all_new_rows = []

        urls = [url.strip() for url in urls_input.replace(',', '\n').split('\n') if url.strip()]
        st.write(f"Found {len(urls)} URLs to process.")

        try:
            for idx, url in enumerate(urls, 1):
                st.info(f"🔄 Processing ({idx}/{len(urls)}): {url}")
                driver.get(url)
                time.sleep(5)

                try:
                    table = driver.find_element(By.XPATH, '//table[@ng-bind-html="trustAsHtml(reportData.QtlyinCr)"]')
                    rows = table.find_elements(By.TAG_NAME, 'tr')

                    data = []
                    for row in rows:
                        cols = row.find_elements(By.TAG_NAME, 'td')
                        cols_text = [col.text.strip() for col in cols]
                        if any(cols_text):
                            data.append(cols_text)

                    if not data:
                        st.warning(f"No data found in table for URL: {url}")
                        continue

                    header = data[0]
                    data_rows = data[1:]
                    df = pd.DataFrame(data_rows, columns=header)

                    page_title = driver.title
                    company_name = page_title.split('|')[0].strip()
                    new_row = {"Company Name": company_name}

                    for metric, output_prefix in metric_mapping.items():
                        matching_row = df[df[header[0]].str.strip() == metric]
                        if not matching_row.empty:
                            for period in selected_time_periods:
                                try:
                                    value = matching_row.iloc[0][period]
                                    new_row[f"{output_prefix} ({period})"] = value if value != "" else ""
                                except KeyError:
                                    new_row[f"{output_prefix} ({period})"] = ""
                        else:
                            for period in selected_time_periods:
                                new_row[f"{output_prefix} ({period})"] = ""

                    all_new_rows.append(new_row)

                except Exception as e:
                    st.error(f"Error processing URL: {url} → {e}")

        finally:
            driver.quit()

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
                    label="📅 Download Updated Excel",
                    data=file,
                    file_name=excel_filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.warning("No new data to save!")
    else:
        st.warning("Please enter at least one URL!")
