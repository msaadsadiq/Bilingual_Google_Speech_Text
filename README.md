# Converting bilingual speech audio files to text using Google's Cloud Speech-to-Text API
# Bi-lingual Text Transcription - English and Spanish mixed

This repo contains a python based approach, to trascribe bilingual speech. Currently there is no single method to transcribe bilingual speech. Thus, we transcribe separately and combine them together to create a single text file. All steps to setup the cloud environment are provided below. This approach converts long audio files that are > 1min but < 1hour. 


# Steps
1. 
1. Run the command 
export GOOGLE_APPLICATION_CREDENTIALS="/Users/saad/Google\ Drive/Psychology/Transcription/Psychology-d3be7cd87026.json"

2. Install cloud for python
pip install --upgrade google-cloud-speech

3. Upload files on bucket psychology audio

4. Run  transcribe.py

