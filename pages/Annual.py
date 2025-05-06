import streamlit as st
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from io import StringIO
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

default_time_periods = ["2025", "2024", "2023", "2022", "2021", "2020"]

excel_filename = "Annual_Data_Filled.xlsx"

st.title("\U0001F4C8 BSE Annual Trends Scraper")

selected_metrics = st.multiselect("Select metrics to extract:", options=list(default_metric_mapping.keys()), default=list(default_metric_mapping.keys()))
additional_metric = st.text_input("Add more metrics (comma-separated)")

if additional_metric:
    for metric in [m.strip() for m in additional_metric.split(',') if m.strip()]:
        if metric not in selected_metrics:
            selected_metrics.append(metric)

metric_mapping = {metric: default_metric_mapping.get(metric, metric) for metric in selected_metrics}

additional_periods_input = st.text_input("Add more time periods (comma-separated):")
combined_time_periods = default_time_periods.copy()

if additional_periods_input:
    additional_periods = [p.strip() for p in additional_periods_input.split(',') if p.strip()]
    combined_time_periods = list(dict.fromkeys(default_time_periods + additional_periods))

selected_time_periods = st.multiselect(
    "Select and order time periods to extract:",
    options=combined_time_periods,
    default=combined_time_periods
)

security_codes_input = st.text_area("Enter Security Codes (one per line or comma separated):")
security_codes = [code.strip() for code in security_codes_input.replace(',', '\n').split('\n') if code.strip()]
urls = [f"https://www.bseindia.com/stock-share-price/{code}/{code}/{code}/financials-results/" for code in security_codes]

if st.button("Scrape All and Save"):
    if urls:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)

        all_new_rows = []

        st.write(f"Found {len(urls)} URLs to process.")

        try:
            for idx, url in enumerate(urls, 1):
                st.info(f"\U0001F501 Processing ({idx}/{len(urls)}): {url}")
                driver.get(url)
                time.sleep(5)

                try:
                    table = driver.find_element(By.XPATH, "//table[contains(@ng-bind-html, 'reportData.AnninCr')]")
                    html = table.get_attribute('outerHTML')
                    df_list = pd.read_html(StringIO(html))

                    if not df_list:
                        st.warning(f"No table found for URL: {url}")
                        continue

                    df = df_list[0]
                    df.columns = df.columns.astype(str)
                    header = df.columns.tolist()

                    page_title = driver.title
                    company_name = page_title.split('|')[0].strip()
                    new_row = {"Company Name": company_name}

                    for metric, output_prefix in metric_mapping.items():
                        match = df[df.iloc[:, 0].astype(str).str.strip().str.lower() == metric.lower()]
                        if not match.empty:
                            for period in selected_time_periods:
                                try:
                                    value = match.values[0][header.index(period)]
                                    new_row[f"{output_prefix} ({period})"] = value if value != "" else ""
                                except (KeyError, ValueError):
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
                    label="\U0001F4C5 Download Updated Annual Excel",
                    data=file,
                    file_name=excel_filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.warning("No new data to save!")
    else:
        st.warning("Please enter at least one URL!")

st.markdown("<hr style='margin-top: 40px;'><div style='text-align: center;'>Developed by - <strong>Aman</strong></div>", unsafe_allow_html=True)
