## logging
import logging
logger = logging.getLogger(__name__)

## Command Functions
priveliged_commands = ['core','globalhistory', 'userstatus', 'g-clearchat']
def help(user_id, operators):
    #from core import operators
    message = """Sudo commands:
- help : Lists commands
- sudo : Activates operator mode
- debug. <msg> : Debugs input
- beam. <msg> : Multi-response to input
- globalbeam : Toggles beam globally
- errortest : Throws error
- userid : Displays your userID
- chathistory : Displays your history
- clearchat : Clears your history"""

    if user_id in operators:
        message += '\n\n'
        message += """Operator Commands:
- core : Displays core and system info
- globalhistory : Displays global history
- userstatus : Displays user statuses
- g-clearchat : Clears all current chats"""
    return message

def sudoer(command, user_id, user_status, current_history, personality, player, config, operators, device):
    #from core import user_status, current_history, personality, player, config, operators, device
    # External Commands
    if command == "help":
        return help(user_id, operators)
    # Operator Commands
    if command in priveliged_commands and user_id in operators:
        if command == 'core':
            return 'Personality: ' + str(personality) + '\nPlayer: ' + str(player) + '\nEngine: ' + str(config['model_type']) + '\nModel: ' + str(config['model_name_or_path'])[:-1] + '\nHardware: ' + str(device)
        elif command == 'globalhistory':
            return current_history
        elif command == 'userstatus':
            return user_status
        elif command == 'g-clearchat':
            current_history = {}
            return 'Global Chat Cleared.'
    elif command in priveliged_commands and user_id not in operators:
        return "Invalid Credentials."
    # Sudoer Commands
    elif command == 'chathistory':
        if current_history[user_id]:
            return current_history[user_id]
        else:
            return 'No history found.'
    elif command == 'userid':
        return user_id
    elif command.split('. ')[0] == 'debug':
        return command.split('. ')
    elif command.split('. ')[0] == 'beam':
        return command.split('. ')
    elif command == 'globalbeam':
        if user_status[user_id]['status'] == 'normal':
            user_status[user_id]['status'] = 'globalbeam'
        else:
            user_status[user_id]['status'] = 'normal'
        return 'Status set to ' + user_status[user_id]['status']
    elif command == 'clearchat':
        #global current_history
        current_history[user_id] = ''
        return 'Current History Cleared.'
    elif command == 'errortest':
        raise RuntimeError('Sudoer has tested the error function -- No need to worry.')
    # Else
    else:
        return "Invalid Command: exit sudo to chat, or run 'help' to list commands."

## Firewall Functions
import random
import json
def firewall(cur_input):
    coreConfig = json.load(open("config/rxConfig.json"))
    coreConfig = coreConfig['coreConfig']
    content_filter = json.load(open("utils/content_filter.json"))
    intercepted_messages = content_filter['intercepted_messages']
    banned_phrases = content_filter['banned_phrases']
    responses_to_banned_inputs = content_filter['responses_to_banned_inputs']

    if cur_input.lower() in intercepted_messages:
        return intercepted_messages[cur_input]

    for response in banned_phrases:
        try:
            response = response.split('//')
        except:
            response = [response, '']
        if response[0] in cur_input and response[1] in cur_input:
            logger.info('Banned message intercepted! Message: ' + cur_input)
            return responses_to_banned_inputs[random.randrange(len(responses_to_banned_inputs)-1)] + '\n(Message Blocked.)'
    return cur_input
