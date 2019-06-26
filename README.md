# Converting bilingual (Spanish-English) speech audio files to text using Google's Cloud Speech-to-Text API
# Bi-lingual Text Transcription - English and Spanish mixed speech

This repo contains a python based approach, to trascribe bilingual speech. Currently there is no single method to transcribe bilingual speech. Thus, we transcribe separately and combine them together to create a single text file. All steps to setup the cloud environment are provided below. This approach converts long audio files that are > 1min but < 1hour. 


File type
.wav
32 bit
44100Hz
Mono


# Steps to Setup Google Cloud 
for details, read the quick guide (https://cloud.google.com/speech-to-text/docs/quickstart-client-libraries)
1. Open cloud.google.com and click on Console
2. Create a new Project and call it 'testProject', or use an existing one
3. Goto Storage, create a bucket and call it 'bilingualaudio'. Or use an existing one
4. Upload the sample file Sample_sp_en.wav to the bucket
5. Goto APIs and Services and Enable the Speech-to-text API 
6. In IAM & Admin, click and goto Service accounts
7. Select your project 'testProject' and create service account by name 'bilingual'
8. Grant role, Project owner 
9. Create key, choose JSON. It should download for e.g. testproject-xxxxxx-xxxxxxxxxx.json

# Steps to setup Google Cloud client on your PC
10. If .json file is in downloads, run the command
export GOOGLE_APPLICATION_CREDENTIALS="~/Downloads/testproject-xxxxxx-xxxxxxxxxx.json"
11. Install cloud for python
pip install --upgrade google-cloud-speech

# Steps to make an audio transcription request for bilingual spanish and english audio
12. Run transcribe.py

