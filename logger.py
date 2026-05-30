import datetime
def log_action(action):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('history.log', 'a') as f:
        f.write(f'[{timestamp}] {action}\n')
