import os
import discord
from dotenv import load_dotenv
import json
import asyncio
import socket

config = json.load(open("../config/rxConfig.json"))

TOKEN = config['discord_config']['token']
client = discord.Client()

HOST = "127.0.0.1"
PORT = 25077

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if not message.content.startswith('!!'):
        sock = socket.socket()
        sock.connect((HOST, PORT))
        outbound_message = 'DISCORD-{}://'.format(message.author.id) + message.content
        sock.sendall(outbound_message.encode('utf-8'))
        data = sock.recv(16384)
        response = data.decode()
        sock.close()
        await message.channel.send(response)

client.run(TOKEN)
