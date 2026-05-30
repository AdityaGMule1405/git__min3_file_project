import os
import shutil
import json
import hashlib
import concurrent.futures
from logger import log_action

def get_file_hash(filepath, block_size=65536):
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            sha256.update(block)
    return sha256.hexdigest()

def load_rules():
    try:
        with open('rules.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        log_action('ERROR', 'rules.json not found.')
        return {}

def organize_file(filepath, rules, processed_hashes):
    try:
        filename = os.path.basename(filepath)
        file_extension = os.path.splitext(filename)[1].lower()
        file_hash = get_file_hash(filepath)

        if file_hash in processed_hashes:
            os.remove(filepath)
            log_action('DELETED', f'{filename} (Duplicate of {processed_hashes[file_hash]}).')
            return

        processed_hashes[file_hash] = filename
        
        moved = False
        for rule in rules.get('rules', []):
            if file_extension in rule.get('extensions', []):
                destination_folder = os.path.join(os.path.dirname(filepath), rule['destination'])
                os.makedirs(destination_folder, exist_ok=True)
                shutil.move(filepath, os.path.join(destination_folder, filename))
                log_action('MOVED', f'{filename} to {rule['destination']}.')
                moved = True
                break
        
        if not moved:
            destination_folder = os.path.join(os.path.dirname(filepath), rules.get('default_destination', 'Others'))
            os.makedirs(destination_folder, exist_ok=True)
            shutil.move(filepath, os.path.join(destination_folder, filename))
            log_action('MOVED', f'{filename} to {rules.get('default_destination', 'Others')} (Default).')

    except Exception as exc:
        log_action('ERROR', f'Failed to process {filepath}: {exc}')

def main():
    rules = load_rules()
    if not rules:
        return

    base_dir = '.'
    files_to_organize = [os.path.join(base_dir, f) for f in os.listdir(base_dir) if os.path.isfile(os.path.join(base_dir, f)) and f != 'main.py' and f != 'rules.json' and f != 'logger.py']
    
    processed_hashes = {}

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(organize_file, filepath, rules, processed_hashes) for filepath in files_to_organize}
        for future in concurrent.futures.as_completed(futures):
            pass # Results are handled by logging within organize_file

if __name__ == '__main__':
    main()
