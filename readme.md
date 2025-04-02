# Bearcats Racing Discord Bot

A specialized Discord bot designed for the Bearcats Racing team server to streamline communication and enhance productivity.

## Features

### Message Summarization
- Automatically summarizes long discussions and threads
- Creates concise digests of important conversations
- Highlights key decisions and action items from meeting channels

### Meeting Scheduler
- Seamlessly integrates with Outlook calendars
- Creates and manages team meeting events
- Sends reminders and meeting links to relevant team members
- Prevents scheduling conflicts with existing team events

### Product Research Assistant
- Web scraping capabilities to find racing components and equipment
- Compares prices across multiple vendors
- Provides technical specifications and compatibility information
- Tracks price changes and availability for critical parts

## Setup Instructions

1. Clone this repository
2. Install required dependencies: `npm install`
3. Configure environment variables (see `.env.example`)
4. Set up Outlook API credentials
5. Run the bot: `npm start`

## Commands

| Command | Description |
|---------|-------------|
| `!summarize` | Summarizes the last 50 messages in the channel |
| `!schedule` | Creates a new meeting event in Outlook |
| `!lookup <item>` | Searches for racing components across vendors |

## Technologies Used
- python
- discord api
- Microsoft Graph API (for Outlook integration)
- serper / crewai (for web scraping)

## Contributing
Interested in contributing? Check out our [contribution guidelines](CONTRIBUTING.md).

## License
MIT