from django.core.management.base import BaseCommand
from nhanes.workprocess.transformation_manager import TransformationManager


class Command(BaseCommand):
    help = 'Aplica todas as regras de normalização nos dados brutos'

    def handle(self, *args, **kwargs):
        manager = TransformationManager()
        manager.apply_transformations()
        self.stdout.write(self.style.SUCCESS('Transformações aplicadas com sucesso'))


"""
5. Fluxo Completo
Definição das Regras: As regras de transformação são definidas no banco de dados,
ligando as variáveis de origem e os campos de destino, além de especificar o
arquivo Python com a lógica de transformação.

Classe Base: A BaseTransformation é criada para padronizar todas as transformações.

Transformações Específicas: Cada transformação específica é criada como uma subclasse
de BaseTransformation.

Gerenciamento das Transformações: A NormalizationManager busca as regras, carrega os
dados, aplica as transformações e salva os resultados.

Execução: Um comando ou script é usado para disparar todo o processo de normalização.

Vantagens
Modularidade: O sistema é modular e cada transformação é isolada, facilitando a
manutenção.
Flexibilidade: Novas transformações podem ser adicionadas facilmente apenas criando uma
nova classe de transformação e adicionando a regra ao banco de dados.
Reusabilidade: A lógica de carregamento e aplicação de transformações é reutilizável
para diferentes tipos de transformações.


"""
