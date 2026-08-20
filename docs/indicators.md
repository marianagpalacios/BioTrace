# Indicadores do BioTrace

Este documento descreve os indicadores introduzidos no MVP v0.9.0.

## 1. Indicadores gerais

### Total de sequências

Número total de sequências recebidas pela análise.

### Sequências válidas

Sequências que passaram pela etapa de validação necessária para seguir no pipeline.

### Sequências rejeitadas

Calculadas por:

```text
rejected_sequences = total_sequences - valid_sequences
```

### Taxa de validação

```text
                  valid_sequences
validation_rate = --------------- × 100
                  total_sequences
```

### Taxa de rejeição

```text
                 rejected_sequences
rejection_rate = ------------------ × 100
                  total_sequences
```

### Sequências identificadas

Sequências válidas que receberam uma identificação segundo os critérios do pipeline.

### Sequências não identificadas

```text
unidentified_sequences = valid_sequences - identified_sequences
```

### Taxa de identificação

O denominador é o número de sequências válidas:

```text
                      identified_sequences
identification_rate = -------------------- × 100
                         valid_sequences
```

Isso é importante porque sequências rejeitadas antes da classificação não devem diminuir artificialmente a taxa de identificação.

### Taxa de não identificação

```text
                    unidentified_sequences
unidentified_rate = ---------------------- × 100
                         valid_sequences
```

Quando o denominador é zero, a taxa é representada como `0.0`.

## 2. Indicadores de qualidade FASTQ

Esses indicadores se aplicam apenas a entradas FASTQ. São registrados:

- Phred médio, mínimo e máximo;
- comprimento médio, mínimo e máximo;
- reads aprovadas e rejeitadas no QC;
- reads afetadas por trimming;
- número total de bases removidas.

Para FASTA, essas métricas não existem. Por isso, `applicable = false` e os valores específicos são representados por `None`, em vez de zero.

## 3. Indicadores taxonômicos

### Espécies observadas

`observed_species_count` representa quantas espécies diferentes foram observadas entre os resultados identificados.

Exemplo:

```text
Species alpha
Species alpha
Species beta

observed_species_count = 2
```

### Frequência absoluta

Número de identificações de cada espécie.

### Proporção

```text
             identificações da espécie
proporção = ------------------------- × 100
                 total identificado
```

### Espécie mais frequente

Espécie com maior número de registros identificados.

### Limitação de interpretação

`observed_species_count` representa apenas a riqueza observada no conjunto analisado. Não representa diretamente biodiversidade ecológica e não deve ser apresentado como índice de Shannon, Simpson ou outro índice de diversidade.

## 4. Indicadores de busca

### Identidade

São calculados o valor médio, o mínimo e o máximo. Também são contabilizadas as seguintes faixas:

- maior ou igual a 99%;
- entre 95% e menos de 99%;
- abaixo de 95%.

Essas faixas servem como resumo descritivo dos resultados. Elas não representam uma probabilidade de identificação correta.

### Cobertura

São calculadas a cobertura média, a mínima e a máxima.

Identidade e cobertura devem ser consideradas separadamente. Uma identidade elevada em apenas uma pequena região da sequência não é equivalente a uma identidade elevada cobrindo praticamente toda a sequência.

### E-value

Quando disponível no BLAST, representa a expectativa estatística relacionada à ocorrência de alinhamentos semelhantes por acaso. São armazenados a média, o mínimo e o máximo.

Essa métrica não é produzida pelo backend pairwise.

### Bit score

Quando disponível no BLAST, são armazenados a média, o mínimo e o máximo.

Essa métrica também não é produzida pelo backend pairwise.

## 5. Indicadores operacionais

### Duração total

Tempo total conhecido para execução da análise.

### Tempo médio por sequência

```text
                            duração total
mean_seconds_per_sequence = -------------
                            nº de sequências
```

Quando nenhuma sequência foi processada, esse valor permanece `None`.

### Cache hits

Quantidade de resultados recuperados do cache.

### Cache misses

Quantidade de buscas que não foram atendidas pelo cache.

### Taxa de cache hit

```text
                 cache_hits
cache_hit_rate = ------------------------ × 100
                 cache_hits + cache_misses
```

### Erros de busca

Quantidade de operações de busca que terminaram em erro.

### Timeouts

Quantidade de operações que excederam o tempo máximo configurado.

## 6. Warnings

Warnings são indicadores textuais produzidos a partir de regras explícitas. Exemplos:

- taxa de rejeição elevada;
- taxa de identificação baixa;
- rejeições de QC;
- resultados abaixo de um limiar de identidade;
- timeouts;
- erros de busca.

Warnings ajudam a chamar atenção para características da execução. Eles não representam automaticamente erros científicos nem substituem a interpretação dos resultados.

## 7. Princípios

Os indicadores do BioTrace seguem três princípios:

1. distinguir ausência de informação de valor zero;
2. evitar transformar métricas técnicas em afirmações científicas mais fortes do que os dados permitem;
3. manter as fórmulas e critérios explícitos e reproduzíveis.
