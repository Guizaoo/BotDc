import discord
import feedparser
import asyncio
import os
from discord.ext import commands, tasks

TOKEN = os.environ.get("TOKEN-Discord")
CANAL_ID = 1422633179306786816
RSS_URL = "https://www.guildwars2.com/en/rss"

intents = discord.Intents.default()
intents.message_content = True 
intents.members = True   
intents.presences = True 

client = commands.Bot(command_prefix='!', intents=intents)

@tasks.loop(minutes=30)
async def checar_noticias_automaticamente():
    await client.wait_until_ready() 
    canal = client.get_channel(CANAL_ID)
    
    if canal is None:
        checar_noticias_automaticamente.stop() 
        return

    if not hasattr(client, 'ja_postadas'):
        client.ja_postadas = set()
        
    try:
        feed = feedparser.parse(RSS_URL)
        novas_noticias = False
        
        for entry in reversed(feed.entries):
            if entry.link not in client.ja_postadas:
                await canal.send(f"📢 **NOVIDADE GUILD WARS 2**\n**{entry.title}**\n{entry.link}")
                client.ja_postadas.add(entry.link)
                novas_noticias = True
                await asyncio.sleep(2)
                
    except Exception as e:
        print(f"Ocorreu um erro durante a checagem automática: {e}")

async def executar_checagem_manual(canal):
    if not hasattr(client, 'ja_postadas'):
        client.ja_postadas = set()
        
    try:
        feed = feedparser.parse(RSS_URL)
        novas_noticias = False
        
        for entry in reversed(feed.entries):
            if entry.link not in client.ja_postadas:
                await canal.send(f"📢 **{entry.title}**\n{entry.link}")
                client.ja_postadas.add(entry.link)
                novas_noticias = True
                await asyncio.sleep(2)
                
        if not novas_noticias:
            await canal.send("🔍 Nenhuma nova notícia do Guild Wars 2 desde a última checagem. Tente novamente mais tarde!")
    
    except Exception as e:
        await canal.send(f"⚠️ **Erro na checagem:** Ocorreu um problema ao buscar o RSS. Detalhes: {e}")

@client.command()
async def noticias(ctx):
    canal_destino = client.get_channel(CANAL_ID) 
    
    if canal_destino is None:
        await ctx.send("ERRO: Não consigo encontrar o canal de postagem. Verifique se o ID está correto!")
        return

    await ctx.send("🤖 **Iniciando checagem manual de notícias...**")
    
    await executar_checagem_manual(canal_destino)
    
@client.command()
async def test(ctx): 
    await ctx.send("olá.") 

@client.event
async def on_ready():
    if not hasattr(client, 'ja_postadas'):
        client.ja_postadas = set()
        
    if not checar_noticias_automaticamente.is_running():
        checar_noticias_automaticamente.start()

if TOKEN:
    try:
        client.run(TOKEN)
    except discord.HTTPException as e:
        print(f"ERRO DE LOGIN: Ocorreu um erro ao fazer login. Verifique o seu TOKEN. Detalhes: {e}")
else:
    print("ERRO: Token não encontrado na variável de ambiente.")