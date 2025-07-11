import cv2
import numpy as np
import os
import json
import sys

def inverse_shuffle(channel, shuffle_key):
    inverse = np.zeros_like(shuffle_key)
    for i, val in enumerate(shuffle_key):
        inverse[val] = i
    flat = channel.flatten()
    unshuffled = flat[inverse]
    return unshuffled.reshape(channel.shape)

def reverse_qice_modulation(channel, quantum_key):
    demodulated = (channel.astype(np.int16) - quantum_key[:channel.size].reshape(channel.shape)) % 256
    return demodulated.astype(np.uint8)

def save_image(path, image, ext):
    if ext == '.jpg' or ext == '.jpeg':
        cv2.imwrite(path, image, [cv2.IMWRITE_JPEG_QUALITY, 100])
    elif ext == '.png':
        cv2.imwrite(path, image, [cv2.IMWRITE_PNG_COMPRESSION, 1])
    else:
        cv2.imwrite(path, image)  # BMP or default

def decrypt_image(enc_path, key_path, output_path, ext):
    with open(key_path, 'r') as f:
        key_data = json.load(f)

    shuffle_key = key_data['shuffle_key']
    quantum_key = np.array(key_data['quantum_key'], dtype=np.uint8)
    is_gray = key_data['is_gray']
    shape = tuple(key_data['shape'])

    img = cv2.imread(enc_path)

    if is_gray:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        demodulated = reverse_qice_modulation(gray, quantum_key)
        unshuffled = inverse_shuffle(demodulated, shuffle_key)
        recovered = cv2.cvtColor(unshuffled, cv2.COLOR_GRAY2BGR)
        save_image(output_path, recovered, ext)
    else:
        b, g, r = cv2.split(img)
        decrypted_channels = []

        for ch in [b, g, r]:
            demodulated = reverse_qice_modulation(ch, quantum_key)
            unshuffled = inverse_shuffle(demodulated, shuffle_key)
            decrypted_channels.append(unshuffled)

        decrypted_img = cv2.merge(decrypted_channels)
        save_image(output_path, decrypted_img, ext)

if __name__ == "__main__":
    enc_path = sys.argv[1]
    key_path = sys.argv[2]
    with open(key_path, 'r') as f:
        key_data = json.load(f)
    name = os.path.splitext(os.path.basename(enc_path))[0].replace("encrypted_", "")
    ext = key_data.get("ext", ".png")
    os.makedirs("decrypted", exist_ok=True)
    output_path = f"decrypted/decrypted_{name}{ext}"
    decrypt_image(enc_path, key_path, output_path, ext)
