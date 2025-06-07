# app/services/email_service.py
import httpx
from typing import List, Dict, Any

from app.core.config import settings

async def send_email_brevo(
    recipient_email: str,
    recipient_name: str,
    subject: str,
    html_content: str
) -> bool:
    """
    Sends an email using the Brevo (formerly Sendinblue) API.
    Returns True if the email was sent successfully, False otherwise.
    """
    if not settings.BREVO_API_KEY:
        print("BREVO_API_KEY not configured. Email not sent.")
        # In a real app, you might want to raise an error or log more formally
        return False

    api_url = "https://api.brevo.com/v3/smtp/email"
    
    headers = {
        "accept": "application/json",
        "api-key": settings.BREVO_API_KEY,
        "content-type": "application/json"
    }
    
    data = {
        "sender": {
            "name": settings.BREVO_SENDER_NAME,
            "email": settings.BREVO_SENDER_EMAIL
        },
        "to": [
            {
                "email": recipient_email,
                "name": recipient_name
            }
        ],
        "subject": subject,
        "htmlContent": html_content
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(api_url, headers=headers, json=data)
            response.raise_for_status() # Raises an HTTPError for bad responses (4XX or 5XX)
            # Brevo API returns 201 Created for successful email sending
            if response.status_code == 201:
                print(f"Email sent successfully to {recipient_email}")
                return True
            else:
                print(f"Failed to send email. Status: {response.status_code}, Response: {response.text}")
                return False
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred while sending email: {e.response.status_code} - {e.response.text}")
            return False
        except httpx.RequestError as e:
            print(f"Request error occurred while sending email: {e}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return False

async def send_otp_email(
    email_to: str,
    otp_code: str
) -> bool:
    """Constructs and sends an OTP email."""
    subject = f"Your OTP for Hirel Platform: {otp_code}"
    # You can create a more sophisticated HTML template for the OTP email
    html_content = f"""
    <html>
        <head></head>
        <body>
            <p>Hello,</p>
            <p>Your One-Time Password (OTP) for accessing Hirel is: <strong>{otp_code}</strong></p>
            <p>This OTP is valid for {settings.OTP_EXPIRE_MINUTES} minutes.</p>
            <p>If you did not request this OTP, please ignore this email.</p>
            <p>Thanks,<br>The Hirel Team</p>
        </body>
    </html>
    """
    # Assuming the recipient's name is the same as their email for simplicity, 
    # or you might want to fetch it if available.
    return await send_email_brevo(
        recipient_email=email_to,
        recipient_name=email_to.split('@')[0], # Basic name from email
        subject=subject,
        html_content=html_content
    )
