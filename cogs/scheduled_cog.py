import logging
import finnhub
import discord
import os
from discord import app_commands
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from api_keys import API_keys
from dotenv import load_dotenv

# Load the .env file from the parent directory
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')
load_dotenv(env_path)

# Define MY_GUILD_ID for testing, production will be None
MY_GUILD_ID = os.getenv("MY_GUILD_ID", None)

class ScheduledTaskCog(commands.Cog):
    def __init__(self, bot):
        
        # Check the validity of the API key before inializing this class
        api_key = API_keys.get_finnhub_api_key()
        if not api_key:
            logging.error("Finnhub API key is missing or invalid.")
            raise ValueError("Finnhub API key is not set. Please configure the API key.")
        self.finnhub_client = finnhub.Client(api_key=api_key)

        # Constants
        self.STOCK_KEYWORDS = ["stock", "market", "shares", "earnings", "IPO", "investment", "trading", "ai", "technology"]
        self.TRUSTED_SOURCES = ["cnbc", "bloomberg", "reuters", "wsj", "financial times"]

        self.bot = bot
        self.category_name = "Stock Channels"
        self.channel_name = "stock-news"  # Default channel name
        self.channel = None  # Will hold a reference to the channel name
        self.message_time = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0) # 6 AM
        if self.message_time < datetime.now():  # Ensure it's the next occurrence if it's already past 6 AM
            self.message_time += timedelta(days=1)
        self.task.start()  # Start the scheduled task


    async def ensure_channel_exists(self, guild):
        """Ensure the category and channel exists, and create it if it doesn't."""
        
        # Find the category
        category = discord.utils.get(guild.categories, name=self.category_name)
        if not category:
            # Create the category if it doesn't exist
            category = await guild.create_category(name=self.category_name)
            logging.info(f"Created new category: {self.category_name}")

        # Find the channel
        if not self.channel:
            existing_channel = discord.utils.get(guild.channels, name=self.channel_name)
            if existing_channel:
                self.channel = existing_channel
            else:
                # Create the channel if it doesn't exist
                self.channel = await guild.create_text_channel(name=self.channel_name, category=category)
                logging.info(f"Channel '{self.channel_name}' created.")


    @tasks.loop(seconds=60)  # Check every 60 seconds
    async def task(self):
        """Checks if it's time to send the scheduled message."""
        now = datetime.now()
        for guild in self.bot.guilds:  # Iterate through all connected guilds
            await self.ensure_channel_exists(guild)  # Ensure the channel exists
            if self.channel and now >= self.message_time:
                # Send the scheduled message
                embed = await self.fetch_and_format_market_news()
                await self.channel.send(embed=embed)
            
                # Schedule for the next day
                self.message_time += timedelta(days=1)


    @task.before_loop
    async def before_task(self):
        logging.info("Waiting for bot to be ready before starting the scheduled_cog task loop")
        await self.bot.wait_until_ready()

    
    def is_stock_relevant(self, article):
        """Filter by relevance (keywords)"""
        headline = article.get("headline", "").lower()
        summary = article.get("summary", "").lower()
        return any(keyword in headline or keyword in summary for keyword in self.STOCK_KEYWORDS)

    
    def get_source_priority(self, article):
        """Rank by source priority and recency"""
        source = article.get("source", "").lower()
        return 1 if source in self.TRUSTED_SOURCES else 2

    def create_news_embed(self, articles):
        """Create a Discord embed with the top news articles."""
        embed = discord.Embed(
            title="Top Stock Market News",
            description="Here are the most relevant stock-related news articles from the past day:",
            color=discord.Color.green()
        )

        for article in articles:
            headline = article["headline"]
            url = article["url"]
            source = article.get("source", "Unknown")
            time = datetime.fromtimestamp(article["datetime"]).strftime("%Y-%m-%d %H:%M:%S")
            embed.add_field(
                name=f"{headline} ({source})",
                value=f"[Read more here]({url})\nPublished: {time}",
                inline=False
            )

        embed.timestamp = datetime.now()
        embed.set_footer(text="Powered by Finnhub API")
        return embed


    async def fetch_and_format_market_news(self):
        """Fetch market news and format it as a response."""
        try:
            # Step 1: Fetch all market news
            logging.info("Retrieving market news")
            news_data = self.finnhub_client.general_news('general')
            if len(news_data) == 0:
                embed = discord.Embed(
                    title="Market News",
                    description="Could not retrieve market news.",
                    color=discord.Color.red()
                )
                return embed

            # Step 2: Filter by time, last day 
            logging.info("Filtering top news articles by the last 24 hours")
            current_time = datetime.utcnow()
            cutoff_time = current_time - timedelta(days=1)
            recent_news = [
                article for article in news_data
                if datetime.utcfromtimestamp(article["datetime"]) >= cutoff_time
            ]

            # Step 3: Search top news by keywords
            logging.info("Filtering top news articles by keywords")
            relevant_news = [article for article in recent_news if self.is_stock_relevant(article)]

            # Step 4: Rank by source priority and recency
            logging.info("Filtering top news articles by priority and recency")
            ranked_news = sorted(
                relevant_news,
                key=lambda article: (self.get_source_priority(article), -article["datetime"])
            )

            # Step 5: Retrieve only first 10 news
            logging.info("Finished filtering, returning top 10 news")
            top_articles = ranked_news[:10]

            # Step 6: Create an embed
            embed = self.create_news_embed(top_articles)
            return embed

        except Exception as e:
            logging.error(f"Error fetching market news: {e}")
            embed = discord.Embed(
                title="Market News",
                description="An error occurred while retrieving market news. Please try again later.",
                color=discord.Color.red()
            )
            return embed


    @app_commands.command(name="get-market-news", description="Retrieves 10 stock market news articles within the last 24 hours")
    @app_commands.guilds(discord.Object(id=MY_GUILD_ID))
    async def get_market_news(self, interaction: discord.Interaction):
        logging.info("get-market-news command is being executed")
        embed = await self.fetch_and_format_market_news()
        await interaction.response.send_message(embed=embed)
            

# Setup for loading the cog
async def setup(bot):
    await bot.add_cog(ScheduledTaskCog(bot))
