import core
from videoEngine.inference_final import main as vd
from vocalEngine.vox import generate
from inputEngine.stt import stt
import AVController as av
from threading import Thread
from playsound import playsound
import warnings
import torch
import time

## User Vars.
# voice to use
voice = 'avsrc/onenacho.mp3'
# Checkpoint for the video engine to run
video_checkpoint = 'videoEngine/checkpoints/pretrain.pth'
# face to use
face = 'avsrc/src.mp4'
# Audio output storage
vocalFile = 'demo_output_00.wav'

## system vars.
avLock = False

# Init.
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

def inputEngine():
    print('Listening...')
    response = stt()
    if response:
        return response
    else:
        raise RuntimeError('The input engine has encountered an error.')

def processEngine(data_in):
    print('processing data in core...')
    return core.chat(data_in, 'INTERFACE')
    return data_in

def vocalEngine(data_in):
    print('Vocalizing data...')
    generate(voice, data_in)

def videoEngine(data_in):
    global avLock
    avLock = True
    print('Visualizing data...')
    av.playFile(vd(video_checkpoint, face, data_in))
    avLock = False

def idle():
    global avLock
    while True:
        if not avLock:
            avLock - True
            av.playFile(face, False)
            avLock = False

if __name__ == '__main__':
    #Thread(target=idle).start()
    core.init()
    while True:
        input = inputEngine()
        input = processEngine(input)
        time.sleep(2)
        input = vocalEngine(input)
        time.sleep(1)
        playsound(vocalFile)
        torch.cuda.empty_cache()
        print('emptying cache...')
        time.sleep(3)
        #videoEngine(vocalFile)
