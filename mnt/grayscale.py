from PIL import Image
import io

def handler(image_bytes):
    """
    Converts an image to grayscale.
    :param image_bytes: The image data in bytes.
    :return: Grayscale image bytes.
    """
    image = Image.open(io.BytesIO(image_bytes))
    grayscale_image = image.convert('L')
    
    output = io.BytesIO()
    grayscale_image.save(output, format=image.format if image.format else 'JPEG')
    return output.getvalue()
