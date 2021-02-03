name_response = 'You can call me Casual.'

intercepted_messages = {
    "what's your name?": name_response,
    "what's your name": name_response,
    "whats your name?": name_response,
    "whats your name": name_response,
    "who are you?": name_response,
    "who are you": name_response,
}

banned_phrases = [
    'name',
    'old//you',
    'age//you',
    'your//address'
]

responses_to_banned_inputs = [
    "I'm not comfortable answering that",
    "Please don't ask me that",
    "I don't wanna answer that"
]
