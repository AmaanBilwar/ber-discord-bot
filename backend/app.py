from dotenv import load_dotenv
import os 
import discord
from discord import app_commands
from discord.ext import commands
from openai import OpenAI
import asyncio
import datetime
import requests
import json
import pytz
from typing import List

load_dotenv()

# Get environment variables
token = os.getenv('DISCORD_TOKEN')
base_url = os.getenv("BASE_URL")
api_key = os.getenv("NEBIUS_API_KEY")

# Initialize LLM client
client = OpenAI(
    base_url=base_url,
    api_key=api_key,
)

description = 'A Discord bot that can summarize conversations'

# Set up intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Create bot instance
bot = commands.Bot(command_prefix='?', description=description, intents=intents)

@bot.event
async def on_ready():
    """Event handler for when the bot is ready."""
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

async def summarize_conversation(messages):
    """Use OpenAI to summarize a conversation."""
    conversation = "\n".join([f"{msg.author.name}: {msg.content}" for msg in messages if msg.content])
    
    try:
        # Use run_in_executor to call the API asynchronously
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes Discord conversations concisely."},
                {"role": "user", "content": f"Summarize this Discord conversation in a concise way:\n\n{conversation}"}
            ],
            max_tokens=800
        ))
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling API: {e}")
        return "Sorry, I encountered an error while trying to summarize the conversation."

@bot.tree.command(name="summarize", description="Summarize conversation in this channel")
@app_commands.describe(
    hours="Number of hours back to summarize",
    days="Number of days back to summarize",
    months="Number of months back to summarize",
    years="Number of years back to summarize",
)
async def summarize(
    interaction: discord.Interaction,
    hours: int = 0,
    days: int = 0,
    months: int = 0,
    years: int = 0
):
    """Command to summarize messages from a specific time period."""
    await interaction.response.defer(thinking=True)
    
    try:
        # Make sure at least one time period is provided
        if not any([hours, days, months, years]):
            hours = 24  # Default to 24 hours if nothing specified
        
        # Calculate the cutoff time
        cutoff_time = discord.utils.utcnow()
        if hours:
            cutoff_time -= datetime.timedelta(hours=hours)
        if days:
            cutoff_time -= datetime.timedelta(days=days)
        if months:
            # Approximate months as 30 days
            cutoff_time -= datetime.timedelta(days=30 * months)
        if years:
            # Approximate years as 365 days
            cutoff_time -= datetime.timedelta(days=365 * years)
        
        # Get messages after the cutoff time
        messages = [msg async for msg in interaction.channel.history(after=cutoff_time, limit=500)]
        messages.reverse()  # Put them in chronological order
        
        if not messages:
            await interaction.followup.send("No messages found in that time period!")
            return
            
        summary = await summarize_conversation(messages)
        
        # Create a human-readable time period string
        time_periods = []
        if years:
            time_periods.append(f"{years} year{'s' if years > 1 else ''}")
        if months:
            time_periods.append(f"{months} month{'s' if months > 1 else ''}")
        if days:
            time_periods.append(f"{days} day{'s' if days > 1 else ''}")
        if hours:
            time_periods.append(f"{hours} hour{'s' if hours > 1 else ''}")
        
        time_period_str = ", ".join(time_periods)
        
        # Create an embed for the summary
        embed = discord.Embed(
            title=f"Summary of last {time_period_str}",
            description=summary,
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Summarized {len(messages)} messages")
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        print(f"Error in summarize command: {e}")
        await interaction.followup.send(f"Sorry, I encountered an error: {str(e)}")

@bot.command()
@commands.is_owner()
async def sync(ctx):
    """Syncs the slash commands to the current guild."""
    guild = discord.Object(id=ctx.guild.id)  # Get current guild ID
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)
    await ctx.send(f"Commands synced to this guild! ({ctx.guild.name})")

bot.run(token)