import time
import datetime
import requests
import logging
from typing import Optional, Tuple, Callable
from configs.bot_config import BotConfig
from models.db import DatabaseManager
from models.informations import InformationDateManager
from models.users import UserManager
from views.diff_checker import diff_to_dict, build_message_custom
from views.network_utils import split_message

# yes we
from plugin.extract_data.main_extractor import get_extracet

class Do_Broadcast:
    def __init__(self, 
                 func: Callable = get_extracet, 
                 use_diff: bool = True, 
                 auth: bool = True):
        """
        Initializes the Do_Broadcast with necessary configuration and dependencies.

        :param func: Callable function to fetch data (used in API interaction).
        :param use_diff: If True, messages are sent with diffs (changes) from the last data.
        :param auth: If True, only users with '1' as the first character in their flags will receive messages.
        """
        self.logger = logging.getLogger(self.__class__.__name__)  # Logger per class
        self.func = func  # Function to fetch data
        self.use_diff = use_diff  # Flag to determine if diffs should be used
        self.auth = auth  # Flag to enable filtering of users based on their flags

        # Initialize settings and dependencies
        self.config = BotConfig()
        self.db_manager = DatabaseManager(self.config.DB_FILE)
        self.user_manager = UserManager(db_manager=self.db_manager)
        self.information_manager = InformationDateManager(db_manager=self.db_manager)

    def send_message(self, chat_id: int, text: str):
        """
        Sends a message to a user, splitting it if it's too long.

        :param chat_id: Telegram chat ID of the recipient.
        :param text: Message text to be sent.
        """
        messages = split_message(text)

        for chunk in messages:
            self._send_single_message(chat_id, chunk)

    def _send_single_message(self, chat_id: int, text: str):
        """
        Sends a single part of the message to the specified user.

        :param chat_id: Telegram chat ID of the recipient.
        :param text: A single chunk of the message to be sent.
        """
        url = f"{self.config.BASE_URL}/sendMessage"
        params = {'chat_id': chat_id, 'text': text}
        try:
            response = requests.get(url, params=params)
            result = response.json()
            if result.get("ok"):
                self.logger.info(f"Message part sent successfully to chat_id {chat_id}.")
            else:
                error_description = result.get("description", "No error description provided.")
                self.logger.error(f"Error sending message part to chat_id {chat_id}: {error_description}")
        except requests.RequestException as e:
            self.logger.error(f"Error sending message to chat_id {chat_id}: {e}")
        time.sleep(self.config.LIMIT)

    def process_auth(self, user_flags: str, data: str, last_data: str) -> str:
        """
        Processes the message for each user, considering their flags and whether diffs should be used.

        :param user_flags: Flags associated with the user (used for filtering).
        :param data: The current data to be sent.
        :param last_data: The previous data (used to calculate diffs).
        :return: The message to be sent to the user.
        """
        if not self.auth:
            return data  # No authentication, send the data as it is

        if user_flags.startswith("1"):
            if self.use_diff:
                diff_result = diff_to_dict(first=data, second=last_data)
                return build_message_custom(user_data=user_flags, message=diff_result)
            else:
                return data
        else:
            return f"{len(data)}\n{user_flags}"  # For unauthorized users, send a summary

    def send_broadcast(self, data: str, last_data: str = ""):
        """
        Sends a broadcast message to all users, applying necessary filters based on flags.

        :param data: The current data to be sent.
        :param last_data: The previous data (used for diff calculations if needed).
        """
        users = self.user_manager.get_all_users()
        self.logger.info(f"Sending broadcast to {len(users)} users.")

        for user in users:
            self.logger.info(f"Preparing message for user chat_id: {user.chat_id}, flags: {user.flags}")
            message = self.process_auth(user.flags, data, last_data)
            self.send_message(user.chat_id, message)
            time.sleep(self.config.LIMIT)

    def update_information(self, data) -> Tuple[str, str]:
        """
        Updates the database with the new data and retrieves the last data.

        :param data: The current data to be saved into the database.
        :return: A tuple of (new data, last data).
        """
        # Step 1: Fetch the last data from the database
        infos = self.information_manager.get_last_information(1)
        last_data = infos[0][2] if infos else ""
        self.logger.info("Fetched last data from the database.")

        if data:
            # Step 2: Add new data to the database (after getting last_data)
            self.information_manager.add_information(data)
            self.logger.info("New data added to the database.")
            return data, last_data

        self.logger.error(f"ERROR when getting data from API: data: {data}")
        return "", ""

    def API(self) -> Optional[str]:
        """
        Fetches the data from the external API using the provided function.

        :return: The data fetched from the API.
        """
        return self.func(debug=False, include_all=True)

    def run(self):
        """
        Orchestrates the process of fetching data, updating the database, and sending the broadcast.
        """
        try:
            self.logger.info("Starting broadcast process...")
            # Step 1: Fetch data using the provided function
            api_response = self.API()

            # Step 2: Update information in the database and get the last data
            data, last_data = self.update_information(data=api_response)

            # Step 3: If data is valid, send the broadcast
            if data:
                self.send_broadcast(data=data, last_data=last_data)
                self.logger.info(f"✅ Broadcast sent at {datetime.datetime.now()}")
            else:
                self.logger.warning("No new data to send, broadcast skipped.")
        except Exception as e:
            self.logger.error(f"Error during broadcast: {e}")

if __name__ == "__main__":
    # Logger setup for class with class name
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    runner = Do_Broadcast(func=get_extracet, use_diff=True, auth=True)
    runner.run()
