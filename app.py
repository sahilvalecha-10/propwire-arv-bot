import streamlit as st
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

st.set_page_config(page_title="Propwire ARV Bot", layout="wide")
st.title("🏠 Propwire ARV Automator")

with st.sidebar:
    st.header("Propwire Login")
    email_addr = st.text_input("Email")
    password = st.text_input("Password", type="password")
    st.info("If the bot fails, use the debug button below.")

col1, col2, col3, col4 = st.columns(4)
with col1: address = st.text_input("Address", "1426 S Curtis Ave, Tucson, AZ 85713")
with col2: s_sqft = st.number_input("Subject SqFt", 1500)
with col3: s_beds = st.number_input("Beds", 3)
with col4: s_baths = st.number_input("Baths", 2.0)

if st.button("Calculate ARV"):
    if not email_addr or not password:
        st.error("Enter login details in the sidebar.")
    else:
        with st.spinner("🚀 Running..."):
            opts = Options()
            opts.add_argument("--headless")
            opts.add_argument("--no-sandbox")
            opts.add_argument("--disable-dev-shm-usage")
            opts.add_argument("--window-size=1920,1080") # Set screen size
            opts.binary_location = "/usr/bin/chromium"
            
            try:
                service = Service("/usr/bin/chromedriver")
                driver = webdriver.Chrome(service=service, options=opts)
                
                # Try to load login
                driver.get("https://propwire.com/login")
                time.sleep(5)
                
                # --- DEBUG: SHOW US WHAT THE BOT SEES ---
                st.image(driver.get_screenshot_as_png(), caption="What the bot sees right now")
                
                # Try to find email
                email_field = driver.find_element(By.NAME, "email")
                email_field.send_keys(email_addr)
                
                driver.find_element(By.NAME, "password").send_keys(password)
                driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
                
                st.success("Logged in! (Processing mock data...)")
                
                # Your table logic follows here...
                raw_data = [{"address": "Comp 1", "price": 280000, "sqft": 1400, "beds": 3, "baths": 2}]
                st.table(pd.DataFrame(raw_data))

            except Exception as e:
                st.error(f"Snapshot taken. Error: {e}")
                # Show screenshot even on error
                st.image(driver.get_screenshot_as_png(), caption="Error State Screenshot")
            finally:
                if 'driver' in locals():
                    driver.quit()
