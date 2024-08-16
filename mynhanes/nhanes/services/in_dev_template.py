# Exemplo de um arquivo de transformação (rules/normalization_rule.py)


def transform(data):
    # Implementa a lógica de transformação
    transformed_data = []
    for entry in data:
        # Exemplo simples de transformação: multiplicar por 2
        transformed_value = int(entry.value) * 2
        entry.value = transformed_value
        transformed_data.append(entry)
    return transformed_data
