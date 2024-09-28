# otp.py
import random as rn
import string as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

otp_store = {}  # Temporary in-memory store; replace with a database in production.

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
USERNAME = 'codesample18@gmail.com'  # Use environment variables for security
PASSWORD = 'rzyz slgi mzlv bezm'     # Replace with your email password or app password

def send_otp(to_email):
    """Generates a 6-digit OTP, sends it to the provided email, and stores it."""
    OTP = ''.join(rn.choices(st.digits, k=6))
    otp_store[to_email] = OTP  # Store OTP temporarily

    # Email content
    from_email = USERNAME
    subject = 'Your OTP for Verification'  # Updated subject line
    body = f"""
    Dear User,

    Thank you for using SportsSehat. To complete your sign-in process, please use the verification code below:

    **{OTP}**

    Please note that this code is valid for 10 minutes. If you did not request this code, please ignore this email.

    Best Regards,
    The SportsSehat Team
    """

    # Create and send the message
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Secure the connection
            server.login(USERNAME, PASSWORD)
            server.send_message(msg)
        print(f"OTP sent successfully to {to_email}!")
    except Exception as e:
        print(f"Failed to send OTP: {e}")
def verify_otp(to_email, entered_otp):
    """Verifies if the entered OTP matches the stored OTP for the given email."""
    stored_otp = otp_store.get(to_email)
    if stored_otp and stored_otp == entered_otp:
        del otp_store[to_email]  # Optionally remove the OTP after successful verification
        return True
    return False