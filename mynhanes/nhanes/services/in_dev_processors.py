import importlib


class NormalizationProcessor:
    def __init__(self, field_name):
        self.field_name = field_name
        self.field = self.get_field()
        self.rule = self.get_normalization_rule()

    def get_field(self):
        # Recupera o objeto Field correspondente ao nome fornecido
        try:
            return Field.objects.get(field=self.field_name)
        except Field.DoesNotExist:
            raise ValueError(f"Field '{self.field_name}' not found.")

    def get_normalization_rule(self):
        # Recupera a regra de normalização correspondente ao Field, se existir
        try:
            return TransformationRule.objects.get(
                destination_fields=self.field, is_active=True
            )
        except TransformationRule.DoesNotExist:
            return None

    def get_source_data(self):
        # Se houver uma regra, carregar as variáveis de origem
        if self.rule:
            source_variables = self.rule.source_variables.all()
            data = RawData.objects.filter(variable__in=source_variables)
        else:
            # Se não houver regra, tentar carregar dados de uma variável com o mesmo nome
            try:
                variable = Variable.objects.get(variable=self.field_name)
                data = RawData.objects.filter(variable=variable)
            except Variable.DoesNotExist:
                raise ValueError(
                    f"No corresponding Variable found for Field '{self.field_name}'."
                )
        return data

    def apply_transformation(self, data):
        if self.rule:
            # Importa o módulo Python com a regra de transformação
            module_name = f"{self.rule.folder_path}.{self.rule.file_name}".replace(
                ".py", ""
            )
            transformation_module = importlib.import_module(module_name)
            transformed_data = transformation_module.transform(data)
        else:
            # Se não houver regra, retorna os dados diretamente
            transformed_data = data
        return transformed_data

    def process(self):
        # Carrega os dados de origem
        source_data = self.get_source_data()
        # Aplica a transformação, se houver
        normalized_data = self.apply_transformation(source_data)
        # Grava os dados transformados no NormalizedData
        for entry in normalized_data:
            NormalizedData.objects.create(
                cycle=entry.cycle,
                dataset=entry.dataset,
                field=self.field,
                sample=entry.sample,
                sequence=entry.sequence,
                value=entry.value,
            )


# Exemplo de uso da classe
processor = NormalizationProcessor("field_name")
processor.process()
