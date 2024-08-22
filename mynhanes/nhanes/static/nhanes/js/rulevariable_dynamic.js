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
