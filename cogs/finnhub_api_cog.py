import discord
import requests
import os
import datetime
import finnhub
import logging
import plot_util
from api_keys import API_keys
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

# Load the .env file from the parent directory
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')
load_dotenv(env_path)

# Define MY_GUILD_ID for testing, production will be None
MY_GUILD_ID = os.getenv("MY_GUILD_ID", None)

class FinnhubCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Check the validity of the API key before inializing this class
        api_key = API_keys.get_finnhub_api_key()
        if not api_key:
            logging.error("Finnhub API key is missing or invalid.")
            raise ValueError("Finnhub API key is not set. Please configure the API key.")
        self.client = finnhub.Client(api_key=api_key)

    @app_commands.command(name="test-finnhub-cog", description="Tests the finnhub cog")
    @app_commands.guilds(discord.Object(id=MY_GUILD_ID))
    async def test_finnhub_cog(self, interaction: discord.Interaction):
        await interaction.response.send_message("Finnhub Cog awaiting commands.")

    @app_commands.command(name="get-quote", description="Retrieves the latest quote of the specified ticker symbole using Finnhub")
    @app_commands.guilds(discord.Object(id=MY_GUILD_ID))
    async def get_quote_finnhub(self, interaction: discord.Interaction, ticker: str):
        ticker = ticker.upper()

        # Prevents injection or invalid requests
        if not ticker.isalnum():
            await interaction.response.send_message("Invalid ticker symbol. Please use a valid alphanumeric ticker.")
            return 

        try:
            # Lookup ticker symbol
            data = self.client.symbol_lookup(ticker)
            if "count" in data and data["count"] > 0:

                # Check for direct match
                if any(ticker == result["symbol"] for result in data["result"]):
                    data = self.client.quote(ticker)

                    # Package the quote data
                    response = f'Current price: {data["c"]}\n'
                    response += f'Previous Close: {data["pc"]}\n'
                    response += f'Open: {data["o"]}\n'
                    response += f'High: {data["h"]}\n'
                    response += f'Low: {data["l"]}\n'
                    response += f'Percent Change: {data["dp"]}\n'
                    response += f'Timestamp: {datetime.datetime.fromtimestamp(data["t"])}\n'
                    await interaction.response.send_message(response)

                # Found indirect matches
                else:
                    response = f'Could not find a direct match.\nDid you mean: \n'
                    count = 1
                    for result in data["result"]:
                        response += f'{count}: {result["symbol"]}, {result["description"]}\n'
                        count += 1
                    await interaction.response.send_message(response)

            # Could not find any matches
            else:
                await interaction.response.send_message("Cannot find a quote for that symbol.\nPlease check that the ticker symbol is correct.")

        except Exception as e:
            logging.error(f"Error fetching quote for {ticker}: {e}")
            await interaction.response.send_message("An error occurred while fetching the quote. Please try again later.")


    @app_commands.command(name="get-quote-rating", description="Returns a chart of recommendation trends")
    @app_commands.guilds(discord.Object(id=MY_GUILD_ID))
    async def get_quote_rating(self, interaction: discord.Interaction, ticker: str):
        ticker = ticker.upper()

        # Prevents injections or invalid requests
        if not ticker.isalnum():
            await interaction.response.send_message("Invalid ticker symbol. Please use a valid alphanumeric ticker.")
            return 

        try:
            # Lookup ticker recommendation trends
            data = self.client.recommendation_trends(ticker)
            if len(data) != 0:
                sb = [item["strongBuy"] for item in data]
                b = [item["buy"] for item in data]
                h = [item["hold"] for item in data]
                s = [item["sell"] for item in data]
                ss = [item["strongSell"] for item in data]
                dates = [item["period"] for item in data]

                # Form recommendation trends graphs
                recommendation_trends = plot_util.RecommendationTrends(sb, b, h, s, ss, dates)
                bar_graph_image_path = plot_util.gen_bar_graph_recommended_trends(ticker, recommendation_trends)
                line_graph_image_path = plot_util.gen_line_graph_recommended_trends(ticker, recommendation_trends)
                with open(bar_graph_image_path, 'rb') as bar_file, open(line_graph_image_path, 'rb') as line_file:
                    files = [
                        discord.File(bar_file), 
                        discord.File(line_file)
                    ]
                    await interaction.response.send_message(files=files)

                # Remove the generated files
                if os.path.exists(bar_graph_image_path):
                    os.remove(bar_graph_image_path)
                if os.path.exists(line_graph_image_path):
                    os.remove(line_graph_image_path)
                
            else:
                await interaction.response.send_message(f'Cannot find recommendation trend for {ticker}')
        except Exception as e:
            logging.error(f"Error fetching recommendation trends for {ticker}: {e}")
            await interaction.response.send_message("An error occurred while fetching the recommendation trends. Please try again later.")

# Setup is required for entry point
async def setup(bot):
    await bot.add_cog(FinnhubCog(bot))
        