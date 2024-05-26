from django.core.management import call_command
import os


def deploy(deploy_type='local', path=None):
    """
    Função para facilitar o deployment do projeto NHANES.

    Args:
    deploy_type (str): Tipo de deployment ('local' ou 'remote').
    path (str, optional): Caminho para a base de dados quando 'remote'.
                            Somente necessário se deploy_type é 'remote'.
    """
    # Definir as variáveis de ambiente ou configurações necessárias
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mynhanes.settings")

    # Executar o comando de deploy usando o call_command do Django
    if deploy_type == 'local':
        call_command('deploy', deploy='local')
    elif deploy_type == 'remote' and path:
        call_command('deploy', deploy='remote', path=path)
    else:
        raise ValueError(
            "Para deployment 'remote', um caminho deve ser especificado."
            )
