# decryptor.py
def decrypt_image(encrypted_path, output_path):
    print(f"Decrypting {encrypted_path}...")
    # Dummy decryption logic for illustration
    with open(encrypted_path, 'rb') as f:
        data = f.read()
    decrypted_data = data[::-1]  # Simple reversal for demo
    with open(output_path, 'wb') as f:
        f.write(decrypted_data)
    print(f"Decrypted image saved to {output_path}")