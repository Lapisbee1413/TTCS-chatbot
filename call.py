import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Import hàm RAG cục bộ (Phạm vi theo đề bài)
from rag_pipeline import ask_ollama_async, MISTRAL_MODEL

load_dotenv()

discord_bot_token = os.getenv("discord_bot_token")
intents = discord.Intents.default()
intents.message_content = True 

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Bot đã online với tên: {bot.user}')

@bot.command()
async def ask(ctx, *, question):
    async with ctx.typing(): 
        # Gọi hàm ask_ollama_async để chạy mô hình Local
        # Sử dụng model Mistral 
        result = await ask_ollama_async(question, model=MISTRAL_MODEL, top_k=3)
        
        answer = result["answer"]
        
        await ctx.send(f"**Trợ lý Pháp lý Local:**\n{answer}")

bot.run(discord_bot_token)