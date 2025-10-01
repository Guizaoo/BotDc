import discord
import feedparser
import asyncio
from discord.ext import commands 
import os 


TOKEN = os.environ.get("TOKEN-Discord")

CANAL_ID = 1422633179306786816

RSS_URL = "https://www.guildwars2.com/en/rss"


intents = discord.Intents.default()
intents.message_content = True 
intents.members = True   
intents.presences = True 


client = commands.Bot(command_prefix='!', intents=intents)

# checagem
async def executar_checagem(canal):
    print("Iniciando busca de notícias por comando...")
    feed = feedparser.parse(RSS_URL)
    novas_noticias = False
    
    if not hasattr(client, 'ja_postadas'):
        client.ja_postadas = set()
        
    for entry in reversed(feed.entries):
        if entry.link not in client.ja_postadas:
            await canal.send(f"📢 **{entry.title}**\n{entry.link}")
            client.ja_postadas.add(entry.link)
            novas_noticias = True
            
    if not novas_noticias:
        await canal.send("🔍 Nenhuma nova notícia do Guild Wars 2 desde a última checagem. Tente novamente mais tarde!")


@client.command()
async def noticias(ctx):
    canal_destino = client.get_channel(CANAL_ID) 
    
    if canal_destino is None:
        await ctx.send("ERRO: Não consigo encontrar o canal de postagem. Verifique se o ID está correto!")
        return

    await ctx.send("🤖 **Iniciando checagem de notícias...**")
    
    await executar_checagem(canal_destino)
    
@client.command()
async def test(ctx): 
    await ctx.send("olá.") 

@client.event
async def on_ready():
    print(f"✅ Bot conectado como {client.user}")

    if not hasattr(client, 'ja_postadas'):
        client.ja_postadas = set()


if TOKEN:
    client.run(TOKEN)
else:
    print("ERRO: Token não encontrado na variável de ambiente.")
