import streamlit as st
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

# NOTE: We removed ChromeDriverManager because Streamlit Cloud 
# uses the pre-installed driver we put in packages.txt

st.set_page_config(page_title="Propwire ARV Bot", layout="wide")
st.title("🏠 Propwire ARV Automator")

with st.sidebar:
    st.header("Propwire Login")
    email_addr = st.text_input("Email")
    password = st.text_input("Password", type="password")

col1, col2, col3, col4 = st.columns(4)
with col1: address = st.text_input("Address", "1426 S Curtis Ave, Tucson, AZ 85713")
with col2: s_sqft = st.number_input("Subject SqFt", 1500)
with col3: s_beds = st.number_input("Beds", 3)
with col4: s_baths = st.number_input("Baths", 2.0)

if st.button("Calculate ARV"):
    if not email_addr or not password:
        st.error("Enter your Propwire login in the sidebar.")
    else:
        with st.spinner("Bot is working..."):
            # --- CLOUD-SPECIFIC CHROME SETUP ---
            opts = Options()
            opts.add_argument("--headless")
            opts.add_argument("--no-sandbox")
            opts.add_argument("--disable-dev-shm-usage")
            opts.add_argument("--disable-gpu")
            
            # These two lines point to the 'packages.txt' installs
            opts.binary_location = "/usr/bin/chromium"
            service = Service("/usr/bin/chromedriver")
            
            try:
                driver = webdriver.Chrome(service=service, options=opts)
                
                # Login logic
                driver.get("https://propwire.com/login")
                time.sleep(3)
                
                # Find login fields
                driver.find_element(By.NAME, "email").send_keys(email_addr)
                driver.find_element(By.NAME, "password").send_keys(password)
                
                # Click Submit
                submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                submit_btn.click()
                
                # Wait for login to process
                time.sleep(5)
                
                # --- DATA PROCESSING LOGIC ---
                # (Using your mock data logic for now)
                raw_data = [
                    {"address": "Comp 1", "price": 280000, "sqft": 1400, "beds": 3, "baths": 2},
                    {"address": "Comp 2", "price": 240000, "sqft": 1350, "beds": 3, "baths": 1.5},
                    {"address": "Comp 3", "price": 310000, "sqft": 1600, "beds": 3, "baths": 2},
                    {"address": "Comp 4", "price": 345000, "sqft": 1700, "beds": 3, "baths": 2.5},
                    {"address": "Comp 5", "price": 360000, "sqft": 1680, "beds": 3, "baths": 3}
                ]
                df = pd.DataFrame(raw_data)

                # Strict filters
                df = df[(df['sqft'] >= s_sqft * 0.85) & (df['sqft'] <= s_sqft * 1.15)]
                df = df[(df['beds'] == s_beds) & (df['baths'].between(s_baths-1, s_baths+1))]
                df = df.sort_values(by="price")

                if not df.empty:
                    c1, c2 = st.columns(2)
                    with c1:
                        st.subheader("📉 Seller-Side (Conservative)")
                        st.table(df.head(3))
                        st.metric("Cons. ARV", f"${df.head(3)['price'].mean():,.0f}")
                    with c2:
                        st.subheader("🚀 Buyer-Side (Realistic)")
                        st.table(df.tail(3))
                        st.metric("Target ARV", f"${df.tail(3)['price'].mean():,.0f}")
                else:
                    st.warning("No comps found with those strict filters.")

            except Exception as e:
                st.error(f"Error during automation: {e}")
            finally:
                if 'driver' in locals():
                    driver.quit()
