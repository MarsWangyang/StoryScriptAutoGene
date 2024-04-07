#Note: The openai-python library support for Azure OpenAI is in preview.
import os, json, logging
import openai
from datetime import datetime
from azure.identity import ManagedIdentityCredential, DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
import tempfile

openai.api_type = "azure"
openai.api_base = "https://youtube-channel-openai.openai.azure.com/"
openai.api_version = "2023-07-01-preview"
openai.api_key = os.getenv("OPENAI_API_KEY")
MSG_FILE_NAME = os.getenv("MSG_FILE_NAME")
SG_ACC_NAME = os.getenv("SG_ACC_NAME")
ENGINE_NAME = os.getenv("ENGINE_NAME")
cache_path = tempfile.gettempdir()
# cache_path = "/Users/mars/Desktop/Youtube_story_generator/templates"
cache_file_name = "cache_msg.json"
past_msg_num = int(os.getenv("PAST_MSG_NUM"))
prompt_msg_num = int(os.getenv("PROMPT_MSG_NUM"))
cache_file_path = os.path.join(cache_path, cache_file_name)
account_url = f"https://{SG_ACC_NAME}.blob.core.windows.net"



def generate(msg: list):

    response = openai.ChatCompletion.create(
                    engine=ENGINE_NAME,
                    messages = msg,
                    temperature=0.7,
                    max_tokens=500,
                    top_p=0.7,
                    frequency_penalty=0,
                    presence_penalty=0
                )
    if update_msg(response['choices'][0]['message']):
        content = response['choices'][0]['message']['content']
        return content
    else:
        return logging.error("[Error] Fail to Generate Script.")

# update message in templates for writer bot
def update_msg(new_response):
    credential = DefaultAzureCredential()
    blob_service_client = BlobServiceClient(account_url, credential=credential)
    container_client = blob_service_client.get_container_client(container="templates")
    original_msg_num = 0
        
    with open(cache_file_path, "rb") as cache_file:
        cache_msg_json = json.load(cache_file)
        cache_msg_json.append(json.loads(str(new_response)))
        original_msg_num = len(cache_msg_json)
    # delete the earliest response
    if original_msg_num > past_msg_num + prompt_msg_num:
        cache_msg_json.pop(3)
    with open(cache_file_path, "w") as cache_file:
        cache_file.write(json.dumps(cache_msg_json))
        original_msg_num += 1
        
    
    try:
        with open(cache_file_path, "rb") as data:
            container_client.upload_blob(name=f"{cache_file_name}", data=data, overwrite=True)
            logging.info("[Info] Upload updated message file into Blob Storage successfully")
            return True
    except RuntimeError:
        logging.error("[Error] Fail to upload updated message file")
        return False
    
    

# download messages from blob
def download_msg():
    try:
        credential = DefaultAzureCredential()
        blob_service_client = BlobServiceClient(account_url, credential=credential)
        container_client = blob_service_client.get_container_client(container="templates")
        logging.info(f"[Info] Connect to blob storage {SG_ACC_NAME} successfully") 
    except RuntimeError:
        logging.error(f"[Error] Fail to connect to blob storage {SG_ACC_NAME}")
        return False
    
    with open(cache_file_path, "wb") as download_file:
        logging.info(f"[Info] Downloading template message for bot-writer")    
        download_file.write(container_client.download_blob(MSG_FILE_NAME).readall())
        logging.info(f"[Info] Download template message for bot-writer successfully")    
        return True

def jsonify_msg():
    
    with open(cache_file_path, "rb") as file:
        cache_json = json.loads(file.read())
    return cache_json

def upload_script():
    pass

