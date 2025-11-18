"""
Reminder checker module for checking and sending reminders.
Designed to run as a one-time execution (perfect for cron jobs, GitHub Actions, etc.)
"""

import logging

logger = logging.getLogger(__name__)


class ReminderChecker:
    """Checker for finding and sending reminders."""

    def __init__(self, google_client, whatsapp_client, calendar_id='primary'):
        """
        Initialize the reminder checker.

        Args:
            google_client: GoogleCalendarClient instance
            whatsapp_client: WhatsAppSender instance
            calendar_id: Google Calendar ID to monitor (default: 'primary')
        """
        self.google_client = google_client
        self.whatsapp_client = whatsapp_client
        self.calendar_id = calendar_id

    def check_and_send_reminders(self):
        """Check for today's reminders and send WhatsApp messages."""
        logger.info("Starting reminder check for TODAY...")

        try:
            # Get today's events from Google Calendar
            events = self.google_client.get_today_events(
                calendar_id=self.calendar_id
            )

            if not events:
                logger.info("No events found for today")
                return

            # Parse events into reminders
            reminders = self.google_client.parse_reminders(events)
            logger.info(f"Found {len(reminders)} reminders for today")

            # Send WhatsApp messages to default recipient
            results = self.whatsapp_client.send_bulk_reminders(reminders)
            logger.info(f"Sent {results['success']} reminders successfully, {results['failed']} failed")

        except Exception as e:
            logger.error(f"Error during reminder check: {e}", exc_info=True)
            raise

    def check_and_send_tomorrow_reminders(self):
        """Check for tomorrow's reminders and send WhatsApp messages."""
        logger.info("Starting reminder check for TOMORROW...")

        try:
            # Get tomorrow's events from Google Calendar
            events = self.google_client.get_tomorrow_events(
                calendar_id=self.calendar_id
            )

            if not events:
                logger.info("No events found for tomorrow")
                return

            # Parse events into reminders
            reminders = self.google_client.parse_reminders(events)
            logger.info(f"Found {len(reminders)} reminders for tomorrow")

            # Send WhatsApp messages to default recipient for tomorrow
            results = self.whatsapp_client.send_bulk_reminders(reminders, when="tomorrow")
            logger.info(f"Sent {results['success']} tomorrow reminders successfully, {results['failed']} failed")

        except Exception as e:
            logger.error(f"Error during tomorrow's reminder check: {e}", exc_info=True)
            raise
