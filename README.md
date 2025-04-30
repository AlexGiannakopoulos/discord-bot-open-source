# 🤖 discord-bot-open-source 🚀

### A general use discord bot for a university project

# Setting Up Your Discord Utility Bot

This guide will walk you through the process of setting up your Discord utility bot with all the requested features.

## Prerequisites

- Python 3.8 or higher
- A Discord account
- Basic knowledge of Python and Discord

## Step 1: Create a Discord Application and Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" tab and click "Add Bot"
4. Under the "Privileged Gateway Intents" section, enable:
   - Presence Intent
   - Server Members Intent
   - Message Content Intent
5. Copy your bot token (you'll need this later)
6. Go to the "OAuth2" tab, then "URL Generator"
7. Select the following scopes:
   - `bot`
   - `applications.commands`
8. Select the following bot permissions:
   - Send Messages
   - Embed Links
   - Read Message History
   - Add Reactions
   - Use External Emojis
   - Manage Messages
9. Copy the generated URL and open it in your browser to invite the bot to your server

## Step 2: Get API Keys

For the GIF command, you'll need a Tenor API key:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Tenor API
4. Create an API key
5. Copy your API key (you'll need this later)

## Step 3: Set Up Your Development Environment

1. Create a new directory for your bot
2. Install the required packages:

```bash
pip install discord.py python-dotenv pytz pillow httpx asyncio apscheduler
```

3. Create the following files in your project directory:

- `main.py` - The main bot file combining all the code we've provided
- `.env` - Environment variables file (using the template provided)

4. Fill in your `.env` file with the tokens and API keys you obtained earlier:

```
DISCORD_TOKEN=your_discord_bot_token_here
TENOR_API_KEY=your_tenor_api_key_here
```

5. Create a `data` folder in your project directory to store event and subscription data

## Step 4: Run Your Bot

1. Run your bot using the following command:

```bash
python main.py
```

2. Your bot should now be online and ready to use!

## Command Usage

Here's how to use each of the commands implemented in your bot:

### GIF Command
- `!gif [search term]` - Send a GIF related to your search term

### Dice Roller
- `!roll [dice notation]` - Roll dice using standard notation (e.g., `!roll 2d6+3`)

### Time Converter
- `!convert [time] [from_timezone] [to_timezone]` - Convert time between timezones
  - Example: `!convert 3:30 PM US/Eastern Europe/London`
- `!alltime [time] [from_timezone]` - Show time in all major timezones
  - Example: `!alltime 14:30 US/Pacific`

### Server commands
- `!stats` - Show detailed server statistics
- `!create-channel` - Create a new text channel with the name u specify if u have the role "admin"

### Calendar/Event Scheduler
- `!addevent [name] [date] [time] [description]` - Add an event
  - Example: `!addevent Meeting 2025-05-15 14:30 Weekly team meeting`
- `!events` - List all upcoming events
- `!delevent [event_id]` - Delete an event by its ID

### Subscription Tracker
- `!addsub [name] [amount] [due_date] [notes]` - Add a subscription
  - Example: `!addsub Netflix 15.99 2025-04-30 Family plan`
- `!subs` - List all your active subscriptions
- `!delsub [sub_id]` - Delete a subscription by its ID
- `!renewsub [sub_id]` - Mark a subscription as paid and update the next due date

### Help Command
- `!help` - Show all available commands and how to use them
- `!devhelp` -Show all commands created with this app in better format 😊

## Customization

Feel free to customize your bot further:

- Modify the command prefixes (default is `!`)
- Add new commands or extend existing ones
- Customize embed colors and designs
- Add more timezones to the time converter
- Implement additional features like custom reminders or message purging

## File Structure

Your complete bot project should have this structure:

```
discord-bot/
├── cogs/
    ├── __init__.py
    ├── calendar_func.py
    ├── convert_time.py
    ├── data.py
    ├── gif.py
    ├── roll_dice.py
    ├── stats.py
    └── subscriptions.py
├── main.py
├── .env
└── data/
    ├── events.json
    └── subscriptions.json
```

## Troubleshooting

- If your bot doesn't come online, check if your Discord token is correct
- If the GIF command doesn't work, verify your Tenor API key
- For permission errors, make sure your bot has the necessary permissions in the server
- If events or subscriptions aren't saving, check if the `data` directory exists and is writable
- If your problem isn't fixed, feel free to create a bug report on tab [Issues](https://github.com/AlexGiannakopoulos/discord-bot-open-source/issues)
- For any other questions feel free to contact me on Discord 😂 @neverlookback
