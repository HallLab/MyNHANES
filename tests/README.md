# Testes MyNHANES

Este diretório contém os testes para o projeto MyNHANES. Os testes são realizados utilizando arquivos de fixtures, que são salvos na pasta `fixtures`.

## Gerando arquivos de fixtures

Para gerar novos arquivos de fixtures, execute o seguinte comando dentro da pasta `tests`:

```bash
$ python generate_fixtures.py
```

Caso queira gerar uma fixture para um único modelo manualmente, você pode rodar o seguinte comando dentro da pasta `mynhanes`:

```bash
$ python manage.py dumpdata nhanes.Cycle --output=tests/fixtures/cycle_fixture.json
```

Substitua `nhanes.Cycle` pelo nome do modelo desejado e ajuste o nome do arquivo de saída conforme necessário.

## Executando testes de cobertura

Para rodar a cobertura de testes, use os seguintes comandos:

```bash
$ coverage run --source='.' manage.py test
$ coverage report
```

## Executando testes com pytest

Para rodar os testes com `pytest`, basta executar:

```bash
$ pytest
```

Certifique-se de que todas as fixtures necessárias estejam carregadas corretamente antes de executar os testes.
