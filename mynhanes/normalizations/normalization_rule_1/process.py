# transformation_rule_1/process.py


def transform(data):
    normalized_field = f"normalized_{data['field']}"
    normalized_value = data["value"].strip().lower()
    return {
        "normalized_field": normalized_field,
        "normalized_value": normalized_value,
        "sample": data["sample"],
        "sequence": data["sequence"],
    }


def transform_2(data):
    # Implementa a lógica de transformação
    transformed_data = []
    for entry in data:
        # Exemplo simples de transformação: multiplicar por 2
        transformed_value = int(entry.value) * 2
        entry.value = transformed_value
        transformed_data.append(entry)
    return transformed_data
