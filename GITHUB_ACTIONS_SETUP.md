# GitHub Actions Setup Guide

This guide will help you deploy the Birthday Reminder App to GitHub Actions for **completely free** automated reminders.

## Why GitHub Actions?

- ✅ **100% Free** - No cost at all
- ✅ **Reliable** - Runs on GitHub's infrastructure
- ✅ **No server management** - GitHub handles everything
- ✅ **Automatic scheduling** - Runs at specified times daily
- ✅ **Easy to monitor** - View logs in GitHub Actions tab

## Architecture

The app runs as **three separate scheduled workflows**:

1. **Today's Reminders** - Runs at 9:00 AM IST daily
2. **Tomorrow's Reminders** - Runs at 9:00 PM IST daily
3. **Keep-Alive** - Runs on the 1st of every month (keeps repo active)

Each reminder workflow:
- Checks out your code
- Installs dependencies
- Authenticates with Google Calendar
- Sends WhatsApp reminders via Twilio
- Uploads logs as artifacts

The keep-alive workflow:
- Updates a timestamp file (`LAST_ACTIVE.txt`) monthly
- Commits and pushes the change automatically
- Prevents GitHub from disabling scheduled workflows (60-day inactivity rule)
- Runs completely in the background - no action needed from you!

## Setup Instructions

### 1. Fork or Create Repository

1. Create a new repository on GitHub (can be private)
2. Push your code to the repository:

```bash
cd birthday_reminder
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 2. Set Up Google Calendar API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the **Google Calendar API**
4. Create **OAuth 2.0 credentials** (Desktop app)
5. Download the credentials JSON file
6. **Copy the entire contents** of the credentials JSON file (you'll need this for GitHub Secrets)

### 3. Set Up Twilio WhatsApp

1. Sign up at [Twilio](https://www.twilio.com/try-twilio)
2. Get your **Account SID** and **Auth Token**
3. Set up WhatsApp Sandbox
4. Note your **Twilio WhatsApp number** (e.g., +14155238886)

### 4. Configure GitHub Secrets

Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add the following secrets:

#### Required Secrets:

| Secret Name | Value | Example |
|-------------|-------|---------|
| `TWILIO_ACCOUNT_SID` | Your Twilio Account SID | ACxxxxxxxxxxxxxxxxx |
| `TWILIO_AUTH_TOKEN` | Your Twilio Auth Token | your_auth_token |
| `TWILIO_WHATSAPP_NUMBER` | Your Twilio WhatsApp number (sender) | +14155238886 |
| `DEFAULT_RECIPIENT_NUMBER` | Your phone number to receive reminders | +1234567890 |
| `GOOGLE_CREDENTIALS` | **Entire contents** of Google credentials.json | `{"installed":{"client_id":"...","project_id":"...",...}}` |

#### Optional Secrets:

| Secret Name | Value | Default |
|-------------|-------|---------|
| `GOOGLE_CALENDAR_ID` | Calendar ID to monitor | primary |

**IMPORTANT for `GOOGLE_CREDENTIALS`:**
- Copy the ENTIRE JSON file content
- It should start with `{"installed":{"client_id"...`
- Include ALL curly braces, quotes, and commas
- Paste the entire thing into the GitHub Secret value field

### 5. Enable GitHub Actions

1. Go to your repository → **Actions** tab
2. If prompted, click **"I understand my workflows, go ahead and enable them"**
3. You should see three workflows:
   - "Today's Reminders"
   - "Tomorrow's Reminders"
   - "Keep Alive"

### 6. First-Time Authentication

**IMPORTANT:** GitHub Actions cannot open a browser for OAuth, so you need to authenticate locally first:

```bash
# On your local machine
cd birthday_reminder
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create config directory
mkdir -p config

# Copy your Google credentials
cp /path/to/downloaded/credentials.json config/credentials.json

# Run the app once to authenticate
python main.py --check today
```

This will:
1. Open a browser for Google OAuth
2. Create `config/token.json` with your authentication token

### 7. Add Token to GitHub Secrets

After authenticating locally:

1. Open `config/token.json`
2. Copy the ENTIRE contents
3. Go to GitHub Secrets
4. Create a new secret named `GOOGLE_TOKEN`
5. Paste the token JSON content

**Update the workflow files** to use the token:

Add this step after "Setup Google credentials" in both workflow files:

```yaml
- name: Setup Google token
  env:
    GOOGLE_TOKEN: ${{ secrets.GOOGLE_TOKEN }}
  run: |
    echo "$GOOGLE_TOKEN" > config/token.json
```

### 8. Test the Workflows

#### Manual Test:

1. Go to **Actions** tab
2. Select "Today's Reminders" workflow
3. Click **"Run workflow"** dropdown
4. Click **"Run workflow"** button
5. Wait for the workflow to complete
6. Check the logs

#### Check Logs:

1. Click on the workflow run
2. Click on the job name
3. Expand each step to see output
4. Download logs artifact if needed

## Customizing Schedule Times

The workflows run at:
- **Today's Reminders**: 3:30 AM UTC = 9:00 AM IST
- **Tomorrow's Reminders**: 3:30 PM UTC = 9:00 PM IST

### To change the schedule:

Edit `.github/workflows/today-reminders.yml` or `.github/workflows/tomorrow-reminders.yml`:

```yaml
on:
  schedule:
    - cron: '30 3 * * *'  # Change this line
```

**Cron syntax:** `minute hour day month weekday`

Examples:
- `'0 0 * * *'` = Midnight UTC
- `'30 14 * * *'` = 2:30 PM UTC (8:00 PM IST)
- `'0 12 * * 1'` = Noon UTC every Monday

**Convert your time to UTC:**
- IST = UTC + 5:30
- To run at X:00 IST, use (X - 5):30 UTC
- Example: 9:00 AM IST = 3:30 AM UTC

## Monitoring

### View Workflow Status:

1. Go to **Actions** tab
2. See all workflow runs with status (✅ Success, ❌ Failed)
3. Click on any run to see detailed logs

### Download Logs:

1. Go to a completed workflow run
2. Scroll to **Artifacts** section
3. Download `today-reminder-logs` or `tomorrow-reminder-logs`

### Enable Email Notifications:

GitHub will email you if a workflow fails. Configure in:
**Settings** → **Notifications** → **Actions**

## Troubleshooting

### Workflow Fails with "Missing environment variables"

- Check that all GitHub Secrets are created correctly
- Secret names must match exactly (case-sensitive)
- Re-save secrets if needed

### Workflow Fails with "Could not authenticate with Google"

- Ensure `GOOGLE_CREDENTIALS` contains the FULL JSON content
- Make sure you've added `GOOGLE_TOKEN` secret (after local auth)
- Check that Google Calendar API is enabled

### No Reminders Sent

- Verify events exist in your calendar for today/tomorrow
- Ensure DEFAULT_RECIPIENT_NUMBER is set correctly in GitHub Secrets
- Review logs for detailed error messages

### Twilio Errors

- Verify Account SID and Auth Token are correct
- Check that WhatsApp Sandbox is set up
- Ensure recipients have joined your WhatsApp Sandbox

## Understanding the Keep-Alive Workflow

### What is it?

The **Keep-Alive workflow** is a smart automation that prevents GitHub from disabling your scheduled workflows.

### Why is it needed?

GitHub has a policy: **Scheduled workflows are automatically disabled after 60 days of no repository activity.** To prevent this, the keep-alive workflow creates minimal activity monthly.

### What does it do?

Every 1st of the month at midnight UTC, it:
1. Updates a file called `LAST_ACTIVE.txt` with the current timestamp
2. Commits this change automatically
3. Pushes to your repository

### What you'll see:

**Monthly automated commits:**
```
chore: keep repository active [skip ci]
by github-actions[bot]
```

**A file in your repo:**
```
LAST_ACTIVE.txt
```

### Is this normal?

✅ **Yes!** This is completely normal and expected.

✅ These commits are intentional and keep your workflows running.

✅ The `[skip ci]` tag means this commit won't trigger other workflows unnecessarily.

### Benefits:

- 🔄 **Set it and forget it** - Never worry about the 60-day rule
- 📅 **Only 12 commits per year** - Minimal impact on your repo
- 🤖 **Fully automatic** - No manual intervention needed
- 🎯 **Non-intrusive** - Just updates a timestamp file

### Can I disable it?

Yes, but not recommended. If you disable it, you'll need to manually trigger any workflow or make a commit every 60 days to keep your reminder workflows active.

To disable: Delete `.github/workflows/keep-alive.yml`

## Cost

**GitHub Actions is FREE for:**
- Public repositories: Unlimited minutes
- Private repositories: 2,000 minutes/month (way more than needed)

**This app uses approximately:**
- 2 minutes per day (2 reminder workflow runs)
- 1 minute per month (keep-alive workflow)
- **Total: ~61 minutes per month**
- Well within free tier limits!

## Security Notes

- ✅ Secrets are encrypted by GitHub
- ✅ Never commit credentials to the repository
- ✅ Workflows run in isolated containers
- ✅ Logs are automatically cleaned after retention period

## Next Steps

1. Create any calendar events - ALL events will trigger reminders
2. Test both workflows manually
3. Wait for scheduled runs
4. Monitor the Actions tab
5. Enjoy automated reminders!

## Support

If you encounter issues:
1. Check workflow logs for errors
2. Verify all secrets are set correctly
3. Test locally first: `python main.py --check today`
4. Review Google Calendar and Twilio configurations
