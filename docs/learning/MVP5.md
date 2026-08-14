# MVP 5 — FASTQ e controle de qualidade

## Objetivo de aprendizagem

O MVP v0.6.0 amplia o BioTrace de uma entrada exclusivamente FASTA para um fluxo que também interpreta FASTQ, avalia qualidade Phred, remove bases ruins nas extremidades e registra as decisões no manifesto reproduzível.

O objetivo educacional não é construir um pipeline completo de NGS, mas compreender como qualidade técnica, validação, classificação e proveniência se relacionam.

## FASTA e FASTQ

FASTA contém identificador e sequência. FASTQ acrescenta uma linha de qualidade para cada read. Portanto, duas sequências iguais podem receber decisões diferentes quando seus escores de qualidade são diferentes.

Cada base de um FASTQ deve possuir exatamente um escore. O parser rejeita registros em que o comprimento da sequência e a quantidade de qualidades não correspondem.

## Qualidade Phred

Phred é uma escala logarítmica associada à probabilidade estimada de erro de uma base:

```text
Q = -10 × log10(P de erro)
```

- Q10 corresponde a aproximadamente 90% de acurácia;
- Q20 corresponde a aproximadamente 99%;
- Q30 corresponde a aproximadamente 99,9%.

Esses valores são estimativas técnicas e não substituem validação científica.

## Métricas utilizadas

O BioTrace calcula por read:

- comprimento bruto e retido;
- Phred médio, mínimo e máximo;
- percentual de bases Q20;
- percentual de bases Q30;
- quantidade removida nas extremidades 5' e 3';
- aprovação ou rejeição;
- motivos de rejeição.

O resumo agregado informa quantos reads foram recebidos, aprovados e rejeitados, além das bases removidas e métricas das qualidades retidas.

## Trimming terminal

O trimming percorre as extremidades enquanto a qualidade estiver abaixo do limiar. Bases ruins no interior do read são preservadas.

Essa decisão evita apagar posições internas e alterar artificialmente as coordenadas da sequência. O algoritmo implementado não substitui ferramentas especializadas de trimming e preparação de bibliotecas.

## Ordem das operações

```text
leitura FASTQ
→ trimming 5' e 3'
→ validação das bases
→ filtro de comprimento
→ filtro de qualidade média
→ relatório de QC
→ estatísticas
→ classificação
```

A ordem importa: comprimento e qualidade são avaliados depois do trimming.

## Arquitetura compartilhada

FASTA e FASTQ possuem entradas diferentes, mas compartilham o núcleo de classificação:

```text
FASTA → validação ┐
                  ├→ sequências válidas → classificação
FASTQ → QC ───────┘
```

Essa separação evita duplicar estatísticas, acesso ao banco, ranking e montagem dos resultados.

## Reprodutibilidade

O manifesto de schema `1.1` registra o formato e os parâmetros de QC. Assim, uma mudança no Phred mínimo, no comprimento ou no trimming muda o fingerprint da execução.

O teste de reprodução confirmou que a mesma entrada, código, banco e parâmetros produzem o mesmo fingerprint e o mesmo hash de resultados.

## Exemplo controlado

O arquivo `data/examples/example_reads.fastq` contém três situações determinísticas:

- um read aprovado após trimming;
- um read rejeitado por baixa qualidade média;
- um read rejeitado por comprimento insuficiente.

Esse conjunto é pequeno e didático. Ele não representa a diversidade ou a complexidade de um experimento ambiental real.

## Limitações aprendidas

Aceitar FASTQ não equivale a oferecer um pipeline completo de NGS. O MVP não implementa paired-end, merge R1/R2, demultiplexing, remoção de adaptadores ou primers, denoising, quimeras, ASVs, OTUs, DADA2, QIIME 2, orientação automática, complemento reverso, alinhamento biológico ou `FASTQ.gz`.

## Resultado

Ao final deste MVP, o BioTrace consegue receber FASTA ou FASTQ, aplicar um controle de qualidade auditável, classificar apenas reads aprovados, exportar o relatório e reproduzir a execução a partir do manifesto.
