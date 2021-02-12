# Exo

*The jankiest project you ever did see*

Exo is a framework for training an AGI chatbot. It implements many different neural nets, including voice synthesis, video synthesis, and (obviously) text generation.

## Installation

Not currently available.

## Usage

```python
import core

core.init()
core.chat('Hey!', userid)
>>> 'How are you?'
```
userid is used to enable holding a conversation with multiple people, while remembering the context of the conversation.
### Telegram Integration
Use exo-telegram.py, along with a [bot API token](https://t.me/botfather), to host your AI on Telegram.

## Contributing
Contributing is greatly appreciated, please contact one of the team members to get started working on the codebase.

## Todo
#### Core
- Finalize content filter
- Add response ranking via a point system
- Add sentiment analysis for proper emotions
- fix ```CUDA out of memory.``` error after running for too long
- Fully redo the logging system
#### Full Engine
- Finish the vocal engine
- Integrate all parts into a seamless user experience
