import logging
import os
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient, errors
from pymongo.errors import PyMongoError
from pymongo.server_api import ServerApi

from app.core.config import settings

logger = logging.getLogger(__name__)

class OtpManagerSync:
    def __init__(
        self,
        database_name: str = "otp_db",
        otp_collection_name: str = "otp_codes",
    ):
        mongo_uri = os.getenv("MONGO_URI")
        if not mongo_uri:
            logger.error("MONGO_URI environment variable not set.")
            raise ValueError("MONGO_URI environment variable not set. Please check your .env file.")

        try:
            # It's generally better to create the MongoClient instance once per application
            # and reuse it, rather than per DatabaseSync instance, especially in web apps.
            # However, sticking to your current structure for now.
            self.client = MongoClient(mongo_uri, server_api=ServerApi('1'))
            self.client.admin.command('ping')  # Verify connection
            logger.info(
                f"Successfully connected to MongoDB: {mongo_uri.split('@')[-1] if '@' in mongo_uri else mongo_uri}")
            self.database = self.client.get_database(database_name)
            self.otp_collection = self.database.get_collection(otp_collection_name)
        except errors.ServerSelectionTimeoutError as e:  # More specific error for timeout
            logger.error(f"Could not connect to MongoDB (timeout): {e}. Check URI and network.")
            raise ConnectionError(f"MongoDB connection timeout: {e}") from e
        except errors.ConnectionFailure as e:
            logger.error(f"Could not connect to MongoDB (failure): {e}")
            raise ConnectionError(f"MongoDB connection failure: {e}") from e
        except Exception as e:  # Catch other potential errors during setup
            logger.error(f"An unexpected error occurred during MongoDB setup: {e}")
            raise

    def store_otp(self, phone_number: str, otp_code: str) -> bool:
        """
        Stores or updates the OTP for a given phone number in MongoDB.
        An existing UNVERIFIED OTP for the same phone number will be replaced.

        Returns:
            bool: True if OTP was stored successfully, False otherwise.
        """
        if self.otp_collection is None:
            logger.error("OtpManagerSync: OTP collection is not initialized. Cannot store OTP.")
            return False

        try:
            now = datetime.now(timezone.utc)
            expires_at = now + timedelta(seconds=settings.OTP_EXPIRY_SECONDS)

            otp_document = {
                "phone_number": phone_number,
                "otp_code": otp_code,  # IMPORTANT: Hash the OTP before storing in production!
                "created_at": now,
                "expires_at": expires_at,
                "verified": False
            }

            result = self.otp_collection.replace_one(
                {"phone_number": phone_number, "verified": False},
                otp_document,
                upsert=True
            )

            if result.acknowledged and (result.modified_count > 0 or result.upserted_id is not None):
                logger.info(f"OtpManagerSync: OTP stored/updated for phone number: {phone_number}")
                return True
            else:
                logger.warning(
                    f"OtpManagerSync: Failed to store/update OTP for phone number: {phone_number}. Result: {result.raw_result}")
                return False
        except PyMongoError as e:
            logger.error(f"OtpManagerSync: MongoDB error while storing OTP for {phone_number}: {e}")
            return False
        except Exception as e:
            logger.error(f"OtpManagerSync: Unexpected error while storing OTP for {phone_number}: {e}", exc_info=True)
            return False

    def verify_otp(self, phone_number: str, otp_code: str) -> bool:
        """
        Verifies the OTP for a given phone number from MongoDB.
        Checks if the OTP matches, has not expired, and has not been verified.
        Deletes the OTP document after successful verification.

        Returns:
            bool: True if OTP is valid, False otherwise.
        """
        if self.otp_collection is None:
            logger.error("OtpManagerSync: OTP collection is not initialized. Cannot verify OTP.")
            return False

        try:
            now_utc = datetime.now(timezone.utc)

            otp_document = self.otp_collection.find_one_and_delete(
                {
                    "phone_number": phone_number,
                    "otp_code": otp_code,
                    "verified": False,
                    "expires_at": {"$gt": now_utc}
                }
            )

            if otp_document:
                logger.info(f"OtpManagerSync: OTP verified and removed for phone number: {phone_number}")
                return True
            else:
                logger.warning(
                    f"OtpManagerSync: OTP verification failed for {phone_number}: OTP not found, expired, already verified, or code mismatch.")
                return False
        except PyMongoError as e:
            logger.error(f"OtpManagerSync: MongoDB error while verifying OTP for {phone_number}: {e}")
            return False
        except Exception as e:
            logger.error(f"OtpManagerSync: Unexpected error while verifying OTP for {phone_number}: {e}", exc_info=True)
            return False

    def close_connection(self):
        """Closes the MongoDB client connection."""
        if hasattr(self, 'client') and self.client:
            self.client.close()
            logger.info("MongoDB connection closed.")
        else:
            logger.info("No active MongoDB client to close or client already closed.")