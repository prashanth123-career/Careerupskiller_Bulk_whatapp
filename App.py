import streamlit as st
import pandas as pd
import pywhatkit as kit
import time
from datetime import datetime
import os

# App title and description
st.title("📱 Bulk WhatsApp Message Sender")
st.markdown("""
Send personalized WhatsApp messages to multiple contacts with a 2-second delay between each message.
""")

# Sidebar with instructions
with st.sidebar:
    st.header("Instructions")
    st.markdown("""
    1. Prepare a CSV file with columns: 'Name', 'Phone' (with country code), and 'Message'
    2. Upload the file below
    3. Preview the data to verify
    4. Click 'Send Messages' when ready
    5. Keep this window open until all messages are sent
    
    **Note:** 
    - You need to be logged in to WhatsApp Web
    - The app will automatically open WhatsApp Web in your default browser
    - Messages will be sent one by one with a 2-second delay
    """)

# File upload
uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:
    # Read the CSV file
    try:
        df = pd.read_csv(uploaded_file)
        
        # Check required columns
        required_columns = ['Name', 'Phone', 'Message']
        if not all(col in df.columns for col in required_columns):
            st.error(f"CSV must contain these columns: {', '.join(required_columns)}")
        else:
            # Display preview
            st.subheader("Message Preview")
            st.dataframe(df.head())
            
            # Count messages
            total_messages = len(df)
            st.info(f"Total messages to send: {total_messages}")
            
            # Estimated time
            estimated_time = total_messages * 2 / 60  # in minutes
            st.info(f"Estimated sending time: ~{estimated_time:.1f} minutes")
            
            # Send messages button
            if st.button("Send Messages"):
                st.warning("⚠️ Please keep this window open until all messages are sent!")
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                sent_count = 0
                failed_count = 0
                failed_contacts = []
                
                for index, row in df.iterrows():
                    try:
                        name = row['Name']
                        phone = row['Phone']
                        message = row['Message']
                        
                        # Remove any non-numeric characters from phone
                        phone = ''.join(filter(str.isdigit, str(phone)))
                        
                        # Display current status
                        status_text.text(f"Sending to {name} ({phone})...")
                        
                        # Get current time and add 20 seconds (time to open browser)
                        now = datetime.now()
                        send_time = now.replace(second=now.second + 20)
                        
                        # Send message
                        kit.sendwhatmsg(
                            phone_no=f"+{phone}",
                            message=message,
                            time_hour=send_time.hour,
                            time_min=send_time.minute,
                            wait_time=15,
                            tab_close=True
                        )
                        
                        # Wait 2 seconds before next message
                        time.sleep(2)
                        
                        sent_count += 1
                        
                    except Exception as e:
                        st.error(f"Failed to send to {row['Name']}: {str(e)}")
                        failed_count += 1
                        failed_contacts.append(f"{row['Name']} ({row['Phone']})")
                    
                    # Update progress
                    progress = (index + 1) / total_messages
                    progress_bar.progress(progress)
                
                # Show completion status
                status_text.text("")
                st.success(f"✅ Sent {sent_count}/{total_messages} messages successfully!")
                
                if failed_count > 0:
                    st.error(f"❌ Failed to send {failed_count} messages:")
                    for contact in failed_contacts:
                        st.write(f"- {contact}")
                
                # Play completion sound
                st.balloons()
                
    except Exception as e:
        st.error(f"Error reading CSV file: {str(e)}")
else:
    st.info("Please upload a CSV file to get started")

# Sample CSV download
st.markdown("### Need a sample CSV template?")
st.download_button(
    label="Download Sample CSV",
    data="""Name,Phone,Message
John Doe,911234567890,Hello John! This is a test message.
Jane Smith,911234567891,Hi Jane! Just checking in.
""",
    file_name="whatsapp_contacts_sample.csv",
    mime="text/csv"
)
