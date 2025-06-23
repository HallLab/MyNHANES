
# mynhanes/cli_entry.py

import sys
import os
from django.core.management import execute_from_command_line


def main():
    # Caminho da pasta onde está o manage.py (e a pasta 'core')
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Adiciona ao sys.path para que 'core.settings' seja visível
    sys.path.insert(0, base_dir)

    # Define o módulo de configuração padrão do Django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

    # Executa o comando como se fosse python manage.py <args>
    execute_from_command_line(sys.argv)
