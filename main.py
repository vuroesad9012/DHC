import os
from dotenv import load_dotenv

load_dotenv()

import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask
from threading import Thread
from views.ticket_views import (
    TicketView, VerifyView, RobuxAmountSelect, TicketSelect, CryptoSelect, 
    CryptoView, CryptoAmountSelect, CryptoAmountView, CryptoAmountSelectedView, 
    CryptoAmountSelectOnlyView, TicketPanelView, CashAppAmountSelect, CashAppView,
    CashAppAmountSelectedView
)

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)

# --- Flask server for Render ---
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

def start_flask():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

start_flask()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    
    # Register all persistent views to handle interactions
    bot.add_view(VerifyView())
    bot.add_view(TicketView())
    bot.add_view(CryptoView())
    bot.add_view(CryptoAmountView())
    bot.add_view(CryptoAmountSelectedView())
    bot.add_view(CryptoAmountSelectOnlyView())
    bot.add_view(CashAppView())
    bot.add_view(CashAppAmountSelectedView())
    bot.add_view(TicketPanelView())
    
    # Create wrapper views for Select components and register them
    class RobuxSelectView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)
            self.add_item(RobuxAmountSelect())
    
    class TicketSelectView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)
            self.add_item(TicketSelect())
    
    class CryptoSelectView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)
            self.add_item(CryptoSelect())
    
    class CryptoAmountSelectView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)
            self.add_item(CryptoAmountSelect())
    
    class CashAppAmountSelectView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)
            self.add_item(CashAppAmountSelect())
    
    bot.add_view(RobuxSelectView())
    bot.add_view(TicketSelectView())
    bot.add_view(CryptoSelectView())
    bot.add_view(CryptoAmountSelectView())
    bot.add_view(CashAppAmountSelectView())
    
    print("Persistent views loaded")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Error syncing commands: {e}")

async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and not filename.startswith("_"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"Loaded cog: {filename}")
            except Exception as e:
                print(f"Error loading cog {filename}: {e}")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
