from flask import Flask, request, jsonify, render_template
import os
import subprocess
import uuid

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encrypt', methods=['POST'])
def encrypt():
    if 'image' not in request.files:
        return jsonify({'message': 'No image uploaded'})

    image = request.files['image']
    filename = image.filename
    name, ext = os.path.splitext(filename)
    ext = ext.lower()

    os.makedirs('input', exist_ok=True)
    os.makedirs('output', exist_ok=True)

    input_path = os.path.join('input', filename)
    image.save(input_path)

    subprocess.run(['python', 'encryptor.py', input_path])

    if ext in ['.jpg', '.jpeg']:
        return jsonify({'message': f'📸 JPG was converted to PNG to avoid quality loss. Encrypted as encrypted_{name}.png'})
    else:
        return jsonify({'message': f'Encrypted image and key saved as encrypted_{name}{ext} and key_{name}.json'})

@app.route('/decrypt', methods=['POST'])
def decrypt():
    if 'image' not in request.files or 'key' not in request.files:
        return jsonify({'message': 'Encrypted image and key (.json) are required'})

    image = request.files['image']
    key = request.files['key']
    img_name = image.filename
    key_name = key.filename

    enc_path = os.path.join('output', img_name)
    key_path = os.path.join('output', key_name)

    os.makedirs('output', exist_ok=True)
    os.makedirs('decrypted', exist_ok=True)

    image.save(enc_path)
    key.save(key_path)

    subprocess.run(['python', 'decryptor.py', enc_path, key_path])

    # auto-verify PSNR after decrypt
    original_name = img_name.replace("encrypted_", "")
    original_path = os.path.join('input', original_name)
    decrypted_path = os.path.join('decrypted', 'decrypted_' + original_name)

    result = subprocess.run(
        ['python', 'verify.py', original_path, decrypted_path],
        capture_output=True,
        text=True
    )
    psnr_output = result.stdout.strip()

    return jsonify({'message': f'Decrypted image saved.\n{psnr_output}'})

if __name__ == '__main__':
    app.run(debug=True)
