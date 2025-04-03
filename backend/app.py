from dotenv import load_dotenv
import os 
import discord
from discord import app_commands
from discord.ext import commands
from openai import OpenAI
import asyncio
import datetime
import requests
import uuid
from discord.ui import View, Button
import redis
import json
import hashlib
import time
load_dotenv()

# Get environment variables
token = os.getenv('DISCORD_TOKEN')
base_url = os.getenv("BASE_URL")
api_key = os.getenv("NEBIUS_API_KEY")
serper_api_key = os.getenv("SERPER_API_KEY")
redis_url = os.getenv("REDIS_URL")  # Connection string for Redis

# Initialize LLM client
client = OpenAI(
    base_url=base_url,
    api_key=api_key,
)

# Initialize Redis client (if available)
redis_client = None
if redis_url:
    try:
        redis_client = redis.from_url(redis_url)
        print("Redis cache initialized")
    except Exception as e:
        print(f"Failed to connect to Redis: {e}")

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

# Add a function to generate cache keys
def generate_cache_key(query, vendor=None):
    """Generate a cache key for Redis."""
    cache_key = f"product_search:{query}"
    if vendor:
        cache_key += f":{vendor}"
    # Create a hash to ensure valid Redis key
    return hashlib.md5(cache_key.encode()).hexdigest()

# Update your search_products function to use the cache
async def search_products(query, vendor=None):
    """Search for products either generically or from a specific vendor."""
    try:
        # Generate cache key
        cache_key = generate_cache_key(query, vendor)
        
        # Try to get from cache first
        if redis_client:
            cached_data = redis_client.get(cache_key)
            if cached_data:
                print(f"Cache hit for query: {query}")
                return json.loads(cached_data)
        
        # If not in cache or no Redis, perform the search
        if vendor:
            results = await search_vendor_products(query, vendor)
        else:
            results = await search_generic_products(query)
            
        # Store in cache if Redis is available
        if redis_client and results:
            # Cache for 30 minutes
            redis_client.setex(
                cache_key, 
                1800,  # 30 minutes in seconds
                json.dumps(results, default=str)  # Handle any non-serializable data
            )
            
        return results
    except Exception as e:
        print(f"Error searching for products: {e}")
        return None

async def search_generic_products(query):
    """Search for products using Serper.dev API."""
    try:
        headers = {
            'X-API-KEY': serper_api_key,
            'Content-Type': 'application/json'
        }
        
        payload = {
            "q": f"{query} buy online",
            "gl": "us",
            "hl": "en",
            "autocorrect": True,
            "type": "shopping"
        }
        
        # Run the API call in a separate thread since it's blocking
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: requests.post(
                'https://google.serper.dev/search',
                headers=headers,
                json=payload
            )
        )
        
        if response.status_code != 200:
            print(f"Error from Serper API: {response.status_code}, {response.text}")
            return []
        
        results = response.json()
        
        if "shopping" not in results:
            return []
        
        products = []
        for item in results["shopping"][:5]:  # Limit to top 5 results
            product = {
                "name": item.get("title", "Unknown Product"),
                "price": item.get("price", "N/A"),
                "vendor": item.get("source", "Unknown"),
                "link": item.get("link", "#"),
                "image": item.get("imageUrl"),
                "shipping": "Check website for shipping details",  # Serper doesn't provide shipping info directly
                "rating": f"{item.get('rating', 'N/A')}" if 'rating' in item else "N/A"
            }
            products.append(product)
        
        return products
    except Exception as e:
        print(f"Error in generic product search: {e}")
        return []

async def search_vendor_products(query, vendor):
    """Search for products from a specific vendor using Serper.dev."""
    # List of supported vendors with their domains
    vendors = {
        "digikey": "digikey.com",
        "mouser": "mouser.com",
        "amazon": "amazon.com", 
        "mcmaster": "mcmaster.com",
        "sparkfun": "sparkfun.com",
        "adafruit": "adafruit.com",
        "grainger": "grainger.com",
        "summit": "summitracing.com",
        "rockauto": "rockauto.com"
    }
    
    # Check if vendor is supported
    vendor = vendor.lower()
    if vendor not in vendors:
        return {"error": f"Vendor '{vendor}' not supported. Supported vendors: {', '.join(vendors.keys())}"}
    
    # For vendor-specific search, add the vendor name to the shopping query
    vendor_modified_query = f"{query} {vendor}"
    
    try:
        headers = {
            'X-API-KEY': serper_api_key,
            'Content-Type': 'application/json'
        }
        
        # Use shopping search with vendor in query
        payload = {
            "q": vendor_modified_query,
            "gl": "us",
            "hl": "en",
            "autocorrect": True,
            "type": "shopping"  # Use shopping search type
        }
        
        # Run the API call in a separate thread since it's blocking
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: requests.post(
                'https://google.serper.dev/search',
                headers=headers,
                json=payload
            )
        )
        
        if response.status_code != 200:
            print(f"Error from Serper API: {response.status_code}, {response.text}")
            return []
        
        results = response.json()
        
        # Check if shopping results exist
        if "shopping" not in results or not results["shopping"]:
            print(f"No shopping results found for {vendor_modified_query}")
            return []
        
        # Filter for results that match the vendor domain
        vendor_domain = vendors[vendor]
        
        products = []
        for item in results["shopping"]:
            # Check if this result is from the right vendor
            is_from_vendor = False
            if "source" in item and vendor_domain.lower() in item["source"].lower():
                is_from_vendor = True
            elif "link" in item and vendor_domain.lower() in item["link"].lower():
                is_from_vendor = True
                
            if is_from_vendor:
                product = {
                    "name": item.get("title", "Unknown Product"),
                    "price": item.get("price", "N/A"),
                    "vendor": vendor,
                    "link": item.get("link", "#"),
                    "image": item.get("imageUrl") if "imageUrl" in item else None,
                    "shipping": item.get("shipping", "Check website for shipping details"),
                    "rating": f"{item.get('rating', 'N/A')}" if 'rating' in item else "N/A"
                }
                products.append(product)
                
                # Limit to 5 vendor-specific results
                if len(products) >= 5:
                    break
        
        return products
    except Exception as e:
        print(f"Error in vendor-specific search: {e}")
        return []

@bot.tree.command(name="lookup", description="Look up product information")
@app_commands.describe(
    query="The product you want to search for",
    vendor="Optional: Specific vendor to search (digikey, mouser, amazon)"
)
async def lookup(interaction: discord.Interaction, query: str, vendor: str = None):
    """Command to look up product information."""
    await interaction.response.defer(thinking=True)
    
    try:
        products = await search_products(query, vendor)
        
        if not products:
            await interaction.followup.send(f"No results found for '{query}'.")
            return
        
        if isinstance(products, dict) and "error" in products:
            await interaction.followup.send(products["error"])
            return
        
        # Create an embed for each product
        embeds = []
        for i, product in enumerate(products[:5]):  # Limit to 5 products max
            embed = discord.Embed(
                title=product["name"],
                url=product["link"],
                description=f"Vendor: {product['vendor']}",
                color=discord.Color.green()
            )
            embed.add_field(name="Price", value=product["price"], inline=True)
            embed.add_field(name="Shipping", value=product["shipping"], inline=True)
            
            if product["rating"] != "N/A":
                embed.add_field(name="Rating", value=product["rating"], inline=True)
                
            if product["image"]:
                embed.set_thumbnail(url=product["image"])
                
            embeds.append(embed)
        
        # Create pagination view with buttons
        class ProductPaginator(View):
            def __init__(self, embeds):
                super().__init__(timeout=60)  # 60-second timeout
                self.embeds = embeds
                self.current_page = 0
                self.total_pages = len(embeds)
            
            @discord.ui.button(label="Previous", style=discord.ButtonStyle.gray)
            async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                self.current_page = (self.current_page - 1) % self.total_pages
                embed = self.embeds[self.current_page]
                embed.set_footer(text=f"Page {self.current_page + 1}/{self.total_pages}")
                await interaction.response.edit_message(embed=embed)
            
            @discord.ui.button(label="Next", style=discord.ButtonStyle.gray)
            async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                self.current_page = (self.current_page + 1) % self.total_pages
                embed = self.embeds[self.current_page]
                embed.set_footer(text=f"Page {self.current_page + 1}/{self.total_pages}")
                await interaction.response.edit_message(embed=embed)
        
        # Create the paginator
        paginator = ProductPaginator(embeds)
        
        # Add page info to first embed
        embeds[0].set_footer(text=f"Page 1/{len(embeds)}")
        
        # Send the first embed with the paginator
        await interaction.followup.send(embed=embeds[0], view=paginator)
    
    except Exception as e:
        print(f"Error in lookup command: {e}")
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