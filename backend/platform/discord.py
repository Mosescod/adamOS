import discord
from discord.ext import commands
from api.gateway import send_to_adam
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
        
    response = await send_to_adam(
        message=message.content,
        user_id=str(message.author.id),
        platform="discord"
    )
    await message.channel.send(response["response"])

def run_bot():
    bot.run(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    run_bot()