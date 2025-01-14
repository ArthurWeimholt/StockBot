# This file helps format responses or embeds 

from datetime import datetime, timedelta
from discord import Embed, Color


def create_embed_footer(embed: Embed) -> None:
    embed.timestamp = datetime.now()
    embed.set_footer(text="Powered by Finnhub API")


def create_quote_embed(ticker: str, data: dict) -> Embed:
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


def embed_news_template(articles: list, embed: Embed) -> None: 

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

