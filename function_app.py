import azure.functions as func
import logging, json
from generator import picture_gene, script_gene, speech_gene
from data import *


app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="post_script", methods=["POST"])
def youtube_post_script(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('[Info] Creating a new script')

    try:
        if script_gene.download_msg():
            msg = script_gene.jsonify_msg()
        else:
            raise RuntimeError
        if type(msg) != list:
            raise TypeError
    except TypeError:
        logging.error("[ERROR] Prompt message error")
        return func.HttpResponse(status_code=400)
        
    try:
        script_response = script_gene.generate(msg)        
        logging.info("[Info] Create new script successfully")
        print(script_response)
        format_res = script_response.replace("\n", " ")
        print("="*30)
        print(format_res)
        res = {
            "status": 200,
            "content": json.loads(format_res)
        }

        return func.HttpResponse(
            json.dumps(res, indent=None),
            mimetype="application/json",
            status_code=200
        )
    except RuntimeError:
        logging.info("[Error] Script generator error, pls check")
        return func.HttpResponse(f"Script generator error, pls check", status_code=400)

    
@app.route(route="post_pic", methods=["POST"])
def youtube_post_pic(req: func.HttpRequest) -> func.HttpResponse:
    
    logging.info('[Info] Creating a new photo')
    try:
        req_body = req.get_json()
        if req_body.get('prompt'):        
            gene_body = GenePicBody()
            gene_body.set_size(req_body.get("size", "1024x1024"))
            gene_body.set_prompt(req_body.get("prompt"))
            gene_body.set_num(req_body.get("num", 1))
        else:
            raise ValueError
    except ValueError:
        logging.error("[ERROR] Need request body")
        return func.HttpResponse(status_code=400)
        
    try:
        pic_link = picture_gene.generate(gene_body.get_prompt(), gene_body.get_size(), gene_body.get_num())
        pic_link = str(pic_link).replace("'", "\"")
        res = {
            "link": json.loads(pic_link)
        }
        return func.HttpResponse(
            json.dumps(res, indent=None),
            mimetype="application/json",
            status_code=200)
    
    except ValueError:
        logging.error("[ERROR] picture generate error")
        return func.HttpResponse(
            "Picture Generator Error, please check your log",
            status_code=400
        )



@app.route(route="text_to_speech", methods=["POST"])
def text_to_speech(req: func.HttpRequest) -> func.HttpResponse:
    req_body = req.get_json()
    
    if req_body.get("content"):
        time: int = req_body.get("content").get("Time")
        story_title = req_body.get("content").get("Title")
        story_context = req_body.get("content").get("Story")
        story = story_title + ".    " + story_context
        file_name = f"{str(time)}_{story_title}"
        speech_gene.generate(story, file_name)
        return func.HttpResponse(f"Text to Speech Success", status_code=200)
    else:
        logging.error("[Error] Text to Speech went mistakes, please check your content.")
        return func.HttpResponse(status_code=400)