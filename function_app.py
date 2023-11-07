import azure.functions as func
import logging
from generator import picture_gene, script_gene
from data import *

app = func.FunctionApp(http_auth_level=func.AuthLevel.ADMIN)

@app.route(route="post_script", methods=["GET"])
def youtube_post_script(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('[Info] Creating a new script')
    try:
        msg = script_gene.jsonify_msg()
        if type(msg) != list:
            raise TypeError
    except TypeError:
        logging.error("[ERROR] Prompt message error")
        
    try:
        script_response = script_gene.generate(msg)
        print(script_response)
        logging.info("[Info] Create new script successfully")
        return func.HttpResponse(
            "Create new script successfully",
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
        gene_body = GenePicBody()
        gene_body.set_size(req_body.get("size", "1024x1024"))
        gene_body.set_prompt(req_body.get("prompt"))
        
    except ValueError:
        logging.error("[ERROR] Need request body")
        
    try:
        pic_link = picture_gene.generate(gene_body.get_prompt(), gene_body.get_size())
        return func.HttpResponse(f"picture link: {pic_link}", status_code=200)
    
    except ValueError:
        logging.error("[ERROR] picture generate error")
        return func.HttpResponse(
            "Picture Generator Error, please check your log",
            status_code=400
        )


@app.route(route="post_new_material")
def youtube_post_new_material(req: func.HttpRequest) -> func.HttpResponse:
    pass


@app.route(route="upload_blob")
def upload_blob(req: func.HttpRequest) -> func.HttpResponse:
    pass