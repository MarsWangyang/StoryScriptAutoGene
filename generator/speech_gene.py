import os, logging
from io import BytesIO
import azure.cognitiveservices.speech as speechsdk
from azure.identity import ManagedIdentityCredential, DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContentSettings
import tempfile
from scipy.io import wavfile

SG_ACC_NAME = os.getenv("SG_ACC_NAME")
SPEECH_KEY = os.getenv("SPEECH_KEY")
SPEECH_REGION = os.getenv("SPEECH_REGION")
account_url = f"https://{SG_ACC_NAME}.blob.core.windows.net"

def clear_unreadable(text: str):
    return text.replace("\n", " ")

def get_ssml_text(text: str):
    ssml_format_begin = """<speak xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xmlns:emo="http://www.w3.org/2009/10/emotionml" version="1.0" xml:lang="en-US"><voice name="en-US-SaraNeural"><s /><mstts:express-as style="whispering"><prosody rate="-20.00%">"""
    ssml_format_end = """</prosody></mstts:express-as><s /></voice></speak>"""
    return ssml_format_begin + clear_unreadable(text) + ssml_format_end
    
def upload(sampling_rate, audio_data, file_name):
    try:
        # credential = ManagedIdentityCredential()
        credential = DefaultAzureCredential()
        my_content_settings = ContentSettings(content_type='audio/x-wav')
        blob_service_client = BlobServiceClient(account_url, credential=credential)
        blob_client = blob_service_client.get_blob_client(container="voice", blob=f"{file_name}.wav")
        blob_client_materials_folder = blob_service_client.get_blob_client(container="materials", blob=f"{file_name}.wav")
        logging.info(f"[Info] Connect to blob storage {SG_ACC_NAME} successfully") 
        
        bytes_wav = bytes()
        byte_io = BytesIO(bytes_wav)
        wavfile.write(byte_io, sampling_rate, audio_data)
        output_wav = byte_io.read()
        
        blob_client.upload_blob(output_wav, content_settings=my_content_settings)
        blob_client_materials_folder.upload_blob(output_wav, content_settings=my_content_settings)
        
        return True
    except RuntimeError:
        logging.error(f"[Error] Fail to connect to blob storage {SG_ACC_NAME}")
        return False


def generate(text, file_name):
    
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    

    # The language of the voice that speaks.
    speech_config.speech_synthesis_voice_name='en-US-SaraNeural'

    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

    ssml_string = get_ssml_text(text)

    result = speech_synthesizer.speak_ssml_async(ssml_string).get()

    stream = speechsdk.AudioDataStream(result)
    
    
    cache_audio_path = tempfile.gettempdir()
    print(cache_audio_path)
    cache_audio_filename = "tmp_audio.wav"
    cache_audio_file_path = os.path.join(cache_audio_path, cache_audio_filename)
    # store in local
    stream.save_to_wav_file(cache_audio_file_path)

    sampling_rate, audio_data = wavfile.read(cache_audio_file_path)
    
    logging.info("[Info] =======UPLOADING....========")
    try:
        upload(sampling_rate, audio_data, file_name)
        logging.info(f"[Info] Uploading Speech {file_name}.wav into {SG_ACC_NAME}/voice")
    except RuntimeError: 
        logging.error(f"[Error] Fail to uploading {file_name}.wav")
    
    # delete after uploading to blob storage
    try:
        os.remove(cache_audio_file_path)
        logging.info(f"[Info] Delet local {file_name}.wav")    
    except OSError:
        logging.error(f"[Error] Fail to delete .wav file")
    # Check result
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text [{}]".format(text))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))

                
