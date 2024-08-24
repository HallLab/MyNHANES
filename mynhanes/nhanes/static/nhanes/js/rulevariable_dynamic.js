document.addEventListener('DOMContentLoaded', function () {
    const variableField = document.getElementById('id_variable');
    const datasetField = document.getElementById('id_dataset');

    if (variableField) {
        variableField.addEventListener('change', function () {
            const variableId = this.value;
            if (!variableId) {
                datasetField.innerHTML = '<option value="">---------</option>';
                return;
            }

            const url = new URL(window.location.origin + '/admin/get-datasets/');
            url.searchParams.append('variable_id', variableId);

            fetch(url)
                .then(response => response.json())
                .then(data => {
                    datasetField.innerHTML = '<option value="">---------</option>';
                    data.forEach(function (dataset) {
                        const option = document.createElement('option');
                        option.value = dataset.id;
                        option.textContent = dataset.name;
                        datasetField.appendChild(option);
                    });
                });
        });
    }
});

// (function ($) {
//     $(document).ready(function () {
//         $('#id_variable').change(function () {
//             var variableId = $(this).val();
//             if (variableId) {
//                 $.ajax({
//                     url: '/nhanes/get_datasets/',  // A URL para a view que buscará os datasets
//                     data: {
//                         'variable_id': variableId
//                     },
//                     success: function (data) {
//                         var datasetSelect = $('#id_dataset');
//                         datasetSelect.empty();
//                         $.each(data.datasets, function (index, dataset) {
//                             datasetSelect.append(
//                                 $('<option></option>').attr('value', dataset.id).text(dataset.name)
//                             );
//                         });
//                     }
//                 });
//             } else {
//                 $('#id_dataset').empty();
//             }
//         });
//     });
// })(django.jQuery);
