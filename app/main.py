# main.py

from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import shutil
import os
import subprocess

from app.runner import run_function


#created Fastapi instance
app = FastAPI()


#static css folder
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


#locate templates
templates = Jinja2Templates(
    directory="templates"
)


#execution logs for dashboard
execution_logs = []


#track currently running functions
running_functions = []


#track runtime/container events
container_events = []


#this where uploaded functions be stored
FUNCTIONS_DIR = "functions"


#if this folder doesnt exist yet we will create one
os.makedirs(
    FUNCTIONS_DIR,
    exist_ok=True
)


#get active docker containers
def get_running_containers():

    result = subprocess.run(

        ["docker", "ps"],

        capture_output=True,

        text=True
    )

    return result.stdout


#home route/display dashboard
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(

        request,

        "index.html",

        {
            "request": request
        }

    )


#deploy function route
@app.post("/deploy")
async def deploy_function(

    file: UploadFile = File(...)
):

    filepath = os.path.join(
        FUNCTIONS_DIR,
        file.filename
    )

    with open(filepath, "wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    return {

        "message": "Function deployed",

        "filename": file.filename
    }


#execute uploaded function
@app.get("/execute/{filename}")
async def execute_function(filename: str):

    filepath = os.path.join(
        FUNCTIONS_DIR,
        filename
    )

    #prevent missing functions
    if not os.path.exists(filepath):

        return {
            "error": "Function not found"
        }


    #track running state
    running_functions.append(
        filename
    )


    #fake runtime/container name
    container_name = f"faas-{filename}"


    #track runtime event
    container_events.append({

        "container": container_name,

        "runtime": "python:3.11",

        "status": "RUNNING"

    })


    #run function inside docker
    result = run_function(filepath)


    #save execution logs
    execution_logs.append({

        "function": filename,

        "stdout": result["stdout"],

        "stderr": result["stderr"],

        "returncode": result["returncode"]

    })
    
    #delete uploaded function after execution
    os.remove(filepath)


    #track destroyed state
    container_events.append({

        "container": container_name,

        "runtime": "python:3.11",

        "status": "DESTROYED"

    })


    #remove running state
    if filename in running_functions:

        running_functions.remove(
            filename
        )


    return result


#live dashboard status route
@app.get("/status")
async def status():

    #get uploaded functions
    files = os.listdir(
        FUNCTIONS_DIR
    )

    #get active containers
    containers = get_running_containers()

    return {

        "files": files,

        "logs": execution_logs,

        "containers": containers,

        "running": running_functions,

        "events": container_events

    }