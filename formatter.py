# This file helps format responses or embeds 

from datetime import datetime, timedelta
from discord import Embed, Color


def create_embed_footer(embed: Embed) -> None:
    """Creates a footer with a timestamp for Embedded responses"""
    embed.timestamp = datetime.now()
    embed.set_footer(text="Powered by Finnhub API")


def create_quote_embed(ticker: str, data: dict) -> Embed:
    """Returns an embedded response for a quote lookup based on a Finnhub API call"""
    
    # Determine the emoji for percent change
    percent_change = data['dp']
    if percent_change > 0:
        percent_change_emoji = f"⬆️"
    elif percent_change < 0:
        percent_change_emoji = f"⬇️"
    else:
        percent_change_emoji = f"➖"

    # Create the embed
    embed = Embed(
        title=f"📊 Stock Quote for {ticker}",
        description=f"Quote last updated at {datetime.fromtimestamp(data['t']).strftime('%Y-%m-%d at %-I:%M %p')}:",
        color=Color.green() if percent_change > 0 else Color.red()
    )
    
    # Add fields with styled values
    embed.add_field(
        name="Price Info", 
        value=(
            f"💰 **Current Price: ${data['c']:.2f}**\n"
            f"☀️ **Open: ${data['o']:.2f}**\n"
            f"🌚 **Previous Close: ${data['pc']:.2f}**\n"
            f"{percent_change_emoji} **Percent Change: {percent_change:.2f}**"
        ),
        inline=False
    )   

    embed.add_field(
        name="Day's Ranges",
        value=(
            f"📈 **Day's High: ${data['h']:.2f}**\n"
            f"📉 **Day's Low: ${data['l']:.2f}**"
        ),
        inline=False
    )
    
    # Add footer and timestamp
    create_embed_footer(embed)
    return embed


def create_capm_embed(ticker: str, beta: float, risk_free_rate: float, market_return: float, capm: float) -> Embed:
    """Returns an embedded response for the Capital Asset Pricing Model"""

    # Create the embed
    embed = Embed(
        title=f"Capital Asset Pricing Model (CAPM) for {ticker}",
        description=f"Uses 10 year U.S. Treasury yield for the risk-free rate\n"
                    f"Uses the expected return of the S&P 500 index\n",
        color=Color.blue()
    )

    # Add fields
    embed.add_field(name="Risk-Free Rate", value=f"{risk_free_rate:.2f}%", inline=False)
    embed.add_field(name="Market Return", value=f"{market_return:.2f}%", inline=False)
    embed.add_field(name="Beta", value=f"{beta:.2f}", inline=False)
    embed.add_field(name="CAPM Expected Return", value=f"{capm:.2f}%", inline=False)

    create_embed_footer(embed)
    return embed


def embed_news_template(articles: list, embed: Embed) -> None: 
    """Adds fields for each news article in an embedded response"""

    # Package each article
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

    # Add timestamp and footer
    create_embed_footer(embed)

