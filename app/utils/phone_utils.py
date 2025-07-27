# verify_project/app/utils/phone_utils.py
import re


def convert_phone(phone_number: str) -> str:
    """
    Cleans and standardizes a phone number.
    This is a basic example. You might need a more robust library
    for proper phone number parsing and validation (e.g., phonenumbers).

    Example: Converts "0912 345 6789" to "+989123456789" (assuming Iranian numbers)
             Converts "9123456789" to "+989123456789"
    """
    # Remove any non-digit characters except for a leading '+'
    cleaned_number = re.sub(r"[^\d+]", "", phone_number)

    if cleaned_number.startswith("00"):
        # Replace leading "00" with "+"
        cleaned_number = "+" + cleaned_number[2:]
    elif cleaned_number.startswith("0"):
        # Assuming it's a local number that needs country code (e.g., Iran +98)
        # This part is highly country-specific and needs adjustment
        cleaned_number = "+98" + cleaned_number[1:]

    # If it doesn't start with '+', and is a typical length for a national number without 0,
    # prepend country code. This is also an assumption.
    elif not cleaned_number.startswith("+") and len(cleaned_number) == 10 and cleaned_number.startswith(
            "9"):  # e.g. 9123456789
        cleaned_number = "+98" + cleaned_number

    return cleaned_number
