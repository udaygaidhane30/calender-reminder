# Encrypted Token Setup Guide

This guide shows you how to set up auto-refreshing OAuth tokens **without sharing your calendar** with anyone.

## How It Works

1. Your OAuth token is encrypted and stored in the repository
2. GitHub Actions decrypts it on each run
3. If the token expires and gets refreshed, it's automatically re-encrypted and committed back
4. **No calendar sharing required** - you keep full control!

## Benefits

- ✅ No need to share calendar with service account
- ✅ Token automatically refreshes when expired
- ✅ Secure - token is encrypted in the repo
- ✅ Zero maintenance after setup
- ✅ Works with your existing OAuth credentials

## Setup Instructions

### Step 1: Install Dependencies

```bash
cd birthday_reminder
pip install -r requirements.txt
```

This installs the `cryptography` package needed for token encryption.

### Step 2: Generate Encryption Key

```bash
python scripts/token_manager.py generate-key
```

This will output an encryption key that looks like:
```
VGhpc0lzQW5FeGFtcGxlS2V5Rm9yRW5jcnlwdGlvbg==
```

**IMPORTANT:** Copy this key! You'll need it in the next step.

### Step 3: Add Encryption Key to GitHub Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `TOKEN_ENCRYPTION_KEY`
5. Value: Paste the key from Step 2
6. Click **Add secret**

### Step 4: Authenticate and Get Your Token

If you haven't already authenticated locally:

```bash
cd birthday_reminder
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Create config directory
mkdir -p config

# Copy your OAuth credentials
# (You should already have this from initial setup)
# If not, download from Google Cloud Console and save as config/credentials.json

# Run authentication
python main.py --check today
```

This will:
1. Open a browser for Google OAuth
2. Create `config/token.json` after you authenticate

### Step 5: Encrypt Your Token

```bash
# Using the encryption key from Step 2
python scripts/token_manager.py encrypt config/token.json config/token.encrypted YOUR_ENCRYPTION_KEY_HERE
```

**Example:**
```bash
python scripts/token_manager.py encrypt config/token.json config/token.encrypted "VGhpc0lzQW5FeGFtcGxlS2V5Rm9yRW5jcnlwdGlvbg=="
```

This creates `config/token.encrypted` - an encrypted version of your token.

### Step 6: Commit Encrypted Token to Repository

```bash
# Add the encrypted token to git
git add config/token.encrypted

# Commit it
git commit -m "Add encrypted Google OAuth token"

# Push to GitHub
git push
```

**Note:** The encrypted token is safe to commit to your repository. Without the encryption key (stored in GitHub Secrets), it cannot be decrypted.

### Step 7: Test the Workflows

The main workflows have been updated to use encrypted tokens automatically!

1. Go to **Actions** tab in GitHub
2. Select "Today's Reminders" workflow
3. Click **Run workflow**
4. Check the logs

You should see:
```
✓ Token decrypted successfully
```

If the token was refreshed during the run, you'll also see:
```
✓ Token was refreshed during this run
✓ Refreshed token encrypted and committed to repository
```

## How Token Auto-Refresh Works

1. **Workflow starts** → Decrypts `config/token.encrypted` to `config/token.json`
2. **App runs** → Uses token to access calendar
3. **Token expired?** → Code automatically refreshes it using refresh token
4. **After app finishes** → Checks if token was modified
5. **If refreshed** → Re-encrypts and commits back to repository
6. **Next run** → Uses the updated token

## Security

### What's Encrypted?
The `config/token.encrypted` file in your repository contains:
- Your access token (expires in ~1 hour, auto-refreshed)
- Your refresh token (long-lived, used to get new access tokens)
- Token metadata

### Is It Safe?
**Yes!** The encryption key is:
- Stored only in GitHub Secrets (never in the repository)
- Never exposed in logs or commits
- Required to decrypt the token
- Using industry-standard Fernet encryption (AES-128 CBC)

Without the `TOKEN_ENCRYPTION_KEY`, the encrypted file is useless to anyone.

### Who Can Access?
- **You** - As the repository owner
- **GitHub Actions** - Only your workflows with proper permissions
- **Nobody else** - Even if someone gets the encrypted file, they can't decrypt it

## Troubleshooting

### "No encrypted token found" in workflow logs

**Solution:** Make sure you completed Step 6 and pushed `config/token.encrypted` to GitHub.

```bash
# Check if file exists
ls -la config/token.encrypted

# If not, re-run Step 5 and Step 6
```

### "Decryption failed" or "Invalid token"

**Solution:** The encryption key doesn't match. Make sure:
1. The key in GitHub Secret `TOKEN_ENCRYPTION_KEY` is correct
2. You used the same key to encrypt the token (Step 5)
3. Try regenerating: delete `config/token.encrypted`, re-run Steps 2, 5, 6

### Token refresh not committing back

**Solution:** Check workflow permissions:
1. Go to **Settings** → **Actions** → **General**
2. Scroll to "Workflow permissions"
3. Select "Read and write permissions"
4. Click **Save**

### "Permission denied" when pushing

**Solution:** Same as above - enable write permissions for GITHUB_TOKEN.

## Rotating Encryption Keys

For extra security, you can rotate your encryption key periodically:

```bash
# 1. Generate new key
python scripts/token_manager.py generate-key

# 2. Get current token (decrypt with old key)
python scripts/token_manager.py decrypt config/token.encrypted config/token.json OLD_KEY

# 3. Encrypt with new key
python scripts/token_manager.py encrypt config/token.json config/token.encrypted NEW_KEY

# 4. Update GitHub Secret TOKEN_ENCRYPTION_KEY with new key

# 5. Commit and push
git add config/token.encrypted
git commit -m "chore: rotate token encryption key"
git push
```

Recommended: Rotate every 90 days.

## Comparison: This vs Service Account

| Feature | Encrypted Token (This) | Service Account |
|---------|----------------------|-----------------|
| Calendar sharing | Not required | Required |
| Setup complexity | Medium | Medium |
| Maintenance | None (auto-refresh) | None |
| Security | High (encrypted) | High |
| Token expiration | Auto-handled | Never expires |
| Privacy | Full (your account) | Full (delegated) |

## Files Modified

This setup added:
- `scripts/token_manager.py` - Encryption/decryption tool
- `.github/workflows/*-encrypted.yml` - New workflows with auto-refresh
- `config/token.encrypted` - Your encrypted token (committed to repo)

This setup keeps (unchanged):
- `config/credentials.json` - OAuth client credentials (local only, in .gitignore)
- `config/token.json` - Plain token (local only, in .gitignore)

## GitHub Secrets Required

After setup, you need these secrets:

1. **Required secrets:**
   - `TOKEN_ENCRYPTION_KEY` - For decrypting the token
   - `GOOGLE_CREDENTIALS` - OAuth credentials from Google Cloud Console
   - `TWILIO_ACCOUNT_SID` - Your Twilio Account SID
   - `TWILIO_AUTH_TOKEN` - Your Twilio Auth Token
   - `TWILIO_WHATSAPP_NUMBER` - Your Twilio WhatsApp number
   - `DEFAULT_RECIPIENT_NUMBER` - Your phone number

2. **No longer needed** (can be removed):
   - `GOOGLE_TOKEN` - Replaced by encrypted token in repository

## Need Help?

Check these files:
- `TOKEN_EXPIRATION_SOLUTIONS.md` - Overview of all solutions
- `GITHUB_ACTIONS_SETUP.md` - General GitHub Actions setup
- `.github/workflows/*-encrypted.yml` - Workflow configuration
