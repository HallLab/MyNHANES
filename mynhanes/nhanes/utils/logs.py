import logging
from django.contrib.contenttypes.models import ContentType
from nhanes.models import Logs

"""
Status:
    e = error
    w = warning
    s = success
"""


def start_logger(process=None):
    # create a logger
    logger = logging.getLogger(process)

    # configure the logger
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


# Logs
def logger(log, status="e", message=None, content_object=None):
    log.info(message)
    if not message:
        message = 'not inform'

    # Verificar se o objeto de conteúdo é fornecido
    if content_object:
        content_type = ContentType.objects.get_for_model(content_object)
        object_id = content_object.pk
    else:
        content_type = None
        object_id = None

    # Criar o log
    Logs.objects.create(
        # process=log.name,
        description=message,
        status=status,
        content_type=content_type,
        object_id=object_id
    )
    return True
