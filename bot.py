import discord
import feedparser
import asyncio
import os
from discord.ext import commands, tasks
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do .env
load_dotenv() 

# Configurações
TOKEN = os.environ.get("TOKEN-Discord")
# CERTIFIQUE-SE DE QUE ESTE É O ID CORRETO DO SEU CANAL
CANAL_ID = 1422633179306786816 
# URL do RSS do Guild Wars 2. Se esta falhar, tente uma alternativa como:
# RSS_URL = "https://en-forum.guildwars2.com/discover/6.xml/"
RSS_URL = "https://www.guildwars2.com/en/rss" 

# Configuração das Intents
# Apenas a Message Content é necessária para ler comandos de prefixo
intents = discord.Intents.default()
intents.message_content = True 

# Inicialização do Bot
client = commands.Bot(command_prefix='!', intents=intents)

@tasks.loop(minutes=30)
async def checar_noticias_automaticamente():
    # Espera até que o bot esteja conectado e pronto
    await client.wait_until_ready() 
    canal = client.get_channel(CANAL_ID)
    
    if canal is None:
        print(f"ERRO: Canal com ID {CANAL_ID} não encontrado. Parando a tarefa automática.")
        checar_noticias_automaticamente.stop() 
        return

    # Inicializa o set de links postados (se ainda não existir)
    if not hasattr(client, 'ja_postadas'):
        client.ja_postadas = set()
        
    try:
        feed = feedparser.parse(RSS_URL)
        # O feed está vazio ou houve erro na requisição
        if not feed.entries:
            print(f"Aviso: O feed RSS está vazio ou não pôde ser lido. URL: {RSS_URL}")
            return
            
        novas_noticias = False
        
        # Percorre as notícias em ordem cronológica (da mais antiga para a mais nova)
        for entry in reversed(feed.entries):
            if entry.link not in client.ja_postadas:
                await canal.send(f"📢 **NOVIDADE GUILD WARS 2**\n**{entry.title}**\n{entry.link}")
                client.ja_postadas.add(entry.link)
                novas_noticias = True
                await asyncio.sleep(2) # Pequena pausa para evitar rate limit do Discord
        
        if novas_noticias:
            print("Notícias automáticas postadas com sucesso.")
                
    except Exception as e:
        print(f"Ocorreu um erro durante a checagem automática: {e}")

async def executar_checagem_manual(canal):
    # Inicializa o set de links postados (se ainda não existir)
    if not hasattr(client, 'ja_postadas'):
        client.ja_postadas = set()
        
    try:
        feed = feedparser.parse(RSS_URL)
        
        # Trata o caso do feed estar vazio ou com erro
        if not feed.entries:
            await canal.send("⚠️ **Erro na checagem:** O feed RSS está vazio ou inacessível. Tente verificar a URL.")
            return

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
    # Garante que o comando seja enviado no canal correto (CANAL_ID) para manter a lógica do bot
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
    print(f"✅ Bot conectado como {client.user} (ID: {client.user.id})")
    
    if not hasattr(client, 'ja_postadas'):
        # Tenta carregar as últimas notícias como "já postadas" na inicialização para evitar flood
        print("Inicializando o registro de notícias postadas...")
        feed = feedparser.parse(RSS_URL)
        if feed.entries:
            # Pega os links das últimas 10 notícias para inicializar o set
            client.ja_postadas = {entry.link for entry in feed.entries[:10]}
            print(f"Registradas {len(client.ja_postadas)} notícias iniciais.")
        else:
            client.ja_postadas = set()

    
    if not checar_noticias_automaticamente.is_running():
        print("Tarefa de checagem automática iniciada.")
        checar_noticias_automaticamente.start()

# Bloco de inicialização
if TOKEN:
    try:
        client.run(TOKEN)
    except discord.HTTPException as e:
        print(f"ERRO DE LOGIN: Ocorreu um erro ao fazer login. Verifique o seu TOKEN. Detalhes: {e}")
    except Exception as e:
         print(f"Ocorreu um erro desconhecido na execução: {e}")
else:
    print("ERRO: Token não encontrado na variável de ambiente (verifique o arquivo .env ou a variável de ambiente na hospedagem).")