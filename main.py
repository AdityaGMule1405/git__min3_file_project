import os, shutil, json
from logger import log_action

def organize_files():
    with open('rules.json', 'r') as f:
        rules = json.load(f)

    for filename in os.listdir('.'):
        if os.path.isfile(filename):
            name, ext = os.path.splitext(filename)
            ext = ext.lstrip('.')

            if ext in rules:
                destination_folder = rules[ext]
                if not os.path.exists(destination_folder):
                    os.makedirs(destination_folder)
                    log_action(f'Created folder: {destination_folder}')
                shutil.move(filename, os.path.join(destination_folder, filename))
                log_action(f'Moved {filename} to {destination_folder}')

if __name__ == '__main__':
    organize_files()
