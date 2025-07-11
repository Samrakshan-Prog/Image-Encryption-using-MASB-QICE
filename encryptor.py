import cv2
import numpy as np
import os
import json
import sys

def generate_shuffle_key(size, seed):
    np.random.seed(seed)
    return np.random.permutation(size).tolist()

def apply_masb_shuffle(channel, shuffle_key):
    flat = channel.flatten()
    shuffled = flat[shuffle_key]
    return shuffled.reshape(channel.shape)

def apply_qice_modulation(channel, quantum_key):
    modulated = (channel + quantum_key[:channel.size].reshape(channel.shape)) % 256
    return modulated.astype(np.uint8)

def generate_qice_key(shape, seed):
    np.random.seed(seed)
    return np.random.randint(0, 256, size=shape[0] * shape[1])

def save_image(path, image, ext):
    if ext == '.jpg' or ext == '.jpeg':
        cv2.imwrite(path, image, [cv2.IMWRITE_JPEG_QUALITY, 100])
    elif ext == '.png':
        cv2.imwrite(path, image, [cv2.IMWRITE_PNG_COMPRESSION, 1])
    else:
        cv2.imwrite(path, image)  # BMP or default

def process_image(image_path, encrypted_output_path, key_path, is_gray=False):
    img = cv2.imread(image_path)
    name, ext = os.path.splitext(os.path.basename(image_path))
    ext = ext.lower()

    if is_gray:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        shape = gray.shape
        seed = int(np.sum(gray.flatten(), dtype=np.uint64)) % 1000
        shuffle_key = generate_shuffle_key(gray.size, seed)
        shuffled = apply_masb_shuffle(gray, shuffle_key)
        quantum_key = generate_qice_key(shape, seed + 123)
        encrypted = apply_qice_modulation(shuffled, quantum_key)
        encrypted_bgr = cv2.cvtColor(encrypted, cv2.COLOR_GRAY2BGR)
        save_image(encrypted_output_path, encrypted_bgr, ext)
    else:
        b, g, r = cv2.split(img)
        shape = b.shape
        seed = int(np.sum(img.flatten(), dtype=np.uint64)) % 1000
        shuffle_key = generate_shuffle_key(b.size, seed)
        quantum_key = generate_qice_key(shape, seed + 123)

        encrypted_channels = []
        for ch in [b, g, r]:
            shuffled = apply_masb_shuffle(ch, shuffle_key)
            encrypted = apply_qice_modulation(shuffled, quantum_key)
            encrypted_channels.append(encrypted)

        encrypted_img = cv2.merge(encrypted_channels)
        save_image(encrypted_output_path, encrypted_img, ext)

    key_data = {
        "shuffle_key": shuffle_key,
        "quantum_key": quantum_key.tolist(),
        "is_gray": is_gray,
        "shape": img.shape,
        "ext": ext
    }

    with open(key_path, 'w') as f:
        json.dump(key_data, f)

if __name__ == "__main__":
    image_path = sys.argv[1]
    name, ext = os.path.splitext(os.path.basename(image_path))
    ext = ext.lower()
    output_path = f"output/encrypted_{name}{ext}"
    key_path = f"output/key_{name}.json"
    os.makedirs("output", exist_ok=True)

    process_image(image_path, output_path, key_path, is_gray=name.lower().startswith("gray_"))
