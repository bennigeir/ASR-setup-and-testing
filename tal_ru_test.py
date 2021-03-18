import requests
import wave
import glob

from base64 import b64encode

file_list = glob.glob('data/isi/*.wav')   
out_file = open('txt/sentences.output.txt','w',encoding='utf-8')
for file in file_list:
    token = 'Bearer ak_Pa2KJXLmk8djBKmJLXM6D4ZGeoVQPE3q0Kw9p5RqvzOa7yl2gbWYA1rN04eyQBOG'
    obj = open(file,'rb').read()
    obj64 = str(b64encode(obj).decode("utf-8"))

    wave_obj = wave.open(file,'r')
    sample_rate = str(wave_obj.getframerate())

    headers = {
        'Content-Type': 'application/json',
        'Authorization': token,
        }

    data = '{"config": {"encoding": "LINEAR16", "sampleRate": ' + sample_rate + '}, "audio" : {"content": "' + obj64 + '"}}'

    response = requests.post('https://tal.ru.is/v1/speech:syncrecognize',
                             headers=headers,
                             data=data)

    out_file.write(response.text[44:-6])
    out_file.write('.\n')
out_file.close()

