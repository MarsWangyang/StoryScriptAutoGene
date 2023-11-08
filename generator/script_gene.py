#Note: The openai-python library support for Azure OpenAI is in preview.
import os, json, logging
import openai
from datetime import datetime
from azure.identity import ManagedIdentityCredential
from azure.storage.blob import BlobServiceClient

openai.api_type = "azure"
openai.api_base = "https://youtube-channel-openai.openai.azure.com/"
openai.api_version = "2023-07-01-preview"
openai.api_key = os.getenv("OPENAI_API_KEY")
MSG_FILE_NAME = os.getenv("MSG_FILE_NAME")
SG_ACC_NAME = os.getenv("SG_ACC_NAME")
ENGINE_NAME = os.getenv("ENGINE_NAME")
cache_path = os.path.join(os.getcwd(), "cache")
cache_file_name = MSG_FILE_NAME
cache_file_path = os.path.join(cache_path, cache_file_name)


def generate(msg: list):

    response = openai.ChatCompletion.create(
                    engine=ENGINE_NAME,
                    messages = msg,
                    temperature=0.5,
                    max_tokens=800,
                    top_p=0.95,
                    frequency_penalty=0,
                    presence_penalty=0,
                    stop=None
                )
    return response['choices'][0]['message']['content']
 
# download messages from blob
def download_msg():
    account_url = f"https://{SG_ACC_NAME}.blob.core.windows.net"
    try:

        credential = ManagedIdentityCredential()
        blob_service_client = BlobServiceClient(account_url, credential=credential)
        container_client = blob_service_client.get_container_client(container="templates")
        logging.info(f"[Info] Connect to blob storage {SG_ACC_NAME} successfully") 
    except RuntimeError:
        logging.error(f"[Error] Fail to connect to blob storage {SG_ACC_NAME}")
        return False
    
    with open(cache_file_path, "wb") as download_file:
        download_file.write(container_client.download_blob(MSG_FILE_NAME).readall())
        logging.info(f"[Info] Download template message for bot-writer successfully")    
        return True

def jsonify_msg():
    
    with open(cache_file_path, "rb") as file:
        cache_json = json.loads(file.read())
    return cache_json

def upload_script():
    pass

