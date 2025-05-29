import streamlit as st
import pandas as pd
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

st.set_page_config(page_title="WhatsApp Bulk Sender", layout="centered")

st.title("📤 WhatsApp Bulk Sender via WhatsApp Web")
st.markdown("""
Send personalized WhatsApp messages in bulk using your own number via WhatsApp Web (no third-party API).  
**Instructions:**
1. Upload a CSV or Excel file with columns: `name`, `phone`, `message`.
2. Login to WhatsApp Web using the QR code.
3. Click **Start Sending**.
""")

uploaded_file = st.file_uploader("📁 Upload CSV or Excel File", type=["csv", "xlsx"])
start_button = st.button("🚀 Start Sending")

def read_data(file):
    if file.name.endswith('.csv'):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)
    return df

def send_messages(data):
    options = Options()
    options.add_argument('--user-data-dir=./User_Data')  # Keep login session
    options.add_argument('--profile-directory=Default')
    options.add_argument('--headless=new')  # Comment this if you want to see browser
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.get("https://web.whatsapp.com")

    st.info("Scan QR code in browser to login (wait for 20-30 seconds)...")
    time.sleep(30)  # Give time for QR scan and loading chats

    for index, row in data.iterrows():
        phone = str(row['phone'])
        name = str(row.get('name', ''))
        message_template = str(row['message'])

        # Personalize message
        personalized_message = message_template.replace("{name}", name)

        url = f"https://web.whatsapp.com/send?phone={phone}&text={personalized_message}"
        driver.get(url)
        time.sleep(10)

        try:
            send_button = driver.find_element(By.XPATH, "//span[@data-icon='send']")
            send_button.click()
            st.success(f"✅ Sent to {name} ({phone})")
        except Exception as e:
            st.error(f"❌ Failed for {phone}: {e}")

        time.sleep(2 + index % 2)  # 2–3 sec delay to avoid spam

    st.success("🎉 All messages processed.")
    driver.quit()

if start_button and uploaded_file:
    df = read_data(uploaded_file)
    required_cols = {'phone', 'message'}
    if not required_cols.issubset(df.columns):
        st.error("Missing required columns. Please include at least: 'phone', 'message'.")
    else:
        send_messages(df)
