import streamlit as st
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from openpyxl import load_workbook

# Mapping scraped metric to final output column prefix
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

# Fixed periods we expect
time_periods = ["Dec-24", "Sep-24", "Jun-24", "Mar-24", "Dec-23", "FY 23-24"]

# Excel file name
excel_filename = "Financials_Data_Filled.xlsx"

st.title("📊 BSE Financials Scraper and Saver")

url = st.text_input("Enter the Financials page URL:")

if st.button("Scrape and Save"):
    if url:
        # Setup selenium
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)

        try:
            driver.get(url)
            time.sleep(5)

            # Scrape table
            table = driver.find_element(By.XPATH, '//table[@ng-bind-html="trustAsHtml(reportData.QtlyinCr)"]')
            rows = table.find_elements(By.TAG_NAME, 'tr')

            data = []
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, 'td')
                cols_text = [col.text.strip() for col in cols]
                if any(cols_text):
                    data.append(cols_text)

            if not data:
                st.error("No data found in table.")
                driver.quit()
                st.stop()

            # First row is header
            header = data[0]
            data_rows = data[1:]

            df = pd.DataFrame(data_rows, columns=header)

            # Extract company name from the page title
            page_title = driver.title
            company_name = page_title.split('|')[0].strip()

            st.success(f"Scraped data for: {company_name}")

            # Build new row dictionary
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
                    # If metric not found, leave blank
                    for period in time_periods:
                        new_row[f"{output_prefix} ({period})"] = ""

            # Check if excel already exists
            if os.path.exists(excel_filename):
                existing_df = pd.read_excel(excel_filename)
                updated_df = pd.concat([existing_df, pd.DataFrame([new_row])], ignore_index=True)
            else:
                updated_df = pd.DataFrame([new_row])

            # Save back to excel
            updated_df.to_excel(excel_filename, index=False)
            st.success("✅ Data saved successfully!")

            with open(excel_filename, "rb") as file:
                st.download_button(
                    label="📥 Download Updated Excel",
                    data=file,
                    file_name=excel_filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        except Exception as e:
            st.error(f"Error while scraping or saving: {e}")

        finally:
            driver.quit()
    else:
        st.warning("Please enter a URL!")
