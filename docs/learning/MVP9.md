# MVP 9 — Indicadores e relatórios

## Objetivo

O MVP v0.9.0 adiciona uma camada dedicada de reporting ao BioTrace.

Até o MVP anterior, o foco principal estava na execução do pipeline:

```text
entrada
→ validação
→ QC
→ busca
→ classificação
```

Neste MVP, os resultados passam também por:

```text
resultados
→ indicadores
→ warnings
→ relatório estruturado
→ exportação
```

## Conceitos praticados

### Separação de responsabilidades

A busca e a classificação não devem saber como o relatório será apresentado. Da mesma forma, o reporting não deve executar BLAST ou classificação. Essa divisão reduz o acoplamento.

### Dataclasses

Os contratos de reporting utilizam dataclasses para representar estruturas como:

- `AnalysisIndicators`;
- `TaxonomyIndicators`;
- `QualityIndicators`;
- `SearchIndicators`;
- `PerformanceIndicators`;
- `AnalysisReport`.

Isso fornece uma estrutura explícita para os dados.

### Agregação

Resultados individuais são transformados em indicadores agregados:

```text
resultado 1
resultado 2
resultado 3
       ↓
frequências
médias
taxas
mínimos
máximos
```

### Tratamento de denominador zero

Taxas precisam considerar casos em que não existe denominador válido. Por exemplo, zero sequências válidas não pode provocar divisão por zero.

### None versus zero

Um valor zero pode representar uma medida real. `None` representa ausência ou não aplicabilidade da medida.

Por exemplo, FASTA não possui Phred. Isso não significa `Phred = 0`, mas sim que Phred não é aplicável.

### Reprodutibilidade

Os arquivos de relatório podem ser associados a hashes SHA-256. Isso permite detectar alterações nos artefatos exportados.

### Testes

Os testes deste MVP cobrem:

- cálculos gerais;
- taxonomia;
- FASTQ;
- busca;
- cache;
- desempenho;
- warnings;
- relatórios;
- JSON;
- CSV;
- Markdown;
- reprodutibilidade;
- regressão das funcionalidades anteriores.

## Resultado arquitetural

A arquitetura passa a incluir:

```text
Pipeline
   ↓
Analysis results
   ↓
Reporting
   ↓
AnalysisReport
   ↓
JSON / CSV / Markdown / UI
```

Essa camada prepara o projeto para a estabilização da versão 1.0.
