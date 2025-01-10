import discord
import requests
import os
import finnhub
from api_keys import API_keys
from discord.ext import commands

class AlphaVantageCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = finnhub.Client(api_key="YOUR API KEY")

    @commands.command(name="test_alpha_vantage", description="Tests the Alpha Vantage cog")
    async def test_alpha_vantage(self, ctx):
        await ctx.send("Alpha Vantage Cog awaiting commands!")

    @commands.command(name="get-quote-av", description="Retrieves the latest quote of the specified ticker symbol using Alpha Vantage")
    async def get_quote_av(self, ctx, ticker):
        ticker = ticker.upper()
        alpha_vantage_api_key = API_keys.get_alpha_vantage_api_key()

        # Form the url for the API call (https://www.alphavantage.co/support/#api-key)
        url = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=' + ticker + '&apikey=' + alpha_vantage_api_key
        r = requests.get(url)
        data = r.json()

        # Check to see we are not capped passed our API call limit
        if "Information" in data:
            await ctx.send(data["Information"])

        # Check if the data returned is valid
        if "Global Quote" in data and len(data["Global Quote"]) == 0:
            # Perform Best Match API and maybe have UI buttons for yes and no (generate)
            url = 'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=' + ticker + '&apikey=' + alpha_vantage_api_key
            r = requests.get(url)
            data = r.json()

            # Form the response
            response = "Invalid ticker symbol\n"
            response += "Did you mean: \n"
            count = 1
            for search in data["bestMatches"]:
                response += f'{count}. {search["1. symbol"]}: {search["2. name"]}\n'
                count += 1
            await ctx.send(response)
        else:
            # Package data to be sent
            response = f'Ticker: {ticker}\n'
            response += f'Date: {data["Global Quote"]["07. latest trading day"]}\n'
            response += f'Open: {data["Global Quote"]["02. open"]}\n'
            response += f'Previous Close: {data["Global Quote"]["08. previous close"]}\n'
            response += f'High: {data["Global Quote"]["03. high"]}\n'
            response += f'Low: {data["Global Quote"]["04. low"]}\n'
            response += f'Percentage Change: {data["Global Quote"]["10. change percent"]}'
            await ctx.send(response)


# Setup is required for entry point
async def setup(bot):
    await bot.add_cog(AlphaVantageCog(bot))
        