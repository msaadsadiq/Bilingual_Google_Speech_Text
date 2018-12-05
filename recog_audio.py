import os
import argparse
import json
from pathlib import Path
from pydub import AudioSegment
from pydub.utils import make_chunks


def transcribe_file(gcs_uri, output, language):
    """Transcribe the given audio file asynchronously and save the most likely results."""
    from google.cloud import speech
    from google.cloud.speech import enums
    from google.cloud.speech import types
    client = speech.SpeechClient()

    audio = types.RecognitionAudio(uri=gcs_uri)
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.FLAC,
        sample_rate_hertz=16000,
        language_code=language,
        enable_word_time_offsets=True
    )

    # [START migration_async_response]
    operation = client.long_running_recognize(config, audio)
    # [END migration_async_request]

    print('Waiting for operation to complete...')
    response = operation.result(timeout=None)

    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    results = list()
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

    filename = gcs_uri.split('/')[-1]
    with open('{}/{}'.format(output, filename.replace('.flac', '.json')), 'w') as f:
        json.dump(results, f)
    with open('{}/{}'.format(output, filename.replace('.flac', '.txt')), 'w') as f:
        for result in response.results:
            # The first alternative is the most likely one for this portion.
            f.write(u'Transcript: {}\n'.format(result.alternatives[0].transcript))
            f.write('Confidence: {}\n'.format(result.alternatives[0].confidence))
    # [END migration_async_response]


def upload_file(local_path, bucket_name, blob_path):
    """Uploads a file to the GCS bucket."""
    from google.cloud import storage

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_path)

    blob.upload_from_filename(local_path)

    print('File \"{}\" uploaded to \"gs://{}/{}\".'.format(local_path, bucket_name, blob_path))


def convert_and_split_speech_file(local_path, format, max_len):
    """Load local speech file, convert to .flac format and slice to small chucks"""
    speech = AudioSegment.from_file(local_path, format)
    chucks = make_chunks(speech, max_len * 1000)
    suffix = Path(local_path).suffix
    filenames = list()
    if len(chucks) == 1:
        if suffix == '.flac':
            filenames.append(local_path)
        else:
            filename = local_path.replace(suffix, '.flac')
            print('Exporting {}'.format(filename))
            chucks[0].export(filename, format='flac')
            filenames.append(filename)
    else:
        for i, chuck in enumerate(chucks):
            filename = local_path.replace(suffix, '_{}.flac'.format(i+1))
            print('Exporting {}'.format(filename))
            chuck.export(filename, format='flac')
            filenames.append(filename)

    return filenames

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Speech Recognition via GCP')
    parser.add_argument('credential', help='The local path to the GCP service account key file')
    parser.add_argument('bucket', help='The basket name in GCP storage')
    parser.add_argument('output_path', help='The path to the local directory to store the outputs')
    parser.add_argument('-l', '--local_path', help='The local path to the speech file (Will be uploaded first)')
    parser.add_argument('-c', '--cloud_path', default='',
                        help='The directory in GCP storage to save the speech file or '
                             'the path to the speech file to recognize')
    parser.add_argument('--format', help='The audio format', default='wav')
    parser.add_argument('--maxlen', help='The length of each speech chuck in seconds', default=3540, type=int)
    parser.add_argument('--language', default='en-US', help='The language of the speech')
    args = parser.parse_args()

    if Path(args.credential).exists():
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = args.credential
    else:
        raise FileNotFoundError('Cannot find the GCP service account key file: {}'.format(args.credential))

    if args.local_path is not None:
        local_file = Path(args.local_path)
        if local_file.exists() and local_file.is_file():
            files = convert_and_split_speech_file(args.local_path, args.format, args.maxlen)
            for file in files:
                name = Path(file).name
                upload_file(file, args.bucket, args.cloud_path + name)
                transcribe_file('gs://{}/{}'.format(args.bucket, args.cloud_path + name), args.output_path, args.language)
        else:
            raise FileNotFoundError('Cannot find the local speech file: {}'.format(args.local_path))
    else:
        transcribe_file('gs://{}/{}'.format(args.bucket, args.cloud_path), args.output_path, args.language)
