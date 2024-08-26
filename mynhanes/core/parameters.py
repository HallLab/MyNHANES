import yaml
from pathlib import Path


def load_config():
    config_path = Path(__file__).resolve().parent / "parameters.yml"
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)


config = load_config()

# Exemplo de como acessar as configurações
database_name = config['database']['name']
