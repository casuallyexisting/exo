from videoEngine.inference_final import main as vd

ckpt = 'videoEngine/checkpoints/pretrain.pth'
face = 'avsrc/biden.mp4'
audio = 'avsrc/your_mom.mp3'

vd(ckpt, face, audio)
