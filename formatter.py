# This file helps format responses or embeds 

from datetime import datetime, timedelta
from discord import Embed


def embed_news_template(articles: list, embed: Embed) -> Embed: 

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
    embed.timestamp = datetime.now()
    embed.set_footer(text="Powered by Finnhub API")
    return embed