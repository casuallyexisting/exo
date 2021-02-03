#!/usr/bin/env python3
# coding=utf-8
# Copyright 2018 Google AI, Google Brain and Carnegie Mellon University Authors and the HuggingFace Inc. team.
# Copyright (c) 2018, NVIDIA CORPORATION.  All rights reserved.
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
""" Conditional text generation with the auto-regressive models of the library (GPT/GPT-2/CTRL/Transformer-XL/XLNet)
"""

from config.rxConfig import coreConfig
import argparse
import logging
import numpy as np
import torch
import random
from datetime import datetime
import time
import json
from transformers import (
    CTRLLMHeadModel,
    CTRLTokenizer,
    GPT2LMHeadModel,
    GPT2Tokenizer,
    OpenAIGPTLMHeadModel,
    OpenAIGPTTokenizer,
    TransfoXLLMHeadModel,
    TransfoXLTokenizer,
    XLMTokenizer,
    XLMWithLMHeadModel,
    XLNetLMHeadModel,
    XLNetTokenizer,
)

custom_player = coreConfig['custom_player']
opped_users = coreConfig['opped_users']
priveliged_users = coreConfig['priveliged_users']

current_history = {}
user_status = {}
running = True
chatlogging = True

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s -   %(message)s", datefmt="%m/%d/%Y %H:%M:%S", level=logging.WARNING,
)
logger = logging.getLogger(__name__)

MAX_LENGTH = int(10000)  # Hardcoded max length to avoid infinite loop
MODEL_CLASSES = {
    "gpt2": (GPT2LMHeadModel, GPT2Tokenizer),
    "ctrl": (CTRLLMHeadModel, CTRLTokenizer),
    "openai-gpt": (OpenAIGPTLMHeadModel, OpenAIGPTTokenizer),
    "xlnet": (XLNetLMHeadModel, XLNetTokenizer),
    "transfo-xl": (TransfoXLLMHeadModel, TransfoXLTokenizer),
    "xlm": (XLMWithLMHeadModel, XLMTokenizer),
}

# Padding text to help Transformer-XL and XLNet with short prompts as proposed by Aman Rusia
# in https://github.com/rusiaaman/XLNet-gen#methodology
# and https://medium.com/@amanrusia/xlnet-speaks-comparison-to-gpt-2-ea1a4e9ba39e
PADDING_TEXT = """In 1991, the remains of Russian Tsar Nicholas II and his family
(except for Alexei and Maria) are discovered.
The voice of Nicholas's young son, Tsarevich Alexei Nikolaevich, narrates the
remainder of the story. 1883 Western Siberia,
a young Grigori Rasputin is asked by his father and a group of men to perform magic.
Rasputin has a vision and denounces one of the men as a horse thief. Although his
father initially slaps him for making such an accusation, Rasputin watches as the
man is chased outside and beaten. Twenty years later, Rasputin sees a vision of
the Virgin Mary, prompting him to become a priest. Rasputin quickly becomes famous,
with people, even a bishop, begging for his blessing. <eod> </s> <eos>"""

def set_seed(args):
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    if args.n_gpu > 0:
        torch.cuda.manual_seed_all(args.seed)

def set_seed_int(new_seed):
    np.random.seed(new_seed)
    torch.manual_seed(new_seed)

def prepare_ctrl_input(args, _, tokenizer, prompt_text):
    if args.temperature > 0.7:
        logger.info("CTRL typically works better with lower temperatures (and lower top_k).")

    encoded_prompt = tokenizer.encode(prompt_text, add_special_tokens=False)
    if not any(encoded_prompt[0] == x for x in tokenizer.control_codes.values()):
        logger.info("WARNING! You are not starting your generation from a control code so you won't get good results")
    return prompt_text

def prepare_xlm_input(args, model, tokenizer, prompt_text):
    # Set the language
    use_lang_emb = hasattr(model.config, "use_lang_emb") and model.config.use_lang_emb
    if hasattr(model.config, "lang2id") and use_lang_emb:
        available_languages = model.config.lang2id.keys()
        if args.xlm_language in available_languages:
            language = args.xlm_language
        else:
            language = None
            while language not in available_languages:
                language = input("Using XLM. Select language in " + str(list(available_languages)) + " >>> ")

        model.config.lang_id = model.config.lang2id[language]
    return prompt_text

def prepare_xlnet_input(args, _, tokenizer, prompt_text):
    prompt_text = (args.padding_text if args.padding_text else PADDING_TEXT) + prompt_text
    return prompt_text

def prepare_transfoxl_input(args, _, tokenizer, prompt_text):
    prompt_text = (args.padding_text if args.padding_text else PADDING_TEXT) + prompt_text
    return prompt_text

PREPROCESSING_FUNCTIONS = {
    "ctrl": prepare_ctrl_input,
    "xlm": prepare_xlm_input,
    "xlnet": prepare_xlnet_input,
    "transfo-xl": prepare_transfoxl_input,
}

def adjust_length_to_model(length, max_sequence_length):
    if length < 0 and max_sequence_length > 0:
        length = max_sequence_length
    elif 0 < max_sequence_length < length:
        length = max_sequence_length  # No generation bigger than model size
    elif length < 0:
        length = MAX_LENGTH  # avoid infinite loop
    return length

def init():
    global args, usernames, player, tokenizer, model, launchTime, personality, model_type, model_name_or_path
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_type", default=None, type=str, required=False, help="Model type selected in the list: " + ", ".join(MODEL_CLASSES.keys()))
    parser.add_argument("--model_name_or_path", default=None, type=str, required=False, help="Path to pre-trained model or shortcut name selected in the list: " + ", ".join(MODEL_CLASSES.keys()))
    parser.add_argument("--length", type=int, default=20)
    parser.add_argument("--stop_token", type=str, default=None, help="Token at which text generation is stopped")
    parser.add_argument("--temperature", type=float, default=1.0, help="temperature of 1.0 has no effect, lower tend toward greedy sampling")
    parser.add_argument("--repetition_penalty", type=float, default=1.0, help="primarily useful for CTRL model; in that case, use 1.2")
    parser.add_argument("--k", type=int, default=0)
    parser.add_argument("--p", type=float, default=0.9)
    parser.add_argument("--padding_text", type=str, default="", help="Padding text for Transfo-XL and XLNet.")
    parser.add_argument("--xlm_language", type=str, default="", help="Optional language when used with the XLM model.")
    parser.add_argument("--seed", type=int, default=42, help="random seed for initialization")
    parser.add_argument("--no_cuda", action="store_true", help="Avoid using CUDA when available")
    parser.add_argument("--num_return_sequences", type=int, default=1, help="The number of samples to generate.")

    config = json.load(open("config/generation_config.json"))
    parser.set_defaults(**config)
    args = parser.parse_args()
    args.device = torch.device("cuda" if torch.cuda.is_available() and not args.no_cuda else "cpu")
    args.n_gpu = 0 if args.no_cuda else torch.cuda.device_count()
    print('using device ' + str(args.device))
    set_seed(args)

    usernames = []
    with open(args.model_name_or_path + "Usernames.txt") as users_file:
        for line in users_file.read().splitlines():
            usernames.append(line)
    player = ""
    try:
        player = custom_player
    except:
        raise ValueError('Character not in config.')
    # Initialize the model and tokenizer
    try:
        args.model_type = args.model_type.lower()
        model_class, tokenizer_class = MODEL_CLASSES[args.model_type]
    except KeyError:
        raise KeyError("the model {} you specified is not supported. You are welcome to add it and open a PR :)")
    tokenizer = tokenizer_class.from_pretrained(args.model_name_or_path)
    model = model_class.from_pretrained(args.model_name_or_path)
    model.to(args.device)
    args.length = adjust_length_to_model(args.length, max_sequence_length=model.config.max_position_embeddings)
    logger.info(args)

    launchTime = time.strftime('%Y-%m-%d_%H.%M.%S')
    personality = ''
    for name in usernames:
        if name != player:
            personality += name + ', '
    model_type = args.model_type
    model_name_or_path = args.model_name_or_path
    global sudoer, firewall
    from private_functions import sudoer, firewall

def log(log_input):
    with open("logs/log_{}.rx0".format(launchTime), 'a+', encoding='utf-8') as file:
        file.write(log_input + '\n')

def chat(custom_input, user_id):
    global current_history, chatlogging
    prompt_text = ''
    try:
        temp = user_status[user_id]['status']
    except:
        user_status[user_id] = {'debug':False, 'status': 'normal'}

    if user_status[user_id]['debug']:
        print('[' + user_id + ' > Sudoer] ' + custom_input)
    else:
        print('[' + user_id + ' > AI] ' + custom_input)

    current_debug = ''
    cur_input = custom_input
    if chatlogging:
        log(player + ': ' + str(cur_input))

    if cur_input == "sudo" and user_id in opped_users:
        user_status[user_id]['debug'] = not user_status[user_id]['debug']
        if user_status[user_id]['debug']:
            stat_db = 'Enabled'
        else:
            stat_db = 'Disabled'
        return "Sudo is now {}".format(stat_db)
    elif cur_input == "sudo" and user_id not in opped_users:
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
        print('New chat started with user', user_id)
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
    # Different models need different input formatting and/or extra arguments
    requires_preprocessing = args.model_type in PREPROCESSING_FUNCTIONS.keys()
    if requires_preprocessing:
        prepare_input = PREPROCESSING_FUNCTIONS.get(args.model_type)
        preprocessed_prompt_text = prepare_input(args, model, tokenizer, prompt_text)

        if model.__class__.__name__ in ["TransfoXLLMHeadModel"]:
            tokenizer_kwargs = {"add_space_before_punct_symbol": True}
        else:
            tokenizer_kwargs = {}

        encoded_prompt = tokenizer.encode(
            preprocessed_prompt_text, add_special_tokens=False, return_tensors="pt", **tokenizer_kwargs
        )
    else:
        encoded_prompt = tokenizer.encode(prompt_text, add_special_tokens=False, return_tensors="pt")
    encoded_prompt = encoded_prompt.to(args.device)

    if encoded_prompt.size()[-1] == 0:
        input_ids = None
    else:
        input_ids = encoded_prompt

    if user_status[user_id]['debug']:
        current_debug = current_debug + "\nINPUTTED PROMPT: \n{}".format(prompt_text) + '\n'

    output_sequences= model.generate(
        input_ids=input_ids,
        max_length=args.length + len(encoded_prompt[0]),
        temperature=args.temperature,
        top_k=args.k,
        top_p=args.p,
        pad_token_id=50256,
        repetition_penalty=args.repetition_penalty,
        do_sample=True,
        num_return_sequences=args.num_return_sequences,
    )
    # Remove the batch dimension when returning multiple sequences
    if len(output_sequences.shape) > 2:
        output_sequences.squeeze_()

    generated_sequences = []
    for generated_sequence_idx, generated_sequence in enumerate(output_sequences):
        generated_sequence = generated_sequence.tolist()
        # Decode text
        text = tokenizer.decode(generated_sequence, clean_up_tokenization_spaces=True)
        # Remove all text after the stop token
        text = text[: text.find(args.stop_token) if args.stop_token else None]
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
        if chatlogging:
            log('No Response :(')
        return "No response :("
    # Prompt text formatting
    prompt_text += generated_sequences[0]
    prompt_text += "\n"
    current_history[user_id] = prompt_text

    returned_response = generated_sequences[0].split(': ')
    if chatlogging:
        log(returned_response[0])

    if user_status[user_id]['status'] == 'beam' or user_status[user_id]['status'] == 'globalbeam':
        for index, sequence in enumerate(generated_sequences):
            generated_sequences[index] = sequence.split(': ')[1]
        returned_response = ''
        for response in generated_sequences:
            returned_response = returned_response + '- ' + response + '\n'
        if user_status[user_id]['status'] == 'beam':
            user_status[user_id]['debug'] = True
            user_status[user_id]['status'] = 'Normal'
        print('[AI > ' + user_id + '] BEAM OUTPUT:\n' + returned_response)
        return 'BEAM OUTPUT (' + str(len(generated_sequences)) + ' reponses generated):\n' + returned_response

    print('[AI > ' + user_id + '] ' + returned_response[1])
    returned_response = str(returned_response[1]) + str(current_debug)
    return returned_response
