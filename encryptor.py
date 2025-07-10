# encryptor.py
def encrypt_image(image_path, output_path):
    print(f"Encrypting {image_path}...")
    # Dummy encryption logic for illustration
    with open(image_path, 'rb') as f:
        data = f.read()
    encrypted_data = data[::-1]  # Simple reversal for demo
    with open(output_path, 'wb') as f:
        f.write(encrypted_data)
    print(f"Encrypted image saved to {output_path}")