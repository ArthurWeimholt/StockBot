import discord
import requests
import os
import datetime
import finnhub
import logging
import plot_util
import formatter
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
        self.finnhub_client = finnhub.Client(api_key=api_key)


    @app_commands.command(name="get-quote", description="Returns the latest quote of the specified ticker symbol in green if postive and red if negative")
    @app_commands.guilds(discord.Object(id=MY_GUILD_ID))
    async def get_quote(self, interaction: discord.Interaction, ticker: str) -> None:
        ticker = ticker.upper()

        # Prevents injection or invalid requests
        if not ticker.isalnum():
            await interaction.response.send_message("Invalid ticker symbol. Please use a valid alphanumeric ticker.")
            return 

        try:
            # Lookup ticker symbol
            data = self.finnhub_client.symbol_lookup(ticker)
            if "count" in data and data["count"] > 0:

                # Check for direct match
                if any(ticker == result["symbol"] for result in data["result"]):
                    data = self.finnhub_client.quote(ticker)

                    # Package the quote data in an embed and return 
                    embed = formatter.create_quote_embed(ticker, data)
                    await interaction.response.send_message(embed=embed)

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


    @app_commands.command(name="get-quote-rating", description="Returns bar and line chart of recommendation trends using Finnhub")
    @app_commands.guilds(discord.Object(id=MY_GUILD_ID))
    async def get_quote_rating(self, interaction: discord.Interaction, ticker: str) -> None:
        ticker = ticker.upper()

        # Prevents injections or invalid requests
        if not ticker.isalnum():
            await interaction.response.send_message("Invalid ticker symbol. Please use a valid alphanumeric ticker.")
            return 

        try:
            # Lookup ticker recommendation trends
            data = self.finnhub_client.recommendation_trends(ticker)
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


    @app_commands.command(name="get-company-news", description="Returns up to 10 news articles within the past week based on a specific ticker using Finnhub")
    @app_commands.guilds(discord.Object(id=MY_GUILD_ID))
    async def get_company_news(self, interaction: discord.Interaction, ticker: str) -> None:
        ticker = ticker.upper()

        # Prevents injections or invalid requests
        if not ticker.isalnum():
            await interaction.response.send_message("Invalid ticker symbol. Please use a valid alphanumeric ticker.")
            return 

        # Define the date range for the past week
        today = datetime.datetime.utcnow()
        last_week = today - datetime.timedelta(days=7)
        
        # Convert the dates to the format required by the API (YYYY-MM-DD)
        start_date = last_week.strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
        
        try:
            news_data = self.finnhub_client.company_news(ticker, _from=start_date, to=end_date)
            
            # Limit the results to a maximum of 10 articles
            top_articles = news_data[:10]

            if not top_articles:
                embed = discord.Embed(
                    title=f"No News for {ticker}",
                    description="There are no recent articles available.",
                    color=discord.Color.red()
                )
            else:
                embed = discord.Embed(
                    title=f"Latest news for {ticker}",
                    description=f"Here are the top {len(top_articles)} news articles from the past week",
                    color=discord.Color.green()
                )
                formatter.embed_news_template(top_articles, embed)
            
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            logging.error(f"Error fetching company news for {ticker}: {e}")
            await interaction.response.send_message("An error occurred while fetching company news. Please try again later.")


    @app_commands.command(name="get-capm", description="Generates the expected return of a stock using the Capital Asset Pricing Model (CAPM)")
    @app_commands.guilds(discord.Object(id=MY_GUILD_ID))
    async def get_company_news(self, interaction: discord.Interaction, ticker: str) -> None:
        ticker = ticker.upper()

        # Prevents injections or invalid requests
        if not ticker.isalnum():
            await interaction.response.send_message("Invalid ticker symbol. Please use a valid alphanumeric ticker.")
            return 
        
        try:
            financials = self.finnhub_client.company_basic_financials(ticker, "all")

            # Extract the beta value
            beta = financials.get("metric", {}).get("beta")
            if beta is None:
                await interaction.response.send_message(f"Beta value not available for {ticker}.")
            
            # Calculate the market risk premium
            risk_free_rate = 4.77
            market_return = 8.00
            market_risk_premium = market_return - risk_free_rate
            
            # Apply the CAPM formula 
            capm_return = risk_free_rate + beta * market_risk_premium

            embed = formatter.create_capm_embed(ticker, beta, risk_free_rate, market_return, capm_return)
            await interaction.response.send_message(embed=embed)
        
        except Exception as e:
            logging.error(f"Error fetching Capital Asset Pricing Model for {ticker}: {e}")
            await interaction.response.send_message("An error occurred while fetching Capital Asset Pricing Model. Please try again later.")


# Setup is required for entry point
async def setup(bot):
    await bot.add_cog(FinnhubCog(bot))
        