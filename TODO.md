# TODO List

## High Priority

- [ ] Criar os Modulos
- [ ] ---

## Medium Priority

- [ ] ---
- [ ] ---

## Low Priority

- [ ] ---
- [ ] Create interface to manage de Normalizations Rules


STOP: Query.py has problem to consider the filter as select values.


Preciso fazeer:
- Criar o modulo de query
- testar todo o fluxo


How to be the Model:

- Raw table to support the source data
- Normal tables to suport the transf from rules
- Tables to support the operations, like workprocess control




Sua abordagem para carregar dados do NHANES e processá-los através de uma série de transformações para movê-los de `RawData` para `NormalizedData` é bastante lógica e organizada. Vou abordar os principais conceitos envolvidos nesse fluxo, incluindo a ordem e o momento de cada passo, e como as diferentes partes do sistema se relacionam.

### 1. **Carregamento Inicial dos Dados (Ingestão)**
   - **RawData Model**: Os dados brutos do NHANES são inicialmente carregados na tabela `RawData`. Isso inclui todas as variáveis e amostras disponíveis, organizadas conforme os datasets e ciclos. Esse passo de ingestão deve garantir que os dados sejam armazenados com consistência e integridade, sem aplicar nenhuma transformação inicial.
   - **Batch Loading**: Dependendo do tamanho dos datasets, é recomendável carregar os dados em lotes (batches) para evitar problemas de desempenho e memória. Todos os dados necessários são carregados, independentemente de quais transformações serão aplicadas depois.

### 2. **Identificação das Regras de Normalização**
   - **NormalizationRule Model**: Após o carregamento, o sistema verifica as regras de normalização definidas no modelo `NormalizationRule`. Cada regra indica qual transformação aplicar, quais variáveis de origem (`Variables`) são necessárias, e qual script Python (arquivo `.py`) deve ser usado para essa transformação.
   - **Mapping das Variáveis**: É importante que as regras de normalização possam mapear variáveis de diferentes datasets e ciclos para uma única transformação. Isso significa que uma transformação pode precisar acessar dados de múltiplos `DatasetCycle` para uma mesma variável, unificando dados antes de aplicar a transformação.

### 3. **Execução das Transformações**
   - **Transformação Condicional**: O processo de transformação deve ser acionado após todos os dados necessários terem sido carregados em `RawData`. Isso permite que todas as variáveis de diferentes datasets estejam disponíveis para a transformação, garantindo que a regra tenha acesso a todos os dados necessários.
   - **Sequenciamento das Transformações**: Se as transformações dependem de múltiplas variáveis ou passos anteriores, pode ser necessário sequenciar as transformações. Por exemplo, uma transformação pode precisar ser aplicada antes de outra para garantir que os dados estejam no estado correto.

### 4. **Execução das Regras e Transferência para NormalizedData**
   - **Rotina de Normalização**: Uma rotina centralizada processa cada `Field` em `NormalizedData`, verificando se há uma regra de normalização associada. Se houver, a rotina carrega as variáveis necessárias de `RawData`, aplica a transformação e grava o resultado em `NormalizedData`.
   - **Fallback sem Regra**: Se não houver uma regra para um campo específico, o sistema pode tentar usar uma variável com o mesmo nome diretamente de `RawData`. Se encontrado, esses dados são transferidos diretamente para `NormalizedData`.

### 5. **Otimização do Processo**
   - **Carregamento Antecipado vs. Sob Demanda**: O carregamento antecipado de todos os dados para `RawData` antes da transformação tem a vantagem de garantir que todas as variáveis necessárias estejam disponíveis. No entanto, isso pode exigir bastante memória, dependendo do tamanho dos dados. Alternativamente, as variáveis necessárias para uma transformação específica poderiam ser carregadas sob demanda, durante a execução da regra.
   - **Batch Processing**: Para evitar sobrecarga, a transformação poderia ser realizada em lotes, processando um subconjunto de `Fields` ou `Variables` por vez.

### 6. **Manutenção e Atualização**
   - **Versão das Regras**: As regras de normalização podem ser versionadas, e o sistema deve permitir a atualização de regras sem impactar dados já normalizados. Isso pode incluir um histórico das regras aplicadas para que você possa reprocessar dados se necessário.
   - **Auditoria e Logs**: Cada transformação deve ser registrada para garantir a rastreabilidade e auditoria, especialmente se uma transformação falhar ou produzir resultados inesperados.

### Conclusão

A estratégia de carregar toda a `RawData` antes de aplicar as transformações garante que o sistema tenha todos os dados necessários disponíveis, o que é particularmente útil quando uma transformação depende de múltiplas variáveis ou datasets. Esse fluxo centralizado permite um processamento mais coordenado e garante que as transformações sejam aplicadas de forma consistente.

Se precisar de mais detalhes ou ajustes no conceito, estou à disposição para ajudar!