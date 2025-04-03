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
4. Set up API keys for required services
5. Run the bot: `python backend/app.py`

## Commands

| Command | Description | Options | 
|---------|-------------|---------|
| `/summarize <years/months/days/hours> ` | Summarize recent conversations | hours, days, months, years - Specify time period to summarize |
| `/lookup <item>` | Search for products and components | query - Product to search for<br>vendor - Optional: Specific vendor to search (digikey, mouser, amazon, etc.) | 
| `/meetings` | Shows the list and timings of all sub-team meetings in a place which is only visible to the user who asked for the time | 

## Technologies Used

### Core Framework
 - Python 3.9+: Primary programming language
 - discord.py: Discord API wrapper for bot functionality
 - asyncio: Handles asynchronous operations to maintain responsiveness

### Language Models
 - OpenAI API Client: Interface for calling LLM models
 - Llama-3.3-70B-Instruct: Large Language Model used for conversation summarization
 - Nebius API: Alternative LLM provider for summarization capabilities

### Data Sources & Retrieval
 - Serper.dev API: Web scraping service for product searches
 - Redis: In-memory database for caching search results to improve performance and reduce API calls

## Data Processing
 - JSON: Used for data serialization and API communication
 - hashlib: Creates consistent cache keys for storing search results

## Technical Implementation

### Conversation Summarization

The bot uses Llama 3.3 to generate concise summaries of Discord conversations. It fetches a specified number of messages based on the time range provided (hours/days/months/years) and processes them asynchronously to avoid blocking the main thread.

### Product Search System
The system employs a multi-tier approach:

     - Cache Check: First checks Redis for cached results to avoid redundant API calls
     - Search Execution: If not cached, performs either generic or vendor-specific search
     - Result Normalization: Standardizes product data from different sources
     - Cache Storage: Stores results for 30 minutes to improve performance

### Vendor-Specific Search

The product lookup feature supports multiple vendors including DigiKey, Mouser, Amazon, and specialty racing suppliers. It filters shopping results to match the specified vendor's domain, ensuring relevant results.

## Current Limitations

 - API Rate Limits: Serper.dev and LLM providers have usage limits that could affect functionality during heavy usage
 - Vendor Coverage: Some racing-specific vendors may have limited result quality depending on their representation in Google Shopping results
 - Price Accuracy: Prices shown are from search results and may not always reflect current pricing on vendor websites
 - Summarization Quality: Very technical conversations might not always be summarized with domain-specific accuracy

## Future Improvements
1. Database Integration: Implement Supabase or similar database to track price history and allow users to save favorite parts
2. Meeting Scheduler: Add Outlook/Google Calendar integration for team meeting management
3. Enhanced Product Details: Implement deeper scraping for technical specifications and compatibility information
4. User Preferences: Allow users to set preferred vendors and part categories
5. Notification System: Enable users to track price changes for specific components
6. Team-Specific Knowledge Base: Integrate with team documentation to provide context-aware responses
7. Custom Vendor Parsers: Develop specialized parsers for racing-specific vendors to improve result quality
8. Image Recognition: Add capabilities to identify parts from uploaded images
9. Purchase Workflow: Implement features to facilitate the parts procurement process


## Environment Variables

``` DISCORD_TOKEN=your_discord_bot_token
    BASE_URL=your_llm_api_base_url
    NEBIUS_API_KEY=your_nebius_api_key
    SERPER_API_KEY=your_serper_api_key
    REDIS_URL=your_redis_connection_string 
```

## Contributing
Interested in contributing? We welcome improvements to any aspect of the bot. Check our contribution guidelines for more information.

## License
This project is licensed under the MIT License - see the LICENSE file for details.