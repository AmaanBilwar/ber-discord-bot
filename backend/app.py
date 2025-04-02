from dotenv import load_dotenv
import os 
import discord
from discord import app_commands
from discord.ext import commands
from openai import OpenAI
import asyncio

load_dotenv()

# Get environment variables
token = os.getenv('DISCORD_TOKEN')
base_url = os.getenv("BASE_URL")
api_key=os.getenv("NEBIUS_API_KEY")


# initialize LLM (nebius) client
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
            max_tokens=500
        ))
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling API: {e}")
        return "Sorry, I encountered an error while trying to summarize the conversation."

@bot.tree.command(name="summarize", description="Summarize recent conversation in this channel")
async def summarize(interaction: discord.Interaction):
    """Command to summarize the last 50 messages in the channel."""
    await interaction.response.defer(thinking=True)
    
    try:
        # Get the last 50 messages
        messages = [msg async for msg in interaction.channel.history(limit=50)]
        messages.reverse()  # Put them in chronological order
        
        if not messages:
            await interaction.followup.send("No messages to summarize!")
            return
            
        summary = await summarize_conversation(messages)
        
        # Create an embed for the summary
        embed = discord.Embed(
            title="Conversation Summary",
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