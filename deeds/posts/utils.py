import os
import secrets
from PIL import Image
from flask import url_for, current_app

def save_post_image(form_image):
    # Generate a random filename to avoid conflicts
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_image.filename)
    picture_fn = random_hex + f_ext

    # Path to save the image
    picture_path = os.path.join(current_app.root_path, 'static/post_images', picture_fn)

    # Resize image before saving
    output_size = (400, 400)  # Adjust as needed
    img = Image.open(form_image)
    img.thumbnail(output_size)
    img.save(picture_path)

    return picture_fn
