import requests
import wave
import glob
import json

from base64 import b64encode


# Token and endpoint for the API call
token = 'ak_Pa2KJXLmk8djBKmJLXM6D4ZGeoVQPE3q0Kw9p5RqvzOa7yl2gbWYA1rN04eyQBOG'
endpoint = 'https://tal.ru.is/v1/speech:syncrecognize'

# Folder containing the WAV files
file_list = glob.glob('data/ben/*.wav')   
# Name of the file where response will be written to
output_txt = 'txt/sentences_ben.output.txt'


def main(verbose=False):
    
    # Open text file to write response from API
    out_file = open(output_txt,'w',encoding='utf-8')
    
    # Iterate all WAV files in the directory
    for file in sorted(file_list):
        
        if verbose:
            print(file)
        
        # Open individual file, decode it as utf-8 and cast to base64
        obj = open(file,'rb').read()
        obj64 = str(b64encode(obj).decode("utf-8"))
    
        # Get sample rate of WAV file
        wave_obj = wave.open(file,'r')
        sample_rate = str(wave_obj.getframerate())
    
        # Define headers and data for the API call
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token,
            }
    
        data = '{"config": {"encoding": "LINEAR16", "sampleRate": '\
            + sample_rate + '}, "audio" : {"content": "' + obj64 + '"}}'
    
        # Make the API call
        response = requests.post(endpoint,
                                 headers=headers,
                                 data=data)
    
        # Write selected parts of the response to a file
        data = json.loads(response.text)
        out_file.write(data['results'][0]['alternatives'][0]['transcript'])
        out_file.write('.\n')
        
    out_file.close()
    
    if verbose:
        print('Done!')


if __name__ == "__main__":
    main()