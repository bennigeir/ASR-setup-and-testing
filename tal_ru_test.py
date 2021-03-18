import requests
import wave

from base64 import b64encode


token = 'Bearer ak_Pa2KJXLmk8djBKmJLXM6D4ZGeoVQPE3q0Kw9p5RqvzOa7yl2gbWYA1rN04eyQBOG'
obj = open('data/flight01_benedikt.wav','rb').read()
obj64 = str(b64encode(obj).decode("utf-8"))

headers = {
    'Content-Type': 'application/json',
    'Authorization': token,
}

data = '{"config": {"encoding": "LINEAR16", "sampleRate": 44100}, "audio" : {"content": "' + obj64 + '"}}'

response = requests.post('https://tal.ru.is/v1/speech:syncrecognize',
                         headers=headers,
                         data=data)

print(response.text)