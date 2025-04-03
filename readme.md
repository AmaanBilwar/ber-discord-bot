# Bearcats Racing Discord Bot

A specialized Discord bot designed for the Bearcats Racing team server to streamline communication and enhance productivity.

## Features

### Message Summarization
- Automatically summarizes long discussions and threads
- Creates concise digests of important conversations
- Highlights key decisions and action items from meeting channels

### Product Research Assistant
- Web scraping capabilities to find racing components and equipment
- Compares prices across multiple vendors
- Provides technical specifications and compatibility information
- Tracks price changes and availability for critical parts

### Meeting Scheduler
- Seamlessly integrates with Outlook calendars
- Creates and manages team meeting events
- Sends reminders and meeting links to relevant team members
- Prevents scheduling conflicts with existing team events


## Setup Instructions

1. Clone this repository
2. Install required dependencies: `pip -r install requirements.txt`
3. Configure environment variables (see `.env.example`)
4. Set up Outlook API credentials
5. Run the bot: `python backend/app.py`

## Commands

| Command | Description |
|---------|-------------|
| `/summarize <years/months/days/hours> ` | Specify the time period youre trying to summarize |
| `/lookup <item>` | Searches for racing components across vendors |
| `/schedule` | Creates a new meeting event in Outlook |
| `/meetings` | Shows the list and timings of all sub-team meetings in a place which is only visible to the user who asked for the time | 

## Technologies Used
- python
- discord api
- Microsoft Graph API (for Outlook integration)
- serper / crewai (for web scraping)

## Contributing
Interested in contributing? Check out our [contribution guidelines](CONTRIBUTING.md).

## License
MIT
