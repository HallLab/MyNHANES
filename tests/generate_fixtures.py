import os
import sys
from django.core.management import call_command
from django.apps import apps
# from django.conf import settings

# Adicionar o caminho de manage.py ao sys.path para garantir que Django consiga
# carregar as configurações corretamente
sys.path.append(os.path.join(os.path.dirname(__file__), '../mynhanes'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')


# Carregar as configurações do Django
import django  # noqa: E402
django.setup()

# Definir o caminho onde os arquivos de fixture serão salvos
# FIXTURES_DIR = os.path.join(settings.BASE_DIR, 'tests', 'fixtures')
FIXTURES_DIR = 'fixtures'

# Certifique-se de que a pasta existe
os.makedirs(FIXTURES_DIR, exist_ok=True)


def generate_fixtures():

    # models list to fixture
    list_models = [
        'version',
        'cycle',
        'group',
        'dataset',
        'tag',
        'variable',
        'variablecycle',
        'datasetcycle',
        'rule',
        'rulevariable',
        'querycolumns',
        'querystructure',
        'QueryFilter',
        'workprocessnhanes',
        'workprocessmasterdata',
        'workprocessrule',
        ]

    # Obtém todas as apps instaladas
    for app in apps.get_app_configs():
        # Itera sobre todos os modelos da app
        for model in app.get_models():
            model_name = model._meta.model_name
            app_label = model._meta.app_label

            if model_name not in list_models:
                continue

            # Gera o nome do arquivo de fixture para o modelo
            fixture_filename = f"{model_name}_fixture.json"
            fixture_path = os.path.join(FIXTURES_DIR, fixture_filename)

            # Comando para gerar as fixtures
            with open(fixture_path, 'w') as fixture_file:
                call_command(
                    'dumpdata',
                    f'{app_label}.{model_name}',
                    '--indent', '4',
                    stdout=fixture_file)

            print(f"Fixture for {app_label}.{model_name} saved to {fixture_path}")

    print("All fixtures generated successfully!")


if __name__ == "__main__":
    generate_fixtures()
