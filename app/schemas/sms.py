# verify_project/app/schemas/sms.py
from pydantic import BaseModel, Field
import re

class SendCodeRequest(BaseModel):
    """
    Request model for sending a verification code.
    """
    phone_number: str = Field(..., description="The phone number to send the OTP to. Should be in a recognizable format.")

    # Example validator, adjust regex as needed for your phone number formats
    # @validator('phone_number')
    # def validate_phone_number(cls, v):
    #     if not re.match(r"^\+?[0-9\s-]{10,15}$", v): # Basic international format check
    #         raise ValueError('Invalid phone number format')
    #     return v

class VerifyCodeRequest(BaseModel):
    """
    Request model for verifying an OTP.
    """
    phone_number: str = Field(..., description="The phone number associated with the OTP.")
    otp_code: str = Field(..., min_length=4, max_length=6, description="The OTP code received by the user.")

class MessageResponse(BaseModel):
    """
    Generic message response model.
    """
    message: str
    detail: str | None = None # Optional field for more details
