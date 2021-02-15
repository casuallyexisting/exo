# Exo

*The jankiest project you ever did see*

Exo is a framework for training an AGI chatbot. It implements many different neural nets, including voice synthesis, video synthesis, and (obviously) text generation.

## Installation

Not currently available.

## Usage
*Still working on making everything user-friendly*

- Connect to socket at address 127.0.0.1 on port 25077
```python
socket.sendall(b'userid://message')
data = sock.recv(16384)
print(data)
>>> 'How are you?'
```
userid is used to enable holding a conversation with multiple people, while remembering the context of the conversation.
### Telegram Integration
*Currently Deprecated*
Use exo-telegram.py, along with a [bot API token](https://t.me/botfather), to host your AI on Telegram.
### Discord Integration
Use exo-discord.py, along with a [bot API token](https://discord.com/developers/applications), to host your AI on discord.
A good guide for setting up a discord bot can be found [here](https://realpython.com/how-to-make-a-discord-bot-python/).

## Contributing
Contributing is greatly appreciated, please contact one of the team members to get started working on the codebase.

## Todo
#### Core
- Finalize content filter
- Add response ranking via a point system
- Add sentiment analysis for proper emotions
#### Window Engine
- Finish the vocal engine
- Integrate all parts into a seamless user experience
#### Telegram
- Finish updating bot to use sockets
