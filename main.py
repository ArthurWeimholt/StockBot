# This requires the 'message_content' intent.

import os
import discord
import logging
from discord.ext import commands
from dotenv import dotenv_values
from api_keys import API_keys

class MyBot(commands.Bot):
    def __init__(self, intents):
        super().__init__(command_prefix='/', intents=intents)

        # In case we want to do something guild specific
        self.MY_GUILD = discord.Object(id=int(os.getenv('MY_GUILD_ID')))  


    async def setup_hook(self):
        logging.info("Setup hook started.")
        try:
            # Load cogs
            for filename in os.listdir("./cogs"):
                if filename.endswith(".py"):
                    cog_name = f'cogs.{filename[:-3]}'
                    logging.info(f"Attempting to load cog: {cog_name}")
                    await self.load_extension(cog_name)
                    logging.info(f"Successfully loaded cog: {cog_name}")

            # Sync commands
            logging.info("Syncing commands...")
            self.MY_GUILD = discord.Object(id=int(os.getenv('MY_GUILD_ID')))
            synced = await self.tree.sync(guild=self.MY_GUILD)
            logging.info(f"Synced {len(synced)} command(s) to guild {self.MY_GUILD.id}")
            for command in synced:
                logging.info(f"Synced {command}")
            logging.info("Setup hook finished.")
        except Exception as e:
            logging.error(f"Error in setup_hook: {e}")


    async def on_ready(self):
        logging.info(f'Logged in as: {self.user}')
        logging.info(f'User ID: {self.user.id}')


    async def on_disconnect(self):
        logging.warning("Bot has disconnected from Discord.")
        

    async def on_command_error(self, ctx, error):
        logging.error(f"Error in command '{ctx.command}': {error}")

        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Command not found. Please check your input.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing required argument. Please check the command usage.")
        else:
            # Log the full traceback for unexpected errors
            logging.error("".join(traceback.format_exception(type(error), error, error.__traceback__)))
            await ctx.send("An unexpected error occurred.")



def main():
    # Load in Environment Variables
    config = dotenv_values(".env")
    for k, v in config.items():
        if v:  # only set if not empty
            os.environ.setdefault(k, v)
    API_keys.set_alpha_vantage_api_key(os.getenv('ALPHA_VANTAGE_API_KEY'))
    API_keys.set_finnhub_api_key(os.getenv('FINNHUB_API_KEY'))

    # Create the log directory if it doesn't exist
    log_directory = 'logs'
    os.makedirs(log_directory, exist_ok=True) 
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,  # Set the log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format='[%(asctime)s] %(name)s [%(levelname)s]: %(message)s',  # Log format
        datefmt='%Y-%m-%d %H:%M:%S',  # Date format
        handlers=[
            logging.FileHandler(filename=os.path.join(log_directory, 'bot.log'), encoding='utf-8', mode='w'),
            logging.StreamHandler()  # Also log to the console
        ]
    )

    # Get the Discord logger
    discord_logger = logging.getLogger('discord')
    discord_logger.setLevel(logging.INFO)

    # Default Intents
    intents = discord.Intents.default()
    intents.message_content = True

    # Load the cog and run the bot, set root_logger to True to enable logging for all loggers
    bot = MyBot(intents=intents)
    bot.run(os.getenv('TOKEN'))


if __name__ == "__main__":
    main()
