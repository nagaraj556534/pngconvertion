
import io
from os import sendfile

from flask import Flask, request, Response , render_template
from PIL import Image
import img2pdf



app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/jpgtopng", methods=["GET"])
def jpgtopng():
    return render_template("jpgtopng.html")

@app.route("/pngtojpg", methods=["GET"])
def pngtojpg():
    return render_template("pngtojpg.html")

@app.route("/webptopng", methods=["GET"])
def webptopng():
    return render_template("webptopng.html")

@app.route("/bmptopng", methods=["GET"])
def bmptopng():
    return render_template("bmptopng.html")

@app.route("/pngtopdf", methods=["GET"])
def pngtopdf():
    return render_template("pngtopdf.html")


    


@app.route("/api/jpgtopng", methods=["POST"])
def jpg_to_png():
    # Get the image file from the POST request
    image = request.files.get("image")

    # Check if the image file was provided
    if not image:
        return Response("No image file provided", 400)

    # Check if the image is a JPEG
    if image.filename.split(".")[-1].lower() != "jpg":
        return Response("Image must be a JPEG", 400)

    # Check if the image is less than 5 MB
    if image.content_length > 5 * 1024 * 1024:
        return Response("Image must be less than 5 MB", 400)

    # Open the image and convert it to PNG
    img = Image.open(image)
    img = img.convert("RGB")
    img.save("converted.png", "PNG")

    # Create a response object with the converted image as an attachment
    response = Response(open("converted.png", "rb").read())
    response.headers.set("Content-Disposition", "attachment", filename="converted.png")
    response.headers.set("Content-Type", "image/png")

    return response 

@app.route('/api/pngtojpg', methods=['POST'])
def png_to_jpg():
    # Get image from parameters
    image = request.files.get('image')
    if not image:
        return 'Please select an image', 400
    if image.filename.split('.')[-1].lower() != 'png':
        return 'Invalid format, only PNG images are allowed', 400
    if image.content_length > 5 * 1024 * 1024:
        return 'File size exceeds 5 MB', 400
    
    # Convert PNG to JPG
    image = Image.open(image)
    image = image.convert('RGB')
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='JPEG')
    image_bytes.seek(0)
    
    # Create response with JPG image as attachment
    response = Response(image_bytes.read())
    response.headers.set('Content-Type', 'image/jpeg')
    response.headers.set(
        'Content-Disposition',
        'attachment',
        filename='converted_image.jpg'
    )
    return response

@app.route('/api/webptopng', methods=['POST'])
def webp_to_png():
    image = request.files.get('image').read()
    with io.BytesIO(image) as image_binary:
        image = Image.open(image_binary)
        image = image.convert('RGBA')
        image_binary = io.BytesIO()
        image.save(image_binary, 'PNG')
        image_binary.seek(0)

        response = Response(image_binary.read())
        response.headers.set('Content-Disposition', 'attachment', filename='converted.png')
        response.headers.set('Content-Type', 'image/png')
        return response


@app.route('/api/bmptopng', methods=['POST'])
def bmp_to_png():
    if 'image' in request.files:
        image = request.files['image']
        if image.filename.endswith('.bmp'):
            if image.content_length <= 5 * 1024 * 1024:
                image = Image.open(io.BytesIO(image.read()))
                output = io.BytesIO()
                image = image.convert('RGBA')
                image.save(output, format='PNG')
                output.seek(0)
                return sendfile(output, as_attachment=True, attachment_filename='converted.png', mimetype='image/png')
            else:
                return 'Error: Image size exceeds 5 MB'
        else:
            return 'Error: Not a BMP image'
    else:
        return 'Error: No image selected'




@app.route("/api/pngtopdf", methods=["POST"])
def png_to_pdf():
    # Check if image is present in the request
    if "image" not in request.files:
        return "No image found in the request", 400

    # Get the image file from the request
    image = request.files["image"]

    # Check if the image is a PNG file
    if not image.filename.endswith(".png"):
        return "The image is not a PNG file", 400

    # Check if the image is less than 5 MB
    if image.content_length > 5 * 1024 * 1024:
        return "The image is larger than 5 MB", 400

    # Convert the PNG image to PDF
    pdf_bytes = img2pdf.convert(io.BytesIO(image.read()).read())

    # Return the PDF as a downloadable attachment
    response = Response(pdf_bytes)
    response.headers["Content-Disposition"] = "attachment; filename=image.pdf"
    response.mimetype = "application/pdf"
    return response



if __name__ == "__main__":
    app.run(debug=True)
