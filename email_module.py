""" credit --- https://medium.com/@elimrany.issam.job/how-to-automate-sending-emails-using-python-2024-2025-4b5d90fae48b """

import smtplib
import ssl
from email.message import EmailMessage
import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

# Define email sender and receiver
email_sender = os.environ.get('EMAIL_SENDER')
email_password = os.environ.get('EMAIL_PASSWORD')

# Add SSL ( of security)
context = ssl.create_default_context()

# send a notification that a motion was detected
def send_email(email_receivers, time_detected): 
    em = EmailMessage()
    
    em['From'] = email_sender
    em['To'] = ', '.join(email_receivers)  # Join the list of receivers into a comma-separated string
    em['Subject'] = 'Motion detected inside the room'
    
    # Variables for dynamic content
    name = os.environ.get('SENDER_NAME')
    drive_link = os.environ.get('DRIVE_LINK')

    # HTML content with f-string
    body = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{
        font-family: Arial, sans-serif;
        line-height: 1.6;
        }}
        p {{
        margin: 0 0 10px;
        }}
        .signature {{
        font-weight: bold;
        }}
        .ps {{
        font-style: italic;
        }}
    </style>
    </head>
    <body>
    <p>Hello,</p>
    <p>This is a email notifying you that motion was detected inside the room at {time_detected.strftime("%Y/%m/%d %H:%M:%S")}</p>
    <p>Best regards,</p>
    <p class="signature">{name}</p>
    <p></p>
    <p class="ps">P.S.: Make sure you check the drive for the footage here {drive_link}</p>
    </body>
    </html>
    """
    
    em.add_alternative(body, subtype='html')

    # Log in and send the email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receivers, em.as_string())
    
    print("email sent!")