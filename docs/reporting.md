# Reporting

O módulo de reporting do BioTrace transforma os resultados técnicos da análise em indicadores estruturados, resumos e arquivos exportáveis.

## Objetivo

O reporting existe para separar duas responsabilidades:

- execução científica e computacional da análise;
- apresentação e consolidação dos resultados.

O pipeline continua responsável por:

- leitura de FASTA e FASTQ;
- validação;
- controle de qualidade;
- busca pairwise ou BLAST;
- classificação;
- cache;
- reprodutibilidade.

O módulo `src/reporting/` recebe esses resultados e produz um `AnalysisReport`.

## Estrutura

O pacote é composto por:

```text
src/reporting/
├── __init__.py
├── contracts.py
├── indicators.py
├── report_service.py
├── exporters.py
└── warnings.py
```

## AnalysisReport

O relatório estruturado agrega:

```text
AnalysisReport
├── metadata
├── indicators
├── taxonomy
├── quality
├── search
├── performance
├── results
└── warnings
```

### Metadata

Registra informações como:

- versão do BioTrace;
- formato de entrada;
- backend de busca;
- horário de geração do relatório.

### Indicadores gerais

Incluem:

- total de sequências;
- sequências válidas;
- sequências rejeitadas;
- sequências identificadas;
- sequências não identificadas;
- taxa de validação;
- taxa de rejeição;
- taxa de identificação;
- taxa de não identificação.

A taxa de identificação usa como denominador as sequências válidas.

### Indicadores taxonômicos

Incluem:

- número de espécies observadas;
- espécie mais frequente;
- frequência absoluta por espécie;
- proporção por espécie.

`observed_species_count` representa apenas a riqueza observada no conjunto analisado. Ele não deve ser interpretado como índice de diversidade ecológica. O BioTrace não calcula Shannon, Simpson ou outros índices ecológicos neste MVP.

### Indicadores de qualidade

Os indicadores de qualidade são aplicáveis a entradas FASTQ e incluem:

- Phred médio, mínimo e máximo;
- comprimento médio, mínimo e máximo;
- reads aprovadas e rejeitadas no QC;
- reads afetadas pelo trimming;
- bases removidas pelo trimming.

Para FASTA, `applicable = false` e os campos específicos de qualidade ficam como `None`. Isso evita representar a ausência de uma métrica como zero.

### Indicadores de busca

Incluem:

- identidade média, mínima e máxima;
- cobertura média, mínima e máxima;
- e-value médio, mínimo e máximo;
- bit score médio, mínimo e máximo;
- número de resultados com identidade maior ou igual a 99%;
- número de resultados com identidade entre 95% e 99%;
- número de resultados com identidade abaixo de 95%.

E-value e bit score são métricas associadas ao BLAST e podem não se aplicar ao backend pairwise. Esses valores não são convertidos em uma probabilidade artificial de identificação correta.

### Indicadores de desempenho

Incluem:

- duração total;
- tempo médio por sequência;
- cache hits e misses;
- taxa de cache hit;
- erros de busca;
- timeouts de busca.

O objetivo é fornecer indicadores operacionais simples, e não implementar um profiler completo.

## Warnings

Warnings são gerados a partir de condições explícitas, como:

- taxa elevada de rejeição;
- baixa taxa de identificação;
- rejeições de QC;
- resultados abaixo do limiar de identidade;
- timeouts;
- erros de busca.

Eles são avisos objetivos e não substituem a interpretação científica.

## Exportação

O BioTrace pode gerar:

- `analysis_report.json`: representação estruturada completa do relatório;
- `analysis_results.csv`: resultados individuais da análise;
- `species_summary.csv`: campos `species`, `count` e `proportion`;
- `analysis_report.md`: representação resumida e legível do relatório.

## Reprodutibilidade

O schema de reprodutibilidade `1.4` pode registrar informações associadas ao reporting, incluindo:

- versão do relatório;
- indicadores calculados;
- warnings;
- duração da análise;
- arquivos exportados;
- SHA-256 dos arquivos;
- tamanho dos arquivos.

Isso permite verificar quais artefatos foram produzidos em uma execução.
