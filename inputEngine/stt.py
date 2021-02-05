# NOTE: this example requires PyAudio because it uses the Microphone class

import speech_recognition as sr

def stt():
    # obtain audio from the microphone
    r = sr.Recognizer()
    with sr.Microphone() as source:
        # print('speak: ')
        audio = r.listen(source)

    # recognize speech using Sphinx
    try:
        # print("Interpreted Response: " + r.recognize_sphinx(audio)) # What (we think) the person said
        return r.recognize_sphinx(audio)
    except sr.UnknownValueError:
        # print("You were not understood.")
        return "What did you say? I couldn't hear you."
    except sr.RequestError as e:
        raise "SphinxError: {0}".format(e)
        return False

if __name__ == '__main__':
    while True:
        stt()
