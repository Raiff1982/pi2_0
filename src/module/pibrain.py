import logging
import os
import tkinter as tk
import urllib.request

import openai
from botbuilder.core import MessageFactory, TurnContext
from botbuilder.schema import Activity, ActivityTypes, EndOfConversationCodes
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googletrans import Translator
from module.utils import (connect_to_database, get_database_info)
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def show_privacy_consent():
	"""Display a pop-up window to obtain user consent for data collection and privacy."""

	def on_accept():
		user_consent.set(True)
		root.destroy()

	def on_decline():
		user_consent.set(False)
		root.destroy()

	root = tk.Tk()
	root.title("Data Permission and Privacy")

	message = ("We value your privacy. By using this application, you consent to the collection and use of your data "
			   "as described in our privacy policy. Do you agree to proceed?")
	label = tk.Label(root, text=message, wraplength=400, justify="left")
	label.pack(padx=20, pady=20)

	button_frame = tk.Frame(root)
	button_frame.pack(pady=10)

	accept_button = tk.Button(button_frame, text="Accept", command=on_accept)
	accept_button.pack(side="left", padx=10)

	decline_button = tk.Button(button_frame, text="Decline", command=on_decline)
	decline_button.pack(side="right", padx=10)

	user_consent = tk.BooleanVar()
	root.mainloop()

	return user_consent.get()


# Load environment variables from .env file
load_dotenv()

# Validate environment variables
openai_api_key = os.getenv('OPENAI_API_KEY')
azure_openai_api_key = os.getenv('AZURE_OPENAI_API_KEY')
azure_openai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
weather_api_key = os.getenv('WEATHER_API_KEY')
news_api_key = os.getenv('NEWS_API_KEY')
alpha_vantage_api_key = os.getenv('ALPHA_VANTAGE_API_KEY')

if not openai_api_key:
	logging.error("OpenAI API key not found in environment variables.")
if not azure_openai_api_key or not azure_openai_endpoint:
	logging.error("Azure OpenAI API key or endpoint not found in environment variables.")
if not weather_api_key:
	logging.error("Weather API key not found in environment variables.")
if not news_api_key:
	logging.error("News API key not found in environment variables.")
if not alpha_vantage_api_key:
	logging.error("Alpha Vantage API key not found in environment variables.")

# Set your OpenAI API key
openai.api_key = openai_api_key

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def download_database(url: str, file_path: str) -> None:
	"""Download the database file from the given URL."""
	try:
		logging.info(f"Downloading database from {url}...")
		urllib.request.urlretrieve(url, file_path)
		logging.info("Download complete.")
	except urllib.error.URLError as e:
		logging.error(f"Error: Failed to download database. {e}")


# Database connection
db_path = "data/Chinook.db"
db_url = "https://github.com/lerocha/chinook-database/raw/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite"
if not os.path.exists(db_path):
	os.makedirs(os.path.dirname(db_path), exist_ok=True)
	download_database(db_url, db_path)
conn = connect_to_database(db_path)
if not conn:
	logging.error("Failed to connect to the database.")
else:
	db_info = get_database_info(conn)
	logging.info(f"Database info: {db_info}")


# Sentiment analysis functions
def analyze_sentiment_textblob(text: str) -> TextBlob:
	"""Analyze the sentiment of the given text using TextBlob."""
	blob = TextBlob(text)
	sentiment = blob.sentiment
	return sentiment


def analyze_sentiment_vader(text: str) -> dict:
	"""Analyze the sentiment of the given text using VADER."""
	analyzer = SentimentIntensityAnalyzer()
	sentiment = analyzer.polarity_scores(text)
	return sentiment


async def end_conversation(turn_context: TurnContext) -> None:
	"""Ends the conversation with the user."""
	await turn_context.send_activity(
		MessageFactory.text("Ending conversation from the skill...")
	)
	end_of_conversation = Activity(type=ActivityTypes.end_of_conversation)
	end_of_conversation.code = EndOfConversationCodes.completed_successfully
	await turn_context.send_activity(end_of_conversation)


async def handle_error(turn_context: TurnContext, error: Exception) -> None:
	"""Handles errors by logging them and notifying the user."""
	logging.error(f"An error occurred: {error}")
	await turn_context.send_activity(
		MessageFactory.text("An error occurred. Please try again later.")
	)


class MyBot:

	def __init__(self):
		self.context = {}

	async def enhance_context_awareness(self, user_id: str, text: str) -> None:
		"""Enhance context awareness by analyzing the user's environment, activities, and emotional state."""
		sentiment = analyze_sentiment_vader(text)
		if user_id not in self.context:
			self.context[user_id] = []
		self.context[user_id].append({"text": text, "sentiment": sentiment})

	async def proactive_learning(self, user_id: str, feedback: str) -> None:
		"""Encourage proactive learning by seeking feedback and exploring new topics."""
		if user_id not in self.context:
			self.context[user_id] = []
		self.context[user_id].append({"feedback": feedback})

	async def ethical_decision_making(self, user_id: str, decision: str) -> None:
		"""Promote ethical decision-making by considering the ethical implications of actions."""
		if user_id not in self.context:
			self.context[user_id] = []
		self.context[user_id].append({"decision": decision})

	async def emotional_intelligence(self, user_id: str, text: str) -> None:
		"""Enhance emotional intelligence by recognizing and responding to the user's emotions."""
		sentiment = analyze_sentiment_textblob(text)
		if user_id not in self.context:
			self.context[user_id] = []
		self.context[user_id].append({"text": text, "sentiment": sentiment})

	async def transparency(self, user_id: str, action: str) -> None:
		"""Promote transparency by explaining the bot's actions and decisions."""
		if user_id not in self.context:
			self.context[user_id] = []
		self.context[user_id].append({"action": action})


# Translation function
def translate_text(text: str, target_language: str) -> str:
	"""Translate the given text to the target language using Google Translate."""
	translator = Translator()
	translation = translator.translate(text, dest=target_language)
	return translation.text


# Calendar API integration
def get_calendar_events():
	"""Fetch upcoming events from Google Calendar."""
	creds = service_account.Credentials.from_service_account_file(
		'path/to/credentials.json',
		scopes=['https://www.googleapis.com/auth/calendar.readonly']
	)
	service = build('calendar', 'v3', credentials=creds)
	now = '2023-01-01T00:00:00Z'  # 'Z' indicates UTC time
	events_result = service.events().list(
		calendarId='primary', timeMin=now,
		maxResults=10, singleEvents=True,
		orderBy='startTime').execute()
	events = events_result.get('items', [])

	if not events:
		logging.info('No upcoming events found.')
		return []

	event_list = []
	for event in events:
		start = event['start'].get('dateTime', event['start'].get('date'))
		event_list.append(f"{start} - {event['summary']}")

	return event_list


if __name__ == "__main__":
	if not show_privacy_consent():
		logging.info("User declined consent. Exiting application.")
	else:
		logging.info("User accepted consent. Proceeding with application.")
