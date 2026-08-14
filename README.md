# 🌿 BioTrace

> Plataforma open source para análise automatizada de DNA ambiental (eDNA), identificação taxonômica simplificada e geração de indicadores iniciais de biodiversidade.

**Versão em desenvolvimento:** MVP v0.6.0
**Foco da versão:** leitura FASTQ, controle de qualidade Phred, trimming terminal e reprodutibilidade dos parâmetros de QC.

---

## Sobre o projeto

O BioTrace é um projeto incremental criado para estudar Engenharia de Software e Bioinformática por meio da construção de um pipeline simplificado de análise de sequências.

A aplicação recebe arquivos FASTA ou FASTQ, valida as sequências ou aplica controle de qualidade, calcula estatísticas, compara os registros aprovados com um banco local de referência e apresenta uma classificação taxonômica simplificada.

O objetivo atual não é substituir ferramentas consolidadas, como BLAST, Kraken2, QIIME 2 ou DADA2. O projeto prioriza:

- arquitetura compreensível;
- responsabilidades bem separadas;
- código testável;
- decisões documentadas;
- evolução incremental;
- transparência sobre limitações científicas.

> **Aviso científico:** os resultados produzidos pelo MVP são demonstrativos e não devem ser usados isoladamente para conclusões taxonômicas, ecológicas, clínicas ou ambientais.

---

## Escopo do MVP v0.6.0

O MVP v0.6.0 aproxima a entrada do BioTrace de dados de sequenciamento ao adicionar FASTQ e controle de qualidade Phred, preservando a análise FASTA e a proveniência introduzida no v0.5.0.

### Entregas desta versão

- leitura de `.fastq` e `.fq` com escores Phred;
- métricas de qualidade média, Q20 e Q30;
- trimming de baixa qualidade nas extremidades 5' e 3';
- filtragem por comprimento e qualidade média;
- relatório auditável de reads aprovados e rejeitados;
- download do relatório de QC em CSV;
- classificação dos reads aprovados pelo banco COI-5P;
- manifesto schema `1.1` com formato e parâmetros de QC;
- fingerprint e hash dos resultados sensíveis ao controle de qualidade;
- reprodução de execuções FASTA e FASTQ;
- exemplo FASTQ determinístico e testes automatizados;
- controles e métricas FASTQ na interface Streamlit.

> Dez referências não constituem um banco taxonômico abrangente. O dataset foi construído para permitir estudo controlado e reprodutível dos componentes do BioTrace.

---

## Funcionalidades

### Leitura e validação

- upload de arquivos `.fasta`, `.fa`, `.fna`, `.fastq` e `.fq`;
- leitura com Biopython;
- leitura dos escores Phred em FASTQ;
- validação da correspondência entre sequência e qualidades;
- dispatcher automático entre FASTA e FASTQ;
- normalização das sequências para letras maiúsculas;
- aceitação configurável da base ambígua `N`;
- identificação de sequências vazias;
- identificação de caracteres inválidos;
- separação entre registros válidos e inválidos.

### Controle de qualidade FASTQ

- trimming de baixa qualidade nas extremidades 5' e 3';
- Phred médio por read;
- percentuais Q20 e Q30;
- filtragem por comprimento;
- filtragem por qualidade média;
- relatório auditável de aprovados e rejeitados;
- download do relatório em CSV;
- parâmetros registrados no manifesto.

### Estatísticas

Para o conjunto analisado:

- quantidade de sequências;
- comprimento mínimo;
- comprimento máximo;
- comprimento médio;
- mediana do comprimento;
- desvio padrão populacional do comprimento;
- frequência agregada de A, T, C e G;
- porcentagem AT;
- porcentagem GC.

Para cada sequência:

- comprimento;
- frequência de A, T, C e G;
- porcentagem AT;
- porcentagem GC;
- quantidade de bases `N`.

### Similaridade e classificação

- distância de edição de Levenshtein;
- similaridade normalizada entre 0% e 100%;
- tratamento de substituições;
- tratamento de inserções e deleções simples;
- limiar mínimo configurável;
- melhor referência por espécie;
- ranking configurável;
- retorno de `Espécie não identificada` quando o limiar não é alcançado.

### Banco de referência

- carregamento isolado em `src/reference/loader.py`;
- validação isolada em `src/reference/validator.py`;
- acesso encapsulado em `src/reference/database.py`;
- validação de colunas obrigatórias;
- detecção de IDs duplicados;
- detecção de espécies sem nome;
- detecção de sequências vazias;
- detecção de caracteres inválidos;
- normalização auditável de espaços e minúsculas;
- listagem de espécies e IDs;
- estatísticas básicas do banco.
- regras científicas para COI/COI-5P, A/C/G/T e 500–800 bp;
- mínimo de duas referências por espécie;
- validação de accession.version, fonte e data;
- metadata da base v1.0.0;
- verificação de contagens e SHA-256 antes da classificação;
- distinção entre duplicidade intraespecífica (warning) e interespecífica (erro).

### Observabilidade

- registro do início e fim da análise;
- quantidade de sequências recebidas;
- IDs de sequências inválidas;
- erros de carregamento ou validação do banco;
- avisos de normalização;
- tempo de execução;
- rotação automática dos arquivos de log.

### Reprodutibilidade

- manifesto JSON persistido em `runs/`;
- schema `1.1` com formato da entrada e parâmetros de QC;
- estados `completed`, `stopped` e `failed`;
- timestamps UTC e duração;
- hash da entrada, da referência, da metadata e dos resultados;
- fingerprint das condições científicas e computacionais;
- identificação do commit e do ambiente Python;
- reprodução de execuções FASTA e FASTQ;
- inclusão do resumo e relatório de QC no hash dos resultados;
- JSONs de execução ignorados pelo Git.

### Interface e exportação

- barra de progresso;
- métricas gerais;
- composição nucleotídica;
- tabela de métricas por sequência;
- tabela de identificação taxonômica;
- ranking por sequência;
- gráfico de contagem por espécie;
- resumo do banco de referência;
- exportação dos resultados em CSV;
- exportação das estatísticas em CSV;
- exportação do ranking em CSV.
- painel de reprodutibilidade da execução;
- download do manifesto JSON.
- controles de qualidade FASTQ;
- métricas e relatório por read;
- download do relatório de QC em CSV.

---

## Arquitetura

```text
Interface Streamlit
        |
        v
Reproducible Analysis Service
        |
        +--> Run Manifest
        |
        v
Sequence Analysis Dispatcher
        |
        +--> FASTA Analysis
        |      +--> FASTA Reader
        |      +--> Sequence Validation
        |
        +--> FASTQ Analysis
               +--> FASTQ Reader
               +--> Phred Quality Control
        |
        v
Classification Service
        +--> Statistics
        +--> ReferenceDatabase
        +--> Similarity
        +--> Taxonomy
```

A interface não executa as regras centrais. Ela coleta os parâmetros, chama o serviço e apresenta os resultados.

O dispatcher seleciona o serviço de entrada. FASTA e FASTQ convergem para o mesmo núcleo de classificação depois da validação ou do controle de qualidade.

Mais detalhes estão em [`docs/architecture.md`](docs/architecture.md).

---

## Fluxo da análise

1. O usuário envia um arquivo FASTA ou FASTQ.
2. A interface detecta o formato e salva o conteúdo temporariamente.
3. O dispatcher seleciona o serviço correspondente.
4. FASTA passa por validação; FASTQ passa por trimming e controle de qualidade Phred.
5. Registros rejeitados são separados e documentados.
6. As estatísticas são calculadas para as sequências aprovadas.
7. O banco local é carregado e validado.
8. Cada sequência aprovada é comparada às referências.
9. O ranking e a classificação são calculados.
10. O wrapper registra hashes, parâmetros, software e ambiente.
11. Um manifesto com status e hash dos resultados é persistido.
12. Resultados, proveniência e relatório de QC são disponibilizados para download.
13. Eventos relevantes são registrados no log.

---

## Algoritmo de similaridade

A similaridade é calculada a partir da distância de edição:

```text
similaridade = (1 - distância / maior_comprimento) × 100
```

A distância representa a menor quantidade de operações necessárias para transformar uma sequência na outra:

- inserção;
- deleção;
- substituição.

### Limitações

Esse método é mais robusto que a comparação posição a posição, mas não é um alinhamento biológico completo.

Ele não possui:

- penalidade diferenciada para abertura e extensão de gaps;
- matriz de substituição;
- alinhamento local;
- traceback;
- complemento reverso automático;
- modelo de evolução molecular;
- otimização para bancos grandes.

Por isso, a pontuação deve ser interpretada como uma medida computacional didática.

---

## Banco de referência curado

O arquivo padrão está em:

```text
data/reference/species_database.csv
```

O banco v1.0.0 contém 10 referências de 5 espécies de Actinopterygii, com duas referências por espécie. O marcador é COI-5P e a fonte registrada é NCBI GenBank.

As colunas da base curada são:

| Coluna | Descrição |
|---|---|
| `species` | Nome da espécie |
| `id` | Identificador único da referência |
| `sequence` | Sequência contendo somente A/C/G/T, entre 500 e 800 bp |
| `gene` | Gene ou marcador |
| `marker_region` | Região do marcador (`COI-5P`) |
| `accession` | Identificador no banco de origem |
| `source` | Fonte do registro |
| `retrieved_at` | Data de recuperação em formato ISO |

`data/reference/database_metadata.json` registra versão, escopo, contagens, fonte, data e SHA-256. Consulte [a documentação científica da base](docs/reference_database.md) e [o inventário da pasta](data/reference/README.md).

---

## Estrutura do projeto

```text
BioTrace/
├── app/
│   └── main.py
├── data/
│   ├── examples/
│   │   └── sample.fasta
│   └── reference/
│       ├── README.md
│       ├── accessions.txt
│       ├── database_metadata.json
│       └── species_database.csv
├── docs/
│   ├── architecture.md
│   ├── modules.md
│   ├── roadmap.md
│   ├── reproducibility.md
│   ├── reference_database.md
│   └── learning/
│       ├── MVP0.md
│       ├── MVP1.md
│       ├── MVP2.md
│       ├── MVP3.md
│       ├── MVP4.md
│       └── fundamentos.md
├── logs/
│   └── .gitkeep
├── runs/
│   └── .gitkeep
├── src/
│   ├── reproducibility/
│   │   ├── contracts.py
│   │   ├── hashing.py
│   │   └── manifest.py
│   ├── reference/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── curation_validator.py
│   │   ├── loader.py
│   │   ├── metadata.py
│   │   └── validator.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── analysis_service.py
│   │   └── reproducible_analysis_service.py
│   ├── __init__.py
│   ├── config.py
│   ├── contracts.py
│   ├── fasta.py
│   ├── logging_config.py
│   ├── similarity.py
│   ├── stats.py
│   ├── taxonomy.py
│   ├── validation.py
│   └── version.py
├── tests/
│   ├── reference/
│   │   ├── test_database.py
│   │   ├── test_loader.py
│   │   └── test_validator.py
│   ├── conftest.py
│   ├── test_fasta.py
│   ├── test_logging_config.py
│   ├── test_similarity.py
│   ├── test_stats.py
│   ├── test_taxonomy.py
│   └── test_validation.py
├── .gitignore
├── pytest.ini
├── requirements-dev.txt
├── requirements.txt
└── README.md
```

---

## Requisitos

- Python 3;
- Git;
- ambiente virtual recomendado.

O MVP é desenvolvido localmente em Windows com Python 3.14.2. A integração contínua verifica também Python 3.12 e 3.13 em Ubuntu.

---

## Instalação

### 1. Clonar o repositório

```bash
git clone https://github.com/marianagpalacios/BioTrace.git
cd BioTrace
```

### 2. Criar o ambiente virtual

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Linux ou macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar as dependências da aplicação

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Para desenvolvimento e testes:

```bash
python -m pip install -r requirements-dev.txt
```

---

## Execução

```bash
python -m streamlit run app/main.py
```

Depois, abra o endereço indicado pelo Streamlit no navegador.

Um arquivo de exemplo está disponível em:

```text
data/examples/example_query.fasta
```

---

## Testes

Execute a porta de qualidade usada localmente e na CI:

```bash
python scripts/verify_project.py
```

Ou execute apenas a suíte:

```bash
python -m pytest
```

Execute um arquivo específico:

```bash
python -m pytest tests/test_similarity.py -v
```

Valide a compilação:

```bash
python -m compileall app src scripts
```

No MVP v0.6.0, a suíte também cobre:

- leitura FASTA;
- validação de sequências;
- carregamento do banco;
- validação do banco;
- abstração do banco;
- similaridade;
- classificação;
- estatísticas;
- logging.
- regras de curadoria científica;
- integridade do dataset real;
- metadata e checksum;
- carregamento versionado do banco.
- hashing canônico;
- construção e persistência do manifesto;
- fingerprint determinístico;
- execução integrada concluída e com falha.
- leitura FASTQ e escores Phred;
- trimming terminal e filtros de qualidade;
- métricas Q20 e Q30;
- integração FASTQ com classificação;
- parâmetros FASTQ no manifesto;
- reprodução de execução FASTQ.

A interface ainda depende de teste manual, mas o fluxo completo do serviço reproduzível possui cobertura de integração.

O GitHub Actions executa a mesma verificação em Python 3.12, 3.13 e 3.14.

---

## Logs

O arquivo padrão é:

```text
logs/biotrace.log
```

Os arquivos `.log` são ignorados pelo Git. Apenas `logs/.gitkeep` é versionado.

O logger usa rotação, evitando crescimento indefinido do arquivo.

---

## Configuração

Os valores padrão estão centralizados em:

```text
src/config.py
```

Entre eles:

- caminho do banco;
- caminho do log;
- limiar padrão;
- aceitação da base `N`;
- quantidade padrão do ranking;
- qualidade Phred média mínima;
- comprimentos mínimo e máximo após QC;
- ativação e limiar do trimming terminal;
- colunas obrigatórias e opcionais.

A versão atual usa configuração em código. Arquivo externo de configuração e variáveis de ambiente podem ser introduzidos quando houver necessidade real.

---

## Documentação

- [Arquitetura](docs/architecture.md)
- [Módulos](docs/modules.md)
- [Roadmap](docs/roadmap.md)
- [Banco de referência](docs/reference_database.md)
- [Reprodutibilidade](docs/reproducibility.md)
- [Controle de qualidade FASTQ](docs/fastq_quality_control.md)
- [Fundamentos de Bioinformática](docs/learning/fundamentos.md)
- [Registro didático do MVP v0.4.0](docs/learning/MVP3.md)
- [Registro didático do MVP v0.5.0](docs/learning/MVP4.md)
- [Registro didático do MVP v0.6.0](docs/learning/MVP5.md)

---

## Limitações atuais

- cobertura taxonômica restrita a 5 espécies e 10 referências;
- dataset inadequado para inferências taxonômicas abrangentes;
- ausência de paired-end e merge R1/R2;
- ausência de trimming de adaptadores e primers;
- ausência de denoising e remoção de quimeras;
- ausência de inferência de ASVs e agrupamento em OTUs;
- ausência de suporte a `FASTQ.gz`;
- ausência de complemento reverso;
- ausência de orientação automática;
- ausência de alinhamento biológico;
- ausência de BLAST;
- comparação exaustiva com todas as referências;
- ausência de ambiente hermético ou container versionado;
- dependências nativas e detalhes do sistema ainda podem afetar reproduções;
- reprodução depende da disponibilidade dos artefatos originais;
- ausência de empacotamento da aplicação;
- ausência de licença formal no repositório.

---

## Próxima versão

Após o fechamento do v0.6.0, o MVP v0.7.0 será dedicado à orientação de sequências e ao alinhamento biológico.

Consulte [`docs/roadmap.md`](docs/roadmap.md) para o plano completo.

---

## Licença

O repositório ainda precisa de um arquivo `LICENSE` para formalizar os direitos de uso, modificação e distribuição.

Até que uma licença seja adicionada, o código é público, mas seus termos jurídicos de reutilização não estão formalmente definidos.
