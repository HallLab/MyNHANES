import os
import subprocess
import socket
from django.conf import settings


def is_jupyter_running(port=8888):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(('localhost', port))
        s.shutdown(socket.SHUT_RDWR)
        return True
    except ConnectionRefusedError:
        return False
    finally:
        s.close()


def start_jupyter_notebook():
    if is_jupyter_running():
        print("Jupyter Notebook is running.")
        return

    # jupyter_path = os.path.join(settings.BASE_DIR)
    # os.makedirs(jupyter_path, exist_ok=True)

    # Construir o comando para iniciar o Jupyter Notebook
    command = [
        'jupyter', 'notebook',
        '--no-browser',
        '--notebook-dir', settings.BASE_DIR,
        '--port', '8888'
    ]

    # Iniciar o Jupyter Notebook em segundo plano
    subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("Started Jupyter Notebook.")
