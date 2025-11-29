import streamlit as st
import pandas as pd
import joblib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# ----------------------------
# Email Configuration
# ----------------------------
SENDER_EMAIL = "your_email@example.com"  # Replace with your Gmail address
SENDER_PASSWORD = "your_app_password"  # 16-character Gmail App Password
RECEIVER_EMAIL = "receiver_email@example.com"  # Where to send alerts

def send_email_alert(transaction_amount, probability, is_fraud):
    try:
        if is_fraud:
            subject = "🚨 FRAUD ALERT: Suspicious Transaction Detected!"
            body = f"""
            🚨 FRAUD ALERT 🚨

            A potentially fraudulent transaction was detected.

            💰 Transaction Amount: ₹{transaction_amount}
            ⚠️ Fraud Probability: {probability*100:.2f}%

            Please review immediately.
            """
        else:
            subject = "✅ Transaction Verified Successfully!"
            body = f"""
            ✅ Genuine Transaction ✅

            Your recent transaction appears safe and verified.

            💰 Transaction Amount: ₹{transaction_amount}
            🧮 Fraud Probability: {probability*100:.2f}%

            Thank you for banking securely with us.
            """

        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECEIVER_EMAIL
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Connect to Gmail SMTP
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Secure the connection
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)

        return True
    except Exception as e:
        st.warning(f"⚠️ Email not sent: {e}")
        return False
     
# ----------------------------


# Load the trained model
model = joblib.load('fraud_detection_model.pkl')
st.title("💳 Financial Fraud Detection App")
st.markdown("""
This web app predicts whether a transaction is **Fraudulent (🚨)** or **Genuine (✅)**  
Enter transaction details below and click **Predict Fraud**.
""")
# Input fields
st.header("🧾 Transaction Details")
# Create a layout with columns for better appearance
col1, col2 = st.columns(2)

with col1:
    transaction_amount = st.number_input("Transaction Amount (₹)", min_value=1, value=2000)
    account_balance = st.number_input("Account Balance (₹)", min_value=0, value=10000)
    transaction_hour = st.slider("Transaction Hour (0–23)", min_value=0, max_value=23, value=14)
    account_type = st.selectbox("Account Type", ["Savings", "Current", "Credit"])
    
with col2:
    transaction_type = st.selectbox("Transaction Type", ["Online", "POS", "ATM"])
    device_type = st.selectbox("Device Type", ["Mobile", "Desktop", "POS Terminal"])
    transaction_location = st.selectbox("Transaction Location", ["Domestic", "International"])
    transaction_dayofweek = st.selectbox(
        "Transaction Day of Week",
        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    )
# Prepare data for prediction
# ----------------------------
input_data = pd.DataFrame({
    'transaction_amount': [transaction_amount],
    'account_balance': [account_balance],
    'transaction_hour': [transaction_hour],
    'account_type': [account_type],
    'transaction_type': [transaction_type],
    'device_type': [device_type],
    'transaction_location': [transaction_location],
    'transaction_dayofweek': [transaction_dayofweek]
})
# ---- Fill missing columns with default values ----
all_columns = [
    'gender', 'state', 'city', 'bank_branch', 'account_type', 'transaction_type',
    'merchant_category', 'transaction_device', 'transaction_location',
    'device_type', 'transaction_currency', 'transaction_dayofweek',
    'transaction_month', 'age', 'transaction_amount', 'account_balance',
    'transaction_hour'
]
# Add any missing columns with neutral defaults
for col in all_columns:
    if col not in input_data.columns:
        if col in ['age', 'transaction_amount', 'account_balance', 'transaction_hour']:
            input_data[col] = 0
        else:
            input_data[col] = 'Unknown'

# Reorder to match training order
input_data = input_data[all_columns]
# ----------------------------
# Predict Button
# ----------------------------
st.markdown("---")
if st.button("🔍 Predict Fraud"):
    try:
        prediction = model.predict(input_data)[0]
        prediction_proba = (
            model.predict_proba(input_data)[0][1] if hasattr(model, "predict_proba") else None
        )

        if prediction == 1:
            st.error("🚨 ALERT: This transaction is **FRAUDULENT!** ⚠️")
            st.warning("Please verify or block this account immediately.")
            if prediction_proba:
                st.write(f"**Fraud Probability:** {prediction_proba*100:.2f}%")

            # ✉️ Send fraud email
            email_sent = send_email_alert(transaction_amount, prediction_proba or 0, is_fraud=True)
            if email_sent:
                st.info("📧 Fraud alert email sent successfully.")
            else:
                st.warning("⚠️ Could not send fraud alert email.")

        else:
            st.success("✅ This transaction is **GENUINE.** 💰")
            if prediction_proba:
                st.write(f"**Fraud Probability:** {prediction_proba*100:.2f}%")

            # ✉️ Send genuine email
            email_sent = send_email_alert(transaction_amount, prediction_proba or 0, is_fraud=False)
            if email_sent:
                st.info("📧 Genuine transaction confirmation email sent successfully.")
            else:
                st.warning("⚠️ Could not send genuine confirmation email.")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
        st.info("Ensure your model pipeline and input feature names match exactly.")

# ----------------------------
# Footer
# ----------------------------
st.markdown("---")
st.caption("Developed by Susheel | Streamlit + Decision Tree Model")