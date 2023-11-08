import os
import openai

openai.api_type = "azure"
openai.api_base = "https://youtube-channel-openai.openai.azure.com/"
openai.api_version = "2023-06-01-preview"
openai.api_key = os.getenv("OPENAI_API_KEY")


def generate(prompt: str, size: str, num: int):
    url_list = []
    response = openai.Image.create(
        # prompt='USER_PROMPT_GOES_HERE',
        prompt=str(prompt),
        size=size,
        n=num
    )

    # image_url = response["data"][0]["url"]
    for i in range(len(response["data"])):
        url_list.append(response["data"][i]["url"])
    return url_list

def upload_pic():
    pass
