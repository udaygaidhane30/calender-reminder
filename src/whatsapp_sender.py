"""
WhatsApp message sender module using Twilio API.
Handles sending WhatsApp messages for reminders.
"""

import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import logging

logger = logging.getLogger(__name__)


class WhatsAppSender:
    """Client for sending WhatsApp messages via Twilio."""

    def __init__(self, account_sid=None, auth_token=None, from_number=None, default_recipient=None):
        """
        Initialize the WhatsApp sender.

        Args:
            account_sid: Twilio account SID
            auth_token: Twilio auth token
            from_number: Twilio WhatsApp-enabled phone number
            default_recipient: Default phone number to send reminders to
        """
        self.account_sid = account_sid or os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = auth_token or os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = from_number or os.getenv('TWILIO_WHATSAPP_NUMBER')
        self.default_recipient = default_recipient or os.getenv('DEFAULT_RECIPIENT_NUMBER')

        if not all([self.account_sid, self.auth_token, self.from_number]):
            raise ValueError("Twilio credentials are required")

        self.client = Client(self.account_sid, self.auth_token)
        logger.info("WhatsApp sender initialized")

    def send_message(self, to_number, message):
        """
        Send a WhatsApp message.

        Args:
            to_number: Recipient's phone number (with country code)
            message: Message text to send

        Returns:
            Message SID if successful, None otherwise
        """
        try:
            # Ensure numbers are in WhatsApp format
            from_whatsapp = f"whatsapp:{self.from_number}"
            to_whatsapp = f"whatsapp:{to_number}" if not to_number.startswith('whatsapp:') else to_number

            message_obj = self.client.messages.create(
                body=message,
                from_=from_whatsapp,
                to=to_whatsapp
            )

            logger.info(f"Message sent successfully to {to_number}. SID: {message_obj.sid}")
            return message_obj.sid

        except TwilioRestException as e:
            logger.error(f"Failed to send message to {to_number}: {e}")
            return None

    def send_reminder(self, event_title, phone=None, when="today"):
        """
        Send a reminder message.

        Args:
            event_title: The calendar event title/summary
            phone: Phone number to send to (uses default_recipient if not provided)
            when: When the event is - "today" or "tomorrow" (default: "today")

        Returns:
            Message SID if successful, None otherwise
        """
        # Use default recipient if phone not provided
        recipient = phone or self.default_recipient

        if not recipient:
            logger.error(f"No recipient number specified for '{event_title}' and no default recipient configured")
            return None

        if when.lower() == "tomorrow":
            message = f"📅 Reminder: {event_title} is tomorrow!"
        else:
            message = f"📅 Reminder: {event_title}"

        return self.send_message(recipient, message)

    def send_bulk_reminders(self, reminders, when="today"):
        """
        Send multiple reminder messages.

        Args:
            reminders: List of reminder dictionaries with 'event_summary' and optional 'phone'
            when: When the events are - "today" or "tomorrow" (default: "today")

        Returns:
            Dictionary with success and failure counts
        """
        results = {'success': 0, 'failed': 0, 'messages': []}

        for reminder in reminders:
            event_title = reminder.get('event_summary', 'Event Reminder')
            phone = reminder.get('phone')  # Optional - will use default if not provided

            sid = self.send_reminder(event_title, phone, when=when)

            if sid:
                recipient = phone or self.default_recipient
                results['success'] += 1
                results['messages'].append({'event': event_title, 'phone': recipient, 'sid': sid})
            else:
                results['failed'] += 1

        logger.info(f"Bulk send complete: {results['success']} successful, {results['failed']} failed")
        return results
