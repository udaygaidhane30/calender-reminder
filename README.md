# Calender Reminder App

An automated reminder application that scrapes data from Google Calendar and sends WhatsApp messages via Twilio API. Perfect for birthday reminders, anniversaries, or any recurring date-based notifications.

**🚀 Deploy for FREE on GitHub Actions** - No server required, completely free hosting!

## Features

- Reads ALL events from Google Calendar
- **Dual Notification System:**
  - Today's reminders (default: 9:00 AM)
  - Tomorrow's reminders (default: 9:00 PM IST)
- Sends WhatsApp messages via Twilio API
- All reminders sent to your configured phone number
- Configurable schedule and message templates
- Comprehensive logging
- Easy setup and configuration

## Deployment Options

### Option 1: GitHub Actions (Recommended) ⭐

**Best for:** Everyone - completely free, no server management required

- ✅ 100% Free (uses GitHub's free tier)
- ✅ Fully automated scheduling
- ✅ No server to maintain
- ✅ Reliable execution
- ✅ Easy to monitor with GitHub Actions logs
- ✅ **Keep-alive workflow included** - Automatically stays active, no 60-day timeout

**➡️ [Complete GitHub Actions Setup Guide](GITHUB_ACTIONS_SETUP.md)**

**About Keep-Alive:** The repository includes an automatic keep-alive workflow that updates a timestamp file monthly. This prevents GitHub from disabling your scheduled workflows due to inactivity (GitHub's 60-day rule). You'll see a `LAST_ACTIVE.txt` file and monthly automated commits - this is normal and keeps everything running smoothly!

### Option 2: Local/Server Deployment

**Best for:** Running on your own machine or server

- Run once: `python main.py --check today`
- Set up cron jobs for automation
- Requires server to stay online

## Project Structure

```
birthday_reminder/
├── .github/
│   └── workflows/
│       ├── today-reminders.yml      # GitHub Actions: Today's reminders (9 AM IST)
│       ├── tomorrow-reminders.yml   # GitHub Actions: Tomorrow's reminders (9 PM IST)
│       └── keep-alive.yml           # GitHub Actions: Keep repository active (monthly)
├── config/                          # Configuration files (credentials, tokens)
├── logs/                            # Application logs
├── src/
│   ├── __init__.py
│   ├── google_calendar.py          # Google Calendar integration
│   ├── whatsapp_sender.py          # Twilio WhatsApp integration
│   └── reminder_checker.py         # Reminder checking logic
├── main.py                         # Application entry point
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── GITHUB_ACTIONS_SETUP.md         # Detailed GitHub Actions setup guide
└── README.md                       # This file
```

## Prerequisites

1. Python 3.8 or higher
2. A Google Cloud account with Calendar API enabled
3. A Twilio account with WhatsApp enabled
4. A Google Calendar with birthday/reminder events

## Setup Instructions

### 1. Clone and Install Dependencies

```bash
# Create a virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Up Google Calendar API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app" as application type
   - Download the credentials JSON file
5. Save the downloaded file as `config/credentials.json`

### 3. Set Up Twilio WhatsApp

1. Sign up at [Twilio](https://www.twilio.com/try-twilio)
2. Get your Account SID and Auth Token from the [Twilio Console](https://console.twilio.com/)
3. Set up WhatsApp:
   - Go to Messaging > Try it out > Send a WhatsApp message
   - Follow instructions to activate your Twilio Sandbox for WhatsApp
   - Note your Twilio WhatsApp number (e.g., +14155238886)

### 4. Create Calendar Events

Create any events in your Google Calendar - ALL events will trigger reminders!

**Event Title Examples:**
- "John's Birthday"
- "Team Meeting"
- "Doctor Appointment"
- "Wedding Anniversary - Sarah"

**IMPORTANT:** The event title will be sent directly in the WhatsApp message to your configured phone number, so make it clear and descriptive!

**Tips:**
- Make events recurring (yearly) for birthdays/anniversaries
- The event title will appear directly in the WhatsApp message (e.g., "📅 Reminder: John's Birthday")
- Keep event titles concise and clear since they're sent as-is
- All reminders will be sent to your default recipient number (configured in environment variables)
- Any event in your calendar will trigger a reminder - no keyword filtering

### 5. Configure Environment Variables

```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

Fill in the following variables in `.env`:

```env
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=+14155238886
DEFAULT_RECIPIENT_NUMBER=+1234567890
GOOGLE_CALENDAR_ID=primary
```

**About `GOOGLE_CALENDAR_ID`:**
- Use `primary` for your main Google Calendar (default)
- To monitor a specific calendar:
  1. Open Google Calendar settings
  2. Click on the calendar you want to monitor
  3. Scroll to "Integrate calendar"
  4. Copy the "Calendar ID" (looks like: `abc123@group.calendar.google.com`)
- ALL events from this calendar will trigger reminders

### 6. First Run Authentication

On first run, the app will open a browser window for Google OAuth:

```bash
# Activate virtual environment
source venv/bin/activate

# Run authentication
python main.py --check today
```

1. Select your Google account
2. Grant access to view your Google Calendar
3. The authentication token will be saved to `config/token.json`

**Note:** You may see a warning that the app is not verified. Click "Advanced" and "Go to [app name] (unsafe)" to proceed. This is normal for personal projects.

## Usage

### For GitHub Actions Deployment

**See [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md)** for complete deployment instructions.

Once set up on GitHub Actions:
- **Automatic execution** at 9 AM IST (today's reminders)
- **Automatic execution** at 9 PM IST (tomorrow's reminders)
- **No maintenance required**
- **View logs** in GitHub Actions tab

### For Local/Manual Execution

```bash
# Activate virtual environment
source venv/bin/activate

# Check and send today's reminders
python main.py --check today

# Check and send tomorrow's reminders
python main.py --check tomorrow
```

The app will:
1. Authenticate with Google Calendar
2. Fetch ALL events for today or tomorrow
3. Send WhatsApp reminders to your configured number:
   - For today: "📅 Reminder: John's Birthday"
   - For tomorrow: "📅 Reminder: John's Birthday is tomorrow!"
4. Exit when complete

### Automate with Cron (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add these lines (adjust paths):
# Today's reminders at 9 AM
30 3 * * * cd /path/to/birthday_reminder && /path/to/venv/bin/python main.py --check today

# Tomorrow's reminders at 9 PM
30 15 * * * cd /path/to/birthday_reminder && /path/to/venv/bin/python main.py --check tomorrow
```

## Configuration

### Environment Variables

**Required:**
- `TWILIO_ACCOUNT_SID`: Your Twilio Account SID
- `TWILIO_AUTH_TOKEN`: Your Twilio Auth Token
- `TWILIO_WHATSAPP_NUMBER`: Your Twilio WhatsApp number (sender)
- `DEFAULT_RECIPIENT_NUMBER`: Your phone number to receive reminders (include country code)

**Optional:**
- `GOOGLE_CALENDAR_ID`: Calendar to monitor (default: primary)

**Note:** For GitHub Actions deployment, set these as GitHub Secrets. See [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md) for details.

### Message Format

The WhatsApp message will contain the calendar event title directly:

**For today's events:**
```
📅 Reminder: John's Birthday
```

**For tomorrow's events:**
```
📅 Reminder: John's Birthday is tomorrow!
```

So make sure your calendar event titles are clear and descriptive!

### Customizing Messages

To customize the WhatsApp message template, edit `src/whatsapp_sender.py:77-80`.

Current format:
```python
if when.lower() == "tomorrow":
    message = f"📅 Reminder: {event_title} is tomorrow!"
else:
    message = f"📅 Reminder: {event_title}"
```

You can change it to anything you like, for example:
```python
if when.lower() == "tomorrow":
    message = f"🎉 Heads up! {event_title} is tomorrow!"
else:
    message = f"🎉 Today's the day: {event_title}!"
```

## Logs

Logs are stored in:
- Console output (colored)
- `logs/reminder_app.log` (file)

## Troubleshooting

### Google Authentication Issues

- Ensure `config/credentials.json` exists and is valid
- Delete `config/token.json` and re-authenticate
- Check that Google Calendar API is enabled in your project
- Make sure you granted "View your calendars" permission during OAuth

### Twilio/WhatsApp Issues

- Verify your Account SID and Auth Token are correct
- Ensure recipients have joined your WhatsApp Sandbox (for testing)
- Check that phone numbers include country codes (e.g., +1234567890)
- For production, request Twilio WhatsApp Business approval

### No Reminders Sent

- Verify your calendar ID is correct
- Check that DEFAULT_RECIPIENT_NUMBER is set correctly in your `.env` file
- Verify events are scheduled for today's date
- Review logs for detailed error messages

### Events Not Being Found

- Check that events are on the correct calendar (if not using `primary`)
- Verify the calendar is not hidden or disabled
- Ensure you're checking the right date (today vs tomorrow)

## Running as a Service

### Linux (systemd)

Create `/etc/systemd/system/birthday-reminder.service`:

```ini
[Unit]
Description=Birthday Reminder App
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/birthday_reminder
Environment="PATH=/path/to/birthday_reminder/venv/bin"
ExecStart=/path/to/birthday_reminder/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable birthday-reminder
sudo systemctl start birthday-reminder
```
