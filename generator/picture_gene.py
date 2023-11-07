import os
import openai

openai.api_type = "azure"
openai.api_base = "https://youtube-channel-openai.openai.azure.com/"
openai.api_version = "2023-06-01-preview"
openai.api_key = os.getenv("OPENAI_API_KEY")


def generate(prompt: str, size: str):
    response = openai.Image.create(
        # prompt='USER_PROMPT_GOES_HERE',
        prompt=str(prompt),
        size=size,
        n=1
    )

    image_url = response["data"][0]["url"]
    print(image_url)
    return response

def upload_pic():
    pass
