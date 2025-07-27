# verify_project/app/services/sms_service.py

import logging

import requests  # Asynchronous HTTP client

from app.core.config import settings  # Import the settings instance

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class SMSSendingError(Exception):
    """Custom exception for SMS sending failures."""

    def __init__(self, message, status_code=None, response_text=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


async def send_otp_sms_async(
        recipient: str,
        verification_code: str,
) -> bool:
    """
    Sends an OTP SMS to the recipient using an asynchronous HTTP client.

    Args:
        recipient: The phone number of the recipient.
        verification_code: The OTP code to send.

    Returns:
        True if the SMS was sent successfully (according to the provider).

    Raises:
        SMSSendingError: If there's an issue sending the SMS.
    """

    headers = {
        "Authorization": settings.SMS_API_KEY,  # Get API key from settings
        "Content-Type": "application/json",
    }
    print(settings.SMS_SENDER_NUMBER)
    payload = {
        "sending_type": "pattern",
        "from_number": settings.SMS_SENDER_NUMBER,
        "code": "xxb9ctbo9k4ymqs",
        "recipients": [recipient],
        "params": {
            "verification-code": int(verification_code)
        }
    }

    try:
        response = requests.post(
            url=settings.SMS_API_URL,
            headers=headers,
            json=payload
        )
        response.raise_for_status()  # Raises HTTPStatusError for 4xx/5xx responses

        # Assuming 2xx status means success. Some APIs might have specific success codes in the body.
        # You might need to inspect response.json() for specific success indicators from your provider.
        logger.info(f"SMS sent successfully to {recipient}. Status: {response.status_code}")
        # Example: if response.json().get("status") == "success": return True
        return True

    except Exception as exc:  # Catch any other unexpected errors
        logger.error(f"Unexpected error sending SMS to {recipient}: {exc}")
        raise SMSSendingError(message="An unexpected error occurred while trying to send SMS.")
