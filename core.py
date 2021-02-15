#!/usr/bin/env python3
# coding=utf-8
# Copyright 2018 Google AI, Google Brain and Carnegie Mellon University Authors and the HuggingFace Inc. team.
# Copyright (c) 2018, NVIDIA CORPORATION.  All rights reserved.
# Copyright (c) 2021, Mason Coles.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import logging
import numpy as np
import torch
import random
from datetime import datetime
import time
import json
import socket
import threading
from utils.intercept import sudoer, firewall
from transformers import (
    GPT2LMHeadModel,
    GPT2Tokenizer,
)

# Logging Configuration
logging.basicConfig(
    format="[%(levelname)-8s]: %(asctime)s - CORE -   %(message)s", datefmt="%m/%d/%Y %H:%M:%S", level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Global Variable Declaration
coreConfig = json.load(open("config/rxConfig.json"))
coreConfig = coreConfig['coreConfig']
custom_player = coreConfig['custom_player']
sudoers = coreConfig['sudoers']
operators = coreConfig['operators']
current_history = {}
user_status = {}
running = True
MAX_LENGTH = int(10000)  # Hardcoded max length to avoid infinite loop
torrent_address = '127.0.0.1'
torrent_port = 25077
torrent_threads = 5

# Config Definitions
config = json.load(open("config/generation_config.json"))
repetition_penalty = config['repetition_penalty']
num_return_sequences = 1
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
n_gpu = torch.cuda.device_count()

logging.debug('Using device ' + str(device))

# Set seed
np.random.seed(42)
torch.manual_seed(42)
if n_gpu > 0:
    torch.cuda.manual_seed_all(42)

# Set User
usernames = []
with open(config['model_name_or_path'] + "Usernames.txt") as users_file:
    for line in users_file.read().splitlines():
        usernames.append(line)
player = ""
try:
    player = custom_player
except:
    raise ValueError('Character not in config.')

launchTime = time.strftime('%Y-%m-%d_%H.%M.%S')
personality = ''
for name in usernames:
    if name != player:
        personality += name + ', '

# Initialize the model and tokenizer
tokenizer = GPT2Tokenizer.from_pretrained(config['model_name_or_path'])
model = GPT2LMHeadModel.from_pretrained(config['model_name_or_path'])
model.to(device)

# Define length and check for compatibility with model
length = config['length']
if not length <= model.config.max_position_embeddings:
    raise ValueError('Defined length exceeds maximum model size.')

# Open socket
torrent = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
torrent.bind((torrent_address, torrent_port))
torrent.listen(torrent_threads)
logger.debug('Socket {}:{} open.'.format(torrent_address, torrent_port))

def chat(custom_input, user_id):
    global current_history
    prompt_text = ''
    try:
        temp = user_status[user_id]['status']
    except:
        user_status[user_id] = {'debug':False, 'status': 'normal'}

    if user_status[user_id]['debug']:
        logging.debug('[' + user_id + ' > Sudoer] ' + custom_input)
    else:
        logging.debug('[' + user_id + ' > AI] ' + custom_input)

    current_debug = ''
    cur_input = custom_input

    if cur_input == "sudo" and user_id in sudoers:
        user_status[user_id]['debug'] = not user_status[user_id]['debug']
        if user_status[user_id]['debug']:
            stat_db = 'Enabled'
        else:
            stat_db = 'Disabled'
        return "Sudo is now {}".format(stat_db)
    elif cur_input == "sudo" and user_id not in sudoers:
        return "Permission Denied."

    if user_status[user_id]['debug']:
        sudone = sudoer(cur_input, user_id)
        if isinstance(sudone, list):
            if sudone[0] == 'debug':
                cur_input = sudone[1]
            elif sudone[0] == 'beam':
                user_status[user_id]['debug'] = False
                user_status[user_id]['status'] = 'beam'
            else:
                raise SyntaxError('Sudo command failed.')
        else:
            return sudone

    try:
        prompt_text = current_history[user_id]
    except:
        logging.info('New chat started with user {}'.format(user_id))
        pass

    if cur_input != firewall(cur_input):
         return firewall(cur_input)
    #if it's blank, don't add anything (let the AI keep talking)
    if cur_input != "":
        prompt_text += (player + ": " + cur_input)
        prompt_text += "\n"
    #trim lengthy inputs (basically rolling memory)
    if len(prompt_text) > 1000:
        prompt_text = prompt_text[len(prompt_text)-1000:]

    encoded_prompt = tokenizer.encode(prompt_text, add_special_tokens=False, return_tensors="pt")
    encoded_prompt = encoded_prompt.to(device)

    if encoded_prompt.size()[-1] == 0:
        input_ids = None
    else:
        input_ids = encoded_prompt

    if user_status[user_id]['debug']:
        current_debug = current_debug + "\nINPUTTED PROMPT: \n{}".format(prompt_text) + '\n'

    output_sequences= model.generate(
        input_ids=input_ids,
        max_length=length + len(encoded_prompt[0]),
        temperature=config['temperature'],
        top_k=config['k'],
        top_p=0.9,
        pad_token_id=50256,
        repetition_penalty=repetition_penalty,
        do_sample=True,
        num_return_sequences=num_return_sequences,
    )
    # Remove the batch dimension when returning multiple sequences
    if len(output_sequences.shape) > 2:
        output_sequences.squeeze_()

    generated_sequences = []
    for generated_sequence_idx, generated_sequence in enumerate(output_sequences):
        generated_sequence = generated_sequence.tolist()
        # Decode text
        text = tokenizer.decode(generated_sequence, clean_up_tokenization_spaces=True)
        # combine prompt w/ output. Only use first line of output response. clean up padding text
        #all the lines of ai text
        ai_lines = text[len(tokenizer.decode(encoded_prompt[0], clean_up_tokenization_spaces=True)) :].splitlines()
        if user_status[user_id]['debug']:
            current_debug = current_debug + "\n\nDEBUG -\nAI OUTPUT LINES:"
            current_debug = current_debug + str(ai_lines)
        #AI often starts with a new line for some reason
        if ai_lines[0] == "":
            ai_lines = ai_lines[1:]
        #check if the AI responded as someone else; if so, append the response
        done = 0
        for line in ai_lines:
            for user in usernames:
                if line.startswith(user) and user != player:
                    generated_sequences.append(line)
                    done = 1
                    break
            if done:
                break
    if len(generated_sequences) == 0:
        return "No response :("
    # Prompt text formatting
    prompt_text += generated_sequences[0]
    prompt_text += "\n"
    current_history[user_id] = prompt_text

    returned_response = generated_sequences[0].split(': ')

    if user_status[user_id]['status'] == 'beam' or user_status[user_id]['status'] == 'globalbeam':
        for index, sequence in enumerate(generated_sequences):
            generated_sequences[index] = sequence.split(': ')[1]
        returned_response = ''
        for response in generated_sequences:
            returned_response = returned_response + '- ' + response + '\n'
        if user_status[user_id]['status'] == 'beam':
            user_status[user_id]['debug'] = True
            user_status[user_id]['status'] = 'Normal'
        logging.debug('[AI > ' + user_id + '] BEAM OUTPUT:\n' + returned_response)
        return 'BEAM OUTPUT (' + str(len(generated_sequences)) + ' reponses generated):\n' + returned_response

    logging.debug('[AI > ' + user_id + '] ' + returned_response[1])
    returned_response = str(returned_response[1]) + str(current_debug)
    return returned_response

def manage_client(client_socket):
    try:
        request = client_socket.recv(1024)
        request = request.decode()
        request = request.split('://', 1)
        client_socket.send(chat(request[1], request[0]).encode('utf-8'))
        client_socket.close()
    except:
        logger.warning('Client Disconnected.')

logger.info('Ready for connections.')
while True:
    client, addr = torrent.accept()
    logger.debug("[*] Accepted connection from: {}:{}".format(addr[0], addr[1]))
    client_handler = threading.Thread(target=manage_client, args=(client,))
    client_handler.start()
