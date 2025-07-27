# verify_project/app/crud/user_crud.py
import os
from datetime import datetime

from dotenv import load_dotenv
from pymongo import MongoClient, errors
from pymongo.server_api import ServerApi
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Call load_dotenv() once. If your main.py or config.py already does this,
# you might not need it here, but it's safe to have for standalone usability.
# Ensure .env is in the project root.
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
load_dotenv(dotenv_path=dotenv_path)


class DatabaseSync:
    def __init__(
            self,
            database_name: str = "users_db",
            users_collection_name: str = "user_profiles",
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
            self.users_collection = self.database.get_collection(users_collection_name)
        except errors.ServerSelectionTimeoutError as e:  # More specific error for timeout
            logger.error(f"Could not connect to MongoDB (timeout): {e}. Check URI and network.")
            raise ConnectionError(f"MongoDB connection timeout: {e}") from e
        except errors.ConnectionFailure as e:
            logger.error(f"Could not connect to MongoDB (failure): {e}")
            raise ConnectionError(f"MongoDB connection failure: {e}") from e
        except Exception as e:  # Catch other potential errors during setup
            logger.error(f"An unexpected error occurred during MongoDB setup: {e}")
            raise

    def create_user(self, name: str, lastname: str, phone_number: str) -> str | bool | None:
        """
        Creates a new user document in the users_collection.
        - Returns str (user_id) if a new user is created.
        - Returns True if the user (by phone_number) already exists.
        - Returns None if input validation fails or a database error occurs during insertion.

        Note: Returning multiple types (str, bool, None) can make handling the response
        more complex. Consider raising custom exceptions or returning a consistent
        response object/tuple for clearer error handling.
        """
        if not all([name, lastname, phone_number]):
            logger.warning("Attempted to create user with missing information (name, lastname, or phone_number).")
            return None

        user_document = {
            "Name": name,
            "LastName": lastname,
            "PhoneNumber": phone_number,
            "createdAt": datetime.now()  # Use UTC for consistency
        }

        try:
            if self.users_collection.find_one({"PhoneNumber": phone_number}):
                logger.info(f"User with phone number {phone_number} already exists.")
                return True  # Indicate user already exists

            result = self.users_collection.insert_one(user_document)
            logger.info(f"User '{name} {lastname}' created successfully with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except errors.DuplicateKeyError:  # If you have a unique index on PhoneNumber
            logger.warning(f"Attempted to create duplicate user with phone number {phone_number} (DuplicateKeyError).")
            return True  # User effectively exists
        except errors.PyMongoError as e:
            logger.error(f"MongoDB error while creating user '{name} {lastname}': {e}")
            return None  # Indicate failure
        except Exception as e:  # Catch any other unexpected errors
            logger.error(f"An unexpected error occurred while creating user '{name} {lastname}': {e}")
            return None

    def get_user_by_phone(self, phone_number: str) -> dict | None:
        """
        Retrieves a user by their phone number.
        Returns the user document (dict) or None if not found or an error occurs.
        """
        if not phone_number:
            logger.warning("Attempted to get user with no phone number provided.")
            return None
        try:
            user_doc = self.users_collection.find_one({"PhoneNumber": phone_number})
            if user_doc and "_id" in user_doc:
                user_doc["_id"] = str(user_doc["_id"])  # Convert ObjectId
                logger.info(f"User found for phone number {phone_number}.")
            elif user_doc:
                logger.warning(f"User document found for {phone_number} but missing '_id'. Doc: {user_doc}")
            else:
                logger.info(f"No user found for phone number {phone_number}.")
            return user_doc
        except errors.PyMongoError as e:
            logger.error(f"MongoDB error while fetching user by phone '{phone_number}': {e}")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred while fetching user by phone '{phone_number}': {e}")
            return None

    def close_connection(self):
        """Closes the MongoDB client connection."""
        if hasattr(self, 'client') and self.client:
            self.client.close()
            logger.info("MongoDB connection closed.")
        else:
            logger.info("No active MongoDB client to close or client already closed.")
