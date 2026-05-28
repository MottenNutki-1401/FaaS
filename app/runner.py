import subprocess # allow py exec in termial, use to run docker subprocess
import uuid # generate randomid, prevent container conflicts
import os #file paths


#function for exec
#uploads user functuiob inside docker container
def run_function(filepath):

    container_name = f"faas-{uuid.uuid4().hex[:8]}" # takes only 8 chars


    #command build (docker as python list)
    command = [

        "docker", #docker executable

        "run", #run a new container

        "--rm", #delete container after execution

        "--name",
        container_name,


        #mount uploaded function in container
        "-v",
        f"{os.path.abspath(filepath)}:/app/function.py",


        #mount persistent storage
        "-v",
        "C:/Users/Gail/Desktop/Outputs:/app/outputs",


        #create isolated python environmnet
        "dokifass-runtime",


        #run uploaded python function
        "sh",

        "-c",

        "python /app/function.py && sleep 5"

    ]


    #execute docker command
    result = subprocess.run(

        command,

        capture_output=True,

        text=True
    )


    #return execution results
    return {

        "stdout": result.stdout, #normal program output

        "stderr": result.stderr, #error output

        "returncode": result.returncode # status code

    }