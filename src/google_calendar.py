"""
Google Calendar data scraper module.
Handles authentication and event retrieval from Google Calendar.
"""

import os
from datetime import datetime, timedelta, timezone
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

logger = logging.getLogger(__name__)

# Scopes required for Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


class GoogleCalendarClient:
    """Client for interacting with Google Calendar API."""

    def __init__(self, credentials_file='config/credentials.json', token_file='config/token.json'):
        """
        Initialize the Google Calendar client.

        Args:
            credentials_file: Path to OAuth2 credentials JSON file
            token_file: Path to store/load access token
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None

    def authenticate(self):
        """Authenticate with Google Calendar API."""
        creds = None

        # Load existing token if available
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)

        # Refresh or create new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save credentials for next run
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())

        self.service = build('calendar', 'v3', credentials=creds)
        logger.info("Successfully authenticated with Google Calendar API")

    def get_today_events(self, calendar_id='primary'):
        """
        Retrieve today's events from Google Calendar.

        Args:
            calendar_id: The calendar ID to fetch events from (default: 'primary')

        Returns:
            List of event dictionaries
        """
        try:
            if not self.service:
                self.authenticate()

            # Get start and end of today in UTC
            today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)

            # Convert to RFC3339 format
            time_min = today_start.isoformat()
            time_max = today_end.isoformat()

            # Fetch events
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])
            logger.info(f"Retrieved {len(events)} events from calendar for today")

            return events

        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return []

    def get_tomorrow_events(self, calendar_id='primary'):
        """
        Retrieve tomorrow's events from Google Calendar.

        Args:
            calendar_id: The calendar ID to fetch events from (default: 'primary')

        Returns:
            List of event dictionaries
        """
        try:
            if not self.service:
                self.authenticate()

            # Get start and end of tomorrow in UTC
            tomorrow_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            tomorrow_end = tomorrow_start + timedelta(days=1)

            # Convert to RFC3339 format
            time_min = tomorrow_start.isoformat()
            time_max = tomorrow_end.isoformat()

            # Fetch events
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])
            logger.info(f"Retrieved {len(events)} events from calendar for tomorrow")

            return events

        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return []

    def get_recurring_birthdays(self, calendar_id='primary', days_ahead=0):
        """
        Get recurring birthday events (events that repeat yearly).

        Args:
            calendar_id: The calendar ID to fetch events from
            days_ahead: Number of days ahead to check (0 = today only)

        Returns:
            List of birthday event dictionaries
        """
        try:
            if not self.service:
                self.authenticate()

            # Get start and end dates in UTC
            start_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=days_ahead + 1)

            # Convert to RFC3339 format
            time_min = start_date.isoformat()
            time_max = end_date.isoformat()

            # Fetch events
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

            # Filter for recurring events (birthdays typically have recurrence rules)
            birthday_events = []
            for event in events:
                # Check if event is recurring or has birthday-related keywords
                summary = event.get('summary', '').lower()
                description = event.get('description', '').lower()

                is_recurring = 'recurrence' in event or 'recurringEventId' in event
                is_birthday = 'birthday' in summary or 'birthday' in description or 'bday' in summary

                if is_recurring or is_birthday:
                    birthday_events.append(event)

            logger.info(f"Found {len(birthday_events)} birthday/recurring events")
            return birthday_events

        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return []

    def parse_reminders(self, events):
        """
        Parse calendar events into reminder objects.

        Args:
            events: List of calendar event dictionaries

        Returns:
            List of reminder dictionaries with name, date, and phone
        """
        reminders = []

        for event in events:
            summary = event.get('summary', 'Unnamed Event')
            description = event.get('description', '')
            start = event.get('start', {})

            # Extract date
            date_str = start.get('date') or start.get('dateTime', '')

            # Try to extract phone number from description
            phone = self._extract_phone_from_description(description)

            # Extract name from summary (e.g., "John's Birthday" -> "John")
            name = self._extract_name_from_summary(summary)

            reminders.append({
                'name': name,
                'date': date_str,
                'phone': phone,
                'event_summary': summary,
                'event_id': event.get('id'),
                'description': description
            })

        return reminders

    def _extract_phone_from_description(self, description):
        """
        Extract phone number from event description.
        Looks for patterns like 'phone: +1234567890' or just '+1234567890'

        Args:
            description: Event description text

        Returns:
            Phone number string or empty string
        """
        import re

        if not description:
            return ''

        # Look for phone: prefix
        phone_match = re.search(r'phone:\s*(\+?\d[\d\s\-\(\)]+)', description, re.IGNORECASE)
        if phone_match:
            # Clean up the phone number (remove spaces, dashes, parentheses)
            phone = re.sub(r'[\s\-\(\)]', '', phone_match.group(1))
            return phone

        # Look for phone number patterns (with +country code)
        phone_match = re.search(r'\+\d{1,3}\d{7,14}', description)
        if phone_match:
            return phone_match.group(0)

        return ''

    def _extract_name_from_summary(self, summary):
        """
        Extract person's name from event summary.
        Handles formats like "John's Birthday", "Birthday - Jane", "Mike Birthday"

        Args:
            summary: Event summary text

        Returns:
            Extracted name or original summary
        """
        import re

        # Pattern: "Name's Birthday" or "Name's Bday"
        match = re.match(r"^(.+?)'s\s+(birthday|bday|b-day)", summary, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Pattern: "Birthday - Name" or "Birthday: Name"
        match = re.match(r"^(?:birthday|bday|b-day)\s*[-:]\s*(.+)$", summary, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Pattern: "Name Birthday"
        match = re.match(r"^(.+?)\s+(?:birthday|bday|b-day)$", summary, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Return original summary if no pattern matches
        return summary
