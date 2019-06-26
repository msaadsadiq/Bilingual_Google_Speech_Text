import io
import os
import json
import sys


filename = sys.argv[1]

def transcribe_gcs(gcs_uri, language_code):

    data = {}
    wordjson= {}
    results = list()
    
    """Asynchronously transcribes the audio file specified by the gcs_uri."""
    from google.cloud import speech
    from google.cloud.speech import enums
    from google.cloud.speech import types
    client = speech.SpeechClient()
    audio = types.RecognitionAudio(uri=gcs_uri)
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=44100,
        language_code=language_code,
        enable_word_time_offsets=True
        )
    operation = client.long_running_recognize(config, audio)
    response = operation.result(timeout=99999999)
    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    
    for result in response.results:
        rst = dict()
        rst['transcript'] = result.alternatives[0].transcript
        rst['confidence'] = result.alternatives[0].confidence
        rst['words'] = list()
        for w in result.alternatives[0].words:
            rst['words'].append({
                'word': w.word,
                'start_time': w.start_time.seconds + w.start_time.nanos * 1e-9,
                'end_time': w.end_time.seconds + w.end_time.nanos * 1e-9
            })
        results.append(rst)

    return(results)

def merge(spanish, english):
    spanish_upd = []
    english_upd = []
    combined = []
    
    for sentence in spanish:
        for elem in sentence.values():
            spanish_upd.append(elem)
    
    for i in range(int(len(spanish_upd)/3)):
        #for j in range()
        for j in range(len(spanish_upd[i*3+2])):
            spanish_upd[i*3+2][j].update({'confidence':spanish_upd[i*3+1], 'Lang':'sp'})
        combined.append(spanish_upd[i*3+2])

    for sentence in english:
        for elem in sentence.values():
            english_upd.append(elem)
    
    for i in range(int(len(english_upd)/3)):
        #for j in range()
        for j in range(len(english_upd[i*3+2])):
            english_upd[i*3+2][j].update({'confidence':english_upd[i*3+1], 'Lang':'en'})
        combined.append(english_upd[i*3+2])

    combined = [item for sublist in combined for item in sublist]    
    return(combined)


def sort_on_confidence(combined):
    from operator import itemgetter
    combined.sort(key=itemgetter('start_time'))
    


def main(filename):
    results_sp = transcribe_gcs('gs://bilingualaudio/'+filename, 'es-US')
    results_en = transcribe_gcs('gs://bilingualaudio/'+filename, 'en-US')

    combined = merge(results_sp, results_en)
    
    saveJson = os.path.splitext(filename)[0]
    with open('./sp_'+saveJson+'.json', 'w') as outfile:
        json.dump(results_sp, outfile)

    saveJson = os.path.splitext(filename)[0]
    with open('./en_'+saveJson+'.json', 'w') as outfile:
        json.dump(results_en, outfile)


if __name__ == '__main__':
    main(filename)
    with open('sp_Sample_sp_en.json') as json_file:
        spanish = json.load(json_file)
    with open('en_sample_sp_en.json') as json_file:
        english = json.load(json_file)

    combined = merge(spanish, english)
    sort_on_confidence(combined)
