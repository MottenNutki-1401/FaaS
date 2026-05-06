from flask import Flask, render_template, request, send_file
import docker
import os
import uuid
import io

app = Flask(__name__)
client = docker.from_env()

# Path to the shared mnt directory
MNT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mnt')
if not os.path.exists(MNT_PATH):
    os.makedirs(MNT_PATH)

@app.route('/')
def home():
    return render_template('index.html')

def get_host_mnt_path():
    """
    Determines the host path for the mnt directory.
    This is tricky when running inside a container (Docker-in-Docker).
    """
    # 1. Check if explicitly provided via environment variable
    host_path = os.environ.get('HOST_MNT_PATH')
    if host_path:
        # If it's a named volume, return it as is
        # If it's a relative path, we need to be careful. 
        # But in docker-compose we set it to 'faas_data' which is a volume name.
        return host_path
    
    # 2. Try to detect if we are running in a container and find our own mount for /app/mnt
    try:
        import socket
        # Only attempt this if we're likely in a container
        if os.path.exists('/.dockerenv') or os.environ.get('KUBERNETES_SERVICE_HOST'):
            container_id = socket.gethostname()
            container = client.containers.get(container_id)
            for mount in container.attrs.get('Mounts', []):
                if mount['Destination'] == '/app/mnt':
                    if mount['Type'] == 'volume':
                        return mount['Name']
                    return mount['Source']
    except Exception:
        # Fallback to absolute path if detection fails or not in container
        pass
        
    # 3. Fallback to local absolute path
    return os.path.abspath(MNT_PATH)

@app.route('/run', methods=['POST'])
def run_function():
    if 'image' not in request.files:
        return "No image uploaded", 400
    
    file = request.files['image']
    if file.filename == '':
        return "No image selected", 400

    function_name = request.form.get('function', 'resize')
    width = request.form.get('width', '100')
    height = request.form.get('height', '100')

    # Generate a unique ID for this request
    request_id = str(uuid.uuid4())
    input_filename = f"{request_id}_input"
    output_filename = f"{request_id}_output"
    
    input_path = os.path.join(MNT_PATH, input_filename)
    output_path = os.path.join(MNT_PATH, output_filename)

    try:
        # Save uploaded image to mnt
        file.save(input_path)
        
        # Determine arguments for the runner
        env = {
            "FUNCTION_NAME": function_name,
            "INPUT_FILE": f"/mnt/{input_filename}",
            "OUTPUT_FILE": f"/mnt/{output_filename}",
            "WIDTH": width,
            "HEIGHT": height
        }

        # Run the container
        host_mnt_path = get_host_mnt_path()
        
        try:
            client.containers.run(
                image="faas-runner",
                environment=env,
                volumes={
                    host_mnt_path: {'bind': '/mnt', 'mode': 'rw'}
                },
                remove=True,
                detach=False
            )
        except docker.errors.ContainerError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            return f"Container Error (Exit {e.exit_status}): {error_msg}", 500

        # Read the result
        if not os.path.exists(output_path):
            return "Function failed to produce output", 500
            
        with open(output_path, 'rb') as f:
            result_bytes = f.read()

        return send_file(
            io.BytesIO(result_bytes),
            mimetype='image/jpeg',
            as_attachment=True,
            download_name=f'processed_{file.filename}'
        )
    except Exception as e:
        return f"Error: {str(e)}", 500
    finally:
        # Cleanup temporary files
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
