import pytest
from unittest.mock import patch, MagicMock
from django.conf import settings
from pathlib import Path
from nhanes.models import NHANESCycle, NHANESDataset, DatasetMetadata
from nhanes.services.loader import download_nhanes_files
import os


# Test the download_nhanes_files function
@pytest.mark.django_db
@patch('nhanes.services.loader.download_file', return_value=True)
@patch('requests.get')
def test_download_nhanes_files(mock_get, mock_download_file):
    # Configuração do ambiente de teste
    cycle = NHANESCycle.objects.create(
        cycle_name='2017-2018',
        base_dir='downloads/data',
        year_code='J',
        base_url='https://wwwn.cdc.gov/Nchs/Nhanes'
    )
    dataset = NHANESDataset.objects.create(name='DEMO', is_download=True)
    metadata = DatasetMetadata.objects.create(
        dataset=dataset,
        cycle=cycle,
        metadata_url='https://wwwn.cdc.gov/Nchs/Nhanes/2017-2018/DEMO_J.htm',
        description="This is a test metadata",
        status='pending'
    )

    # Configurar o mock para simular uma resposta HTTP bem-sucedida
    response = MagicMock()
    response.status_code = 200
    response.iter_content = lambda chunk_size: [b'data']
    mock_get.return_value = response

    # Simulando a função download_file para sempre retornar True
    mock_download_file.return_value = True

    # Chamar a função de download
    download_nhanes_files()

    # Atualiza o objeto para verificar mudanças
    metadata.refresh_from_db()

    # Verificações
    assert metadata.status == 'complete'
    # assert mock_get.called
    assert mock_download_file.called
    mock_download_file.assert_called_with(
        'https://wwwn.cdc.gov/Nchs/Nhanes/2017-2018/DEMO_J.htm',
        Path(settings.BASE_DIR) / 'downloads' / 'data' / 'DEMO_J.htm'
    )


# Use uma variável de ambiente para controlar a execução
@pytest.mark.skipif(
        os.environ.get('RUN_REAL_DOWNLOAD_TESTS') != 'True',
        reason="Real download tests are disabled"
        )
def test_real_download():
    url = 'https://wwwn.cdc.gov/Nchs/Nhanes/2017-2018/DEMO_J.PTX'
    save_path = Path(settings.BASE_DIR) / 'downloads' / 'data' / 'DEMO_J.htm'
    assert download_nhanes_files(url, save_path) is True
    # Verifique se o arquivo foi salvo
    assert os.path.exists(save_path)
