from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse #allow html response
from fastapi.templating import Jinja2Templates #allow renderhtml

import shutil #copy uploaded files
import os
#import engine (runner.py)
from app.runner import run_function

#created Fastapi instance
app = FastAPI

#locate templates
templates = Jinja2Templates (
    directory = "templates"
)

#this wjhere uploaded functions be stored
FUNCTIONS_DIR = "functions"

#if this folder doesnt exost yet we will create one
os.makedirs(
    FUNCTIONS_DIR,
    exist_ok=True
)

    #homeoute/ diplay dashboard
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    #get all uploaded funct/files
    files = os.listdir (FUNCTIONS_DIR)



    return templates.TemplatesResponse (
        #html file to render
        "index.html",

        #data sent to template
        {
            "request": request,
            "files": files # data sent to template
        }
        
    )
#deploy function route
@app.post ("/deploy")
async def deploy_function (
    file: UploadFile = File(...) #receive uploaded file
):
    #build full file path
    filepath = os.path.jpin(
        FUNCTIONS_DIR,
        file.filename
    )
    #save uploaded files to disk| wb => write binary mode
    with open (filepath, "wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer

        )

    #return deployment response
    return {
        "message": "functions have been deployed",
        "filename": file.filename
    }
#execute function route(trigger upload function)

@app.get("/execute/{filename}")
async def execute_function(filename:str):

    #build file path
    filepath = os.path.join(
        FUNCTIONS_DIR,
        filename
    )
    #prevent executing missing functions
    if not os.path.exists(filepath):
        return {
            "error": "Aww Snap! Function isn't found"
        }
    #run uploaded function....
    #trigger doc container/funct .exec/container deletion kaboom
    result = run_function (filepath)

    #return .exec output logs
    return result