## MVP 0 — Análise inicial de arquivos FASTA

Este documento registra o desenvolvimento inicial do MVP do projeto eDNA Insight, uma aplicação simples para leitura, análise básica e identificação preliminar de sequências em arquivos FASTA.

## Objetivo

O objetivo deste MVP é validar o fluxo mínimo de funcionamento da aplicação:

1. receber um arquivo FASTA;
2. ler as sequências contidas no arquivo;
3. calcular estatísticas básicas;
4. comparar as sequências com um banco local;
5. apresentar uma identificação taxonômica simplificada;
6. exibir tabela, gráfico e opção de exportação dos resultados.

## Estrutura do projeto
```
edna-insight/
├── app/
│   └── main.py
├── src/
│   ├── fasta.py
│   ├── stats.py
│   ├── similarity.py
│   └── taxonomy.py
├── data/
│   ├── examples/
│   │   └── sample.fasta
│   └── reference/
│       └── species_database.csv
├── docs/
├── tests/
├── venv/
├── requirements.txt
└── README.md
```

## Descrição geral

A aplicação foi construída em Python, utilizando Streamlit para a interface web, Biopython para leitura de arquivos FASTA e Pandas para manipulação de tabelas.

O sistema recebe um arquivo FASTA por upload, salva temporariamente esse arquivo, realiza a leitura das sequências, calcula estatísticas básicas e compara cada sequência com um banco local em formato CSV.

O resultado final é apresentado em uma tabela com o identificador da sequência, a espécie provável e o percentual de similaridade. Também é gerado um resumo por espécie, um gráfico de barras e um arquivo CSV para download.

Fluxo da aplicação
```
Arquivo FASTA
      ↓
Upload pela interface Streamlit
      ↓
Salvamento temporário do arquivo
      ↓
Leitura com Biopython
      ↓
Extração dos identificadores e sequências
      ↓
Cálculo de estatísticas básicas
      ↓
Carregamento do banco local CSV
      ↓
Comparação por similaridade
      ↓
Identificação da espécie provável
      ↓
Exibição dos resultados
      ↓
Geração de gráfico
      ↓
Exportação em CSV
```

## Módulos desenvolvidos
## 1. src/fasta.py

- Responsável pela leitura de arquivos FASTA.

- A função principal é read_fasta(file_path), que recebe o caminho de um arquivo FASTA e retorna uma lista de dicionários contendo o identificador e a sequência de cada registro.

- Exemplo de retorno:

[
    {
        "id": "seq1",
        "sequence": "ATCGATCGATCG"
    }
]

## 2. src/stats.py

-Responsável pelo cálculo de estatísticas básicas das sequências.

-As principais informações calculadas são:

      número total de sequências;
      menor comprimento;
      maior comprimento;
      comprimento médio;
      conteúdo GC de cada sequência.

- O conteúdo GC corresponde à porcentagem de bases G e C em relação ao tamanho total da sequência.

## 3. src/similarity.py

- Responsável pelo cálculo de similaridade entre duas sequências.

- A função calculate_similarity(seq1, seq2) compara duas sequências posição por posição e calcula a porcentagem de caracteres iguais.

- Exemplo:

ATCG

ATCA

- Resultado:

75%

Esse método é simples e serve apenas como aproximação inicial. Ele não substitui algoritmos reais de alinhamento ou classificação taxonômica.

## 4. src/taxonomy.py

- Responsável pelo carregamento do banco local e pela identificação da espécie provável.

- O banco local é armazenado em:

data/reference/species_database.csv

- Formato esperado:

species,sequence
Danio rerio,ATCGATCGATCGATCG
Homo sapiens,GGGAAATTTCCCGGG
Escherichia coli,TTTTGGGGAAAACCC

- A função best_similarity_match(sequence, database) compara uma sequência de entrada com todas as sequências do banco e retorna a espécie com maior similaridade.

## 5. Interface web

- A interface foi construída com Streamlit no arquivo:

## 6. app/main.py

-Funcionalidades disponíveis:
```
upload de arquivo FASTA;
exibição de estatísticas básicas;
tabela de identificação taxonômica;
resumo por espécie;
gráfico de barras;
exportação dos resultados em CSV.
```
- Exemplo de entrada
```
>seq1
ATCGATCGATCG

>seq2
GGGAAATTTCCCGGG

>seq3
TTTTGGGGAAAACCC
```

- Exemplo de saída
```
ID	Espécie provável	Similaridade (%)
seq1	Danio rerio	100
seq2	Homo sapiens	100
seq3	Escherichia coli	100
```

### Limitações

A versão atual possui algumas limitações importantes:

- utiliza um banco local pequeno;
- não utiliza bancos biológicos reais;
- não realiza alinhamento de sequências;
- não utiliza BLAST, Kraken2, QIIME2 ou DADA2;
- não processa arquivos FASTQ;
- não considera qualidade Phred;
- não possui filtro mínimo de similaridade;
- não possui validação robusta das sequências;
- não gera relatório PDF;
- não possui testes automatizados.

## Próximos passos

Possíveis evoluções do projeto:

- adicionar validação de sequências;
- definir um limiar mínimo de similaridade;
- melhorar o algoritmo de comparação;
- adicionar sequências reais de referência;
- gerar relatório em PDF;
- salvar histórico de análises;
- integrar BLAST;
- integrar bancos como NCBI, SILVA, GTDB ou BOLD;
- adicionar testes automatizados;
- containerizar a aplicação com Docker.

## Conclusão

Este MVP estabelece a base inicial do projeto eDNA Insight. Embora ainda simplificado, o sistema já implementa o fluxo mínimo de análise: entrada de arquivo FASTA, leitura das sequências, cálculo de estatísticas, comparação com banco local e apresentação dos resultados.

A estrutura modular permite evolução incremental, mantendo separadas as responsabilidades de leitura, estatística, similaridade, classificação e interface.
