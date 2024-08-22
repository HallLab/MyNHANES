# from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from .models import Dataset, Data


def get_datasets_for_variable(request):
    variable_id = request.GET.get('variable_id')
    datasets = Dataset.objects.filter(
        id__in=Data.objects.filter(variable_id=variable_id).values('dataset_id')
    ).distinct()
    datasets_data = [{'id': ds.id, 'name': ds.dataset} for ds in datasets]
    return JsonResponse(datasets_data, safe=False)

"""
Como Funciona:
View e URL: A view get_datasets_for_variable retorna os Datasets disponíveis para a Variable selecionada.
Formulário e Script: O formulário RuleVariableForm é estendido para incluir um script JavaScript (rulevariable_dynamic.js) que faz uma requisição AJAX ao servidor sempre que a Variable é alterada.
Atualização do Campo: O campo Dataset é atualizado com os datasets retornados pelo AJAX.
Benefícios:
Filtro Dinâmico: Isso garante que o usuário só possa selecionar datasets que realmente contenham a Variable escolhida.
Melhoria na UX: Melhora a experiência do usuário, simplificando e reduzindo erros na seleção de datasets.
"""