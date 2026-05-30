import datetime
def log_action(*args):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = ' '.join(map(str, args))
    with open('organizer.log', 'a') as f:
        f.write(f'[{timestamp}] {message}\n')
