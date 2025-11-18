"""
Birthday Reminder App - Main Entry Point
Scrapes data from Google Calendar and sends WhatsApp reminders via Twilio.
Designed to run as a one-time job (perfect for GitHub Actions, cron, etc.)
"""

import os
import sys
import logging
import argparse
from dotenv import load_dotenv
import colorlog

from src.google_calendar import GoogleCalendarClient
from src.whatsapp_sender import WhatsAppSender
from src.reminder_checker import ReminderChecker


def setup_logging():
    """Configure logging with colors."""
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    ))

    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    # Also log to file
    file_handler = logging.FileHandler('logs/reminder_app.log')
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    logger.addHandler(file_handler)


def main():
    """Main application entry point."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Birthday Reminder App - Send WhatsApp reminders from Google Calendar')
    parser.add_argument('--check', choices=['today', 'tomorrow'], required=True,
                        help='Check for today\'s or tomorrow\'s events')
    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info(f"Starting Birthday Reminder App - Checking {args.check}'s events...")

    # Validate environment variables
    required_env_vars = [
        'TWILIO_ACCOUNT_SID',
        'TWILIO_AUTH_TOKEN',
        'TWILIO_WHATSAPP_NUMBER',
        'DEFAULT_RECIPIENT_NUMBER'
    ]

    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please check your .env file or GitHub Secrets")
        sys.exit(1)

    try:
        # Initialize Google Calendar client
        logger.info("Initializing Google Calendar client...")
        google_client = GoogleCalendarClient()
        google_client.authenticate()

        # Initialize WhatsApp sender
        logger.info("Initializing WhatsApp sender...")
        whatsapp_client = WhatsAppSender()

        # Get configuration
        calendar_id = os.getenv('GOOGLE_CALENDAR_ID', 'primary')

        logger.info(f"Monitoring calendar: {calendar_id}")

        # Initialize reminder checker
        checker = ReminderChecker(
            google_client=google_client,
            whatsapp_client=whatsapp_client,
            calendar_id=calendar_id
        )

        # Run the appropriate check
        if args.check == 'today':
            logger.info("Running today's reminder check...")
            checker.check_and_send_reminders()
        else:
            logger.info("Running tomorrow's reminder check...")
            checker.check_and_send_tomorrow_reminders()

        logger.info("Reminder check completed successfully!")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
