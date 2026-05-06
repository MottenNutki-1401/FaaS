from PIL import Image
import io

def handler(image_bytes, width=100, height=100):
    """
    Resizes an image to the specified width and height.
    :param image_bytes: The image data in bytes.
    :param width: Target width.
    :param height: Target height.
    :return: Resized image bytes.
    """
    image = Image.open(io.BytesIO(image_bytes))
    resized_image = image.resize((int(width), int(height)))
    
    output = io.BytesIO()
    resized_image.save(output, format=image.format if image.format else 'JPEG')
    return output.getvalue()
