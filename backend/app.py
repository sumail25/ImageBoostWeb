from flask import Flask, render_template, request, send_file
import os
import base64
from flask_cors import CORS
from PIL import Image
import subprocess

app = Flask(__name__, template_folder='../frontend')
CORS(app)

# call image_boost
def img_process(image_name, model_type, upscale_factor, face_enhance):
    if model_type == 'general':
        model = 'RealESRGAN_x4plus'
    else:
        model = 'RealESRGAN_x4plus_anime_6B'
    
    if face_enhance == True:
        is_face = '--face_enhance'
    else:
        is_face = ''

    # print(f"python backend/imageboostmodel/image_boost.py -n {model} -i backend//uploaded_images/{image_name} -o backend//processed_images -s {upscale_factor} -t 100 {is_face}")
    command = f"python backend/imageboostmodel/image_boost.py -n {model} -i backend/uploaded_images/{image_name} -o backend//processed_images -s {upscale_factor} -t 100 {is_face}"
    subprocess.run(command, shell=True)



# home
@app.route('/')
def home():
    return render_template('web.html')


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file uploaded'

    file = request.files['file']
    if file.filename == '':
        return 'No file selected'

    # upload image
    current_directory = os.path.dirname(os.path.abspath(__file__))
    upload_folder = os.path.join(current_directory, 'uploaded_images')
    
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    # PermissionError --> TODO
    # else:
    #    os.remove(upload_folder)

    file.save(os.path.join(upload_folder, file.filename))

    return render_template('web.html')


@app.route('/process', methods=['POST'])
def process():
    image_name = request.form.get('image_name')
    model_type = request.form.get('model_type')
    upscale_factor = int(request.form.get('upscale_factor'))
    face_enhance = request.form.get('face_enhance').lower() == 'true'

    # PermissionError --> TODO
    current_directory = os.path.dirname(os.path.abspath(__file__))
    process_folder = os.path.join(current_directory, 'processed_images')
    if not os.path.exists(process_folder):
        os.makedirs(process_folder)
    # else:
    #    os.remove(process_folder)

    # processing
    img_process(image_name, model_type, upscale_factor, face_enhance)

    file_name = os.path.splitext(image_name)[0]
    extension = os.path.splitext(image_name)[1]
    processed_image_path = os.path.join(process_folder, file_name + '_out' + extension)
    #processed_image.save(processed_image_path)

    encoded_filename = base64.b64encode(processed_image_path.encode('utf-8')).decode('utf-8')

    return encoded_filename


# download
@app.route('/download', methods=['GET'])
def download():
    filename = request.args.get('filename')
    file_path = os.path.join('processed_images', filename)

    return send_file(file_path, as_attachment=True)




if __name__ == '__main__':
    app.run(debug=True)

