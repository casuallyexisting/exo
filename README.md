# Exo

*The jankiest project you ever did see*

Exo is the platform for running custom conversational AI models. To train your own, see the model creation repository [here](https://github.com/casuallyexisting/exo-model-creation)

## Installation
Clone the repository and modify the config files found in 'config/'
### generation_config
- Set the model path
### rxConfig
- Set any username as the 'custom_player' (Used so the AI can keep track of who's who)
- Set the User ID's of users to have elevated priveliges. Discord IDs are formatted as 'DISCORD-<User ID>', Telegram IDs are 'TELEGRAM-<User ID>', and Terminal is simply 'TERMINAL'.
  - Sudoers have access to commands that affect their experience, such as debugging their chat. Operators have access to commands that directly affect how the AI is operating for everyone, as well as seeing system and model information.
- If using Telegram and/or Discord, set the token values while setting up the bot in the 'Usage' section.

## Usage
### Terminal Access
Run 'interfaces/exo-terminal.py' to open a chat in the terminal with the AI. This uses the user ID 'TERMINAL'.
### Telegram Integration
Use exo-telegram.py, along with a [bot API token](https://t.me/botfather), to host your AI on Telegram. Run 'interfaces/exo-telegram.py' to connect the Discord bot to the AI.
### Discord Integration
Use exo-discord.py, along with a [bot API token](https://discord.com/developers/applications), to host your AI on discord. Run 'interfaces/exo-discord.py' to connect the Discord bot to the AI.
A good guide for setting up a discord bot can be found [here](https://realpython.com/how-to-make-a-discord-bot-python/).
### Custom Integration
- Connect to socket at address 127.0.0.1 on port 25077
```python
socket.sendall(b'userid://message')
data = sock.recv(16384)
print(data)
>>> 'response'
```

## Contributing
Contributing is greatly appreciated, please contact one of the team members to get started working on the codebase.

## Todo
#### Core
- Add response ranking via a point system
- Add sentiment analysis for proper emotions
#### Window Engine
- Finish the vocal engine
- Integrate all parts into a seamless user experience
