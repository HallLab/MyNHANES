import sys
import os
from pathlib import Path

# Adiciona o diretório do projeto ao PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent))
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'
