import os
import shutil
import json
import hashlib
import concurrent.futures
from logger import log_action

CONFIG_FILE = 'rules.json'
LOG_FILE = 'organizer.log'

def load_rules():
    if not os.path.exists(CONFIG_FILE):
        print(f'Error: Configuration file {CONFIG_FILE} not found.')
        return None
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def get_file_hash(filepath, hash_algorithm='sha256'):
    hasher = hashlib.new(hash_algorithm)
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def organize_file(filepath, rules, processed_hashes):
    filename = os.path.basename(filepath)
    file_hash = get_file_hash(filepath)

    if file_hash in processed_hashes:
        log_action('duplicate', filepath, f'Deleting duplicate file with hash {file_hash}')
        os.remove(filepath)
        return
    else:
        processed_hashes[file_hash] = filepath

    for rule in rules.get('rules', []):
        if any(filename.lower().endswith(ext.lower()) for ext in rule.get('extensions', [])):
            destination_folder = rule.get('destination', 'Others')
            os.makedirs(destination_folder, exist_ok=True)
            destination_path = os.path.join(destination_folder, filename)
            shutil.move(filepath, destination_path)
            log_action('move', filepath, destination_path)
            return
    
    # If no rule matches, move to 'Others'
    others_folder = 'Others'
    os.makedirs(others_folder, exist_ok=True)
    destination_path = os.path.join(others_folder, filename)
    shutil.move(filepath, destination_path)
    log_action('move', filepath, destination_path)

def main():
    rules = load_rules()
    if not rules:
        return

    base_path = '.' # Current directory
    files_to_organize = [os.path.join(base_path, f) for f in os.listdir(base_path) if os.path.isfile(os.path.join(base_path, f)) and f not in [CONFIG_FILE, 'main.py', LOG_FILE]]
    
    processed_hashes = {} # To store hashes of processed files

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(organize_file, f, rules, processed_hashes) for f in files_to_organize]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as exc:
                print(f'File generated an exception: {exc}')

if __name__ == '__main__':
    main()
