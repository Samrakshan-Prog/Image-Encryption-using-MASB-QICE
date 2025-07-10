# app.py
from flask import Flask, request, jsonify
import os
from encryptor import encrypt_image
from decryptor import decrypt_image

app = Flask(__name__)

@app.route('/encrypt', methods=['POST'])
def encrypt():
    image = request.files['image']
    image_path = 'uploaded_image.png'
    encrypted_path = 'encrypted_image.png'
    image.save(image_path)
    encrypt_image(image_path, encrypted_path)
    return jsonify({'message': 'Image encrypted successfully!'})

@app.route('/decrypt', methods=['POST'])
def decrypt():
    image = request.files['image']
    encrypted_path = 'uploaded_encrypted_image.png'
    decrypted_path = 'decrypted_image.png'
    image.save(encrypted_path)
    decrypt_image(encrypted_path, decrypted_path)
    return jsonify({'message': 'Image decrypted successfully!'})

if __name__ == '__main__':
    app.run(debug=True)