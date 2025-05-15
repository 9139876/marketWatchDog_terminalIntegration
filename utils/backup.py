import datetime
import subprocess
import os
from rich.console import Console

name = 'mt5_integration'

destinations = [
    # {'name': 'yandexCloud', 'path':  '/media/yandexCloud/backups/'},
    # {'name': 'mailCloud', 'path': '/media/mailCloud/backups/'},
    {'name': 'orico', 'path': r'Z:\backups_development'},
]

now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
os.chdir('../')
baseDirectory = os.getcwd()
fileNames = []

console = Console()

# Create archive
with console.status(f'[bold green]Create archive {name}') as status:
    fileName = f'{name}_{now}.zip'
    fileNames.append(fileName)
    proc = subprocess.Popen(f'git archive --output=../backup/{fileName} HEAD', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.wait()
    if proc.poll() == 0:
        console.log(f'Archive {name} created success')
    else:
        console.log(f'{name} - error: {proc.stderr.read()}')

for destination in destinations:
    with console.status(f'[bold green]Copy to {destination["name"]}') as status:
        os.chdir('../backup')
        proc = subprocess.Popen(f'copy {fileName} {destination["path"]}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.wait()
        if proc.poll() == 0:
            console.log(f'{destination["name"]} - copied success')
        else:
            console.log(f'{destination["name"]} - error: {proc.stderr.read()}')

console.log('Done!')
