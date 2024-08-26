# from django.shortcuts import render

# Create your views here.
# from django.http import JsonResponse
# from .models import Dataset, Data


# def get_datasets_for_variable(request):
#     variable_id = request.GET.get('variable_id')
#     datasets = Dataset.objects.filter(
#         id__in=Data.objects.filter(variable_id=variable_id).values('dataset_id')
#     ).distinct()
#     datasets_data = [{'id': ds.id, 'name': ds.dataset} for ds in datasets]
#     return JsonResponse(datasets_data, safe=False)

# # def get_datasets(request):
# #     variable_id = request.GET.get('variable_id')
# #     datasets = Data.objects.filter(data__variable_id=variable_id).distinct()
# #     dataset_list = [{'id': ds.id, 'name': ds.dataset} for ds in datasets]
# #     return JsonResponse({'datasets': dataset_list})
