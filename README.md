# StockBot

## Description
This is a discord bot pertaining to anything stock market related.
StockBot is meant to be used as an analysis/metric tool for users to stay informed and provide 
insightful data on events, news, and certain stocks. Users can execute special commands to 
retrieve the data they need for research. StockBot uses [Finnhub](https://finnhub.io/docs/api/introduction) and [AlphaVantage](https://www.alphavantage.co/documentation/) API calls.

---

## Commands
Below are the list of commands that Stock Bot can execute.

**get-quote** <br>
This command uses a Finnhub API to return the following:
- Current Price 
- Open Price
- Previous Close Price
- Percent Change
- Day's High
- Day's Low

If the percent change is negative or 0, then the embeded response will be Red. If the percent change is postive then embedded response will be green. Shown below is an example response.

[//]: <> (Insert picture here)

**get-quote-rating** <br>
This command uses a Finnhub API to return a bar and line graph of the analyst recommendation trends based on a ticker symbol


**get-market-news** <br>
Fetches, filters, ranks, and displays the top 10 stock-related news articles from the past 24 hours in an embedded message.

**get-company-news** <br>

## Scheduled Commands
**get-market-news** <br>
Fetches, filters, ranks, and displays the top 10 stock-related news articles from the past 24 hours in an embedded message every morning at 6 AM PST

---

## Developer Workflow

---

## Architecture
