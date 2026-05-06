import os
import importlib.util
import sys

def main():
    function_name = os.environ.get("FUNCTION_NAME")
    input_file = os.environ.get("INPUT_FILE")
    output_file = os.environ.get("OUTPUT_FILE")
    width = os.environ.get("WIDTH", "100")
    height = os.environ.get("HEIGHT", "100")

    if not all([function_name, input_file, output_file]):
        print("Missing required environment variables")
        sys.exit(1)

    try:
        # Debug: list files in /mnt
        print(f"Files in /mnt: {os.listdir('/mnt')}")
        
        # Load the function from the mounted /mnt directory
        function_path = f"/mnt/{function_name}.py"
        if not os.path.exists(function_path):
            print(f"Error: Function file {function_path} not found.")
            sys.exit(1)

        spec = importlib.util.spec_from_file_location(function_name, function_path)
        if spec is None:
            print(f"Error: Could not load spec for {function_name}")
            sys.exit(1)
            
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if not hasattr(module, 'handler'):
            print(f"Error: Function {function_name} has no 'handler' attribute")
            sys.exit(1)
            
        handler = getattr(module, 'handler')

        # Read input image
        if not os.path.exists(input_file):
            print(f"Error: Input file {input_file} not found.")
            sys.exit(1)
            
        with open(input_file, 'rb') as f:
            image_bytes = f.read()

        print(f"Executing {function_name} with {len(image_bytes)} bytes of input")
        # Execute handler
        if function_name == 'resize':
            result_bytes = handler(image_bytes, width=width, height=height)
        else:
            result_bytes = handler(image_bytes)

        if result_bytes is None:
            print(f"Error: Handler returned None")
            sys.exit(1)

        # Write output image
        with open(output_file, 'wb') as f:
            f.write(result_bytes)

        print(f"Successfully processed {function_name}, wrote {len(result_bytes)} bytes")
    except Exception as e:
        import traceback
        print(f"Exception during execution:\n{traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
