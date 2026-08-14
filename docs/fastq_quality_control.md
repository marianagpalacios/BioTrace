# Controle de qualidade FASTQ no BioTrace

## Objetivo

O MVP v0.6.0 introduz leitura de arquivos FASTQ e um fluxo didático de controle de qualidade baseado em escores Phred.

O objetivo é permitir o estudo controlado e reproduzível das etapas que antecedem a classificação de sequências. O suporte a FASTQ não representa um pipeline completo de sequenciamento de nova geração.

## FASTA e FASTQ

FASTA registra identificadores e sequências:

```text
>read_1
ACGTACGT
```

FASTQ registra quatro linhas por read:

```text
@read_1
ACGTACGT
+
IIIIIIII
```

Essas linhas representam o identificador, a sequência, um separador e as qualidades codificadas. A principal diferença é que FASTQ associa um escore de qualidade a cada base.

## Escores Phred

O escore Phred representa uma estimativa logarítmica da probabilidade de erro na identificação de uma base:

```text
Q = -10 × log10(P)
```

Em que `P` é a probabilidade estimada de erro.

| Phred | Probabilidade de erro | Acurácia estimada |
|---:|---:|---:|
| Q10 | 1 em 10 | 90% |
| Q20 | 1 em 100 | 99% |
| Q30 | 1 em 1.000 | 99,9% |

Um valor Phred não comprova sozinho que uma sequência é biologicamente correta. Ele representa uma estimativa técnica de confiança na chamada da base.

## Leitura dos escores no BioTrace

O BioTrace utiliza o Biopython para interpretar FASTQ. Cada registro é transformado em uma estrutura com `id`, `sequence` e uma lista de `qualities`. A quantidade de escores deve ser igual ao comprimento da sequência; arquivos inconsistentes são rejeitados pelo leitor.

## Fluxo do controle de qualidade

```text
FASTQ
  ↓
parser
  ↓
sequence + Phred
  ↓
trimming terminal
  ↓
validação das bases
  ↓
comprimento
  ↓
Phred médio
  ↓
aprovado / rejeitado
  ↓
estatísticas
  ↓
classificação
```

A ordem é importante porque o comprimento e as estatísticas de qualidade são calculados sobre a sequência retida após o trimming.

## Trimming das extremidades

O BioTrace remove bases abaixo do limiar configurado somente nas extremidades 5' e 3'. Na extremidade 5', o algoritmo avança a partir do início enquanto os escores forem menores que o limiar. Na extremidade 3', ele recua a partir do final sob a mesma condição.

Bases de baixa qualidade localizadas no interior do read não são removidas, pois isso alteraria artificialmente as coordenadas da sequência. O trimming pode ser desabilitado.

## Qualidade média

A qualidade média é a média aritmética dos escores Phred retidos:

```text
Phred médio = soma dos escores / número de bases
```

O read é rejeitado quando a média fica abaixo do valor configurado. A média pode esconder regiões internas ruins e deve ser interpretada junto com outras métricas.

## Percentuais Q20 e Q30

Q20 é o percentual das bases retidas com Phred maior ou igual a 20:

```text
Q20 (%) = bases com Q ≥ 20 / bases retidas × 100
```

Q30 é o percentual das bases retidas com Phred maior ou igual a 30:

```text
Q30 (%) = bases com Q ≥ 30 / bases retidas × 100
```

O relatório apresenta essas métricas por read e também de forma agregada.

## Filtragem por comprimento

Depois do trimming, o BioTrace verifica se o comprimento retido está dentro dos limites configurados. Os padrões são 500 a 800 bp, acompanhando o fluxo didático COI-5P e o banco de referência atual. Isso não significa que todo FASTQ deva possuir reads nessa faixa.

## Registros aprovados e rejeitados

Um registro é aprovado quando possui bases aceitas, mantém bases depois do trimming, atende aos limites de comprimento e possui qualidade média igual ou superior ao limiar. Somente reads aprovados seguem para estatísticas e classificação taxonômica.

Um registro pode ser rejeitado por bases inválidas, sequência vazia após trimming, comprimento abaixo ou acima dos limites ou qualidade Phred média insuficiente. Os motivos são preservados no relatório para auditoria.

## Parâmetros configuráveis

O MVP permite configurar:

- Phred médio mínimo;
- comprimento mínimo após QC;
- comprimento máximo após QC;
- ativação do trimming terminal;
- limiar Phred do trimming;
- aceitação da base ambígua `N`.

Os parâmetros FASTQ não alteram a análise FASTA.

## Relatório de qualidade

Para cada read, o BioTrace registra identificador, comprimentos bruto e retido, bases removidas em 5' e 3', Phred médio, mínimo e máximo, Q20, Q30, aprovação e motivos de rejeição. A interface permite baixar o relatório como CSV, inclusive quando nenhum read é aprovado.

## Manifesto e reprodutibilidade

O manifesto de schema `1.1` registra o formato da entrada, os parâmetros de qualidade, hashes SHA-256 e o fingerprint da execução. Alterar um parâmetro de qualidade altera as condições da execução e seu fingerprint. Hashes detectam alterações nos artefatos, mas não comprovam qualidade científica por si só.

## Limitações científicas

O MVP v0.6.0 não implementa:

- paired-end;
- merge de R1 e R2;
- demultiplexing;
- remoção de adaptadores;
- remoção de primers;
- denoising;
- remoção de quimeras;
- inferência de ASVs;
- agrupamento em OTUs;
- DADA2;
- QIIME 2;
- BLAST;
- orientação automática;
- complemento reverso;
- alinhamento biológico;
- arquivos `FASTQ.gz`.

```text
suporte a FASTQ ≠ pipeline completo de NGS
```

O fluxo foi construído para estudo controlado de parsing, qualidade Phred, trimming terminal, filtragem, auditoria e reprodutibilidade. Análises científicas reais exigem ferramentas especializadas, controles experimentais e validação adequada ao protocolo utilizado.
