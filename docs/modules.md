# Módulos do BioTrace

Este documento descreve as responsabilidades dos módulos do MVP v0.4.0.

---

## `app/main.py`

### Responsabilidade

Interface web construída com Streamlit.

### Entradas

- arquivo FASTA;
- limiar mínimo;
- permissão da base `N`;
- quantidade máxima de resultados.

### Saídas

- mensagens;
- métricas;
- tabelas;
- gráfico;
- arquivos CSV.

### Dependências

- `streamlit`;
- `pandas`;
- `src.config`;
- `src.services.analysis_service`.

### Observação

Não deve concentrar regras científicas.

---

## `src/config.py`

### Responsabilidade

Centralizar parâmetros e caminhos padrão.

### Valores principais

- raiz do projeto;
- caminho do banco;
- caminho da metadata do banco;
- caminho do log;
- limiar padrão;
- limites do slider;
- aceitação de `N`;
- tamanho do ranking;
- colunas do banco;
- bases válidas.
- regras COI-5P, limites de comprimento e mínimo por espécie.

### Trade-off

É simples e suficiente para um único ambiente. Configuração externa pode ser adicionada quando existirem necessidades de implantação distintas.

---

## `src/fasta.py`

### Responsabilidade

Ler arquivos FASTA com Biopython.

### Função

```python
read_fasta(file_path: str) -> list[SequenceRecord]
```

### Contrato

Retorna:

```python
[
    {
        "id": "seq_1",
        "sequence": "ATCG"
    }
]
```

### Limitação

Não valida o alfabeto. Essa função pertence a `validation.py`.

---

## `src/validation.py`

### Responsabilidade

Validar as sequências de consulta.

### Funções

- `get_valid_bases`;
- `find_invalid_bases`;
- `validate_sequences`.

### Regras

Modo flexível:

```text
A, T, C, G, N
```

Modo estrito:

```text
A, T, C, G
```

### Saída

Uma tupla com:

- sequências válidas;
- detalhes das sequências inválidas.

---

## `src/stats.py`

### Responsabilidade

Calcular estatísticas descritivas e composição nucleotídica.

### Funções

- `sequence_length`;
- `nucleotide_frequency`;
- `gc_content`;
- `at_content`;
- `sequence_composition`;
- `summarize_sequences`.

### Métricas

- comprimento;
- média;
- mediana;
- desvio padrão populacional;
- A%, T%, C%, G%;
- AT%;
- GC%;
- quantidade de `N`.

### Observação

Quando há `N`, A + T + C + G pode ser menor que 100%, pois o denominador continua sendo o comprimento completo.

---

## `src/similarity.py`

### Responsabilidade

Calcular distância e similaridade.

### Funções

```python
edit_distance(seq1: str, seq2: str) -> int
```

```python
calculate_similarity(seq1: str, seq2: str) -> float
```

### Estratégia

Distância de Levenshtein com memória otimizada por linhas.

### Complexidade

- tempo: `O(n × m)`;
- memória: `O(min(n, m))`.

### Limitação

Não realiza alinhamento biológico.

---

## `src/taxonomy.py`

### Responsabilidade

Construir ranking e aplicar a regra de classificação.

### Funções

- `exact_match`;
- `rank_similarity_matches`;
- `classify_sequence`;
- `best_similarity_match`.

### Regras

- cada espécie aparece uma vez no ranking;
- a melhor referência da espécie é mantida;
- o limiar é aplicado somente após o ranking;
- resultado abaixo do limiar recebe `Espécie não identificada`.

### Dependências

- `ReferenceDatabase`;
- `calculate_similarity`.

---

## `src/logging_config.py`

### Responsabilidade

Configurar o logger do projeto.

### Função

```python
configure_logging(log_file=LOG_FILE_PATH) -> logging.Logger
```

### Características

- nível `INFO`;
- codificação UTF-8;
- rotação por tamanho;
- até três backups;
- prevenção de handlers duplicados para o mesmo arquivo.

---

# Camada de referência

## `src/reference/loader.py`

### Responsabilidade

Ler o CSV sem aplicar regras biológicas.

### Função

```python
load_reference_csv(file_path) -> pandas.DataFrame
```

### Exceção

```python
ReferenceDatabaseLoadError
```

### Falhas tratadas

- arquivo inexistente;
- caminho inválido;
- CSV vazio;
- CSV malformado;
- erro de acesso.

---

## `src/reference/validator.py`

### Responsabilidade

Validar e normalizar o DataFrame de referência.

### Tipos

```python
ReferenceValidationResult
```

```python
ReferenceDatabaseValidationError
```

### Erros bloqueantes

- colunas obrigatórias ausentes;
- linha vazia;
- espécie ausente;
- ID ausente;
- ID duplicado;
- sequência vazia;
- caractere inválido.

### Avisos

- espaços externos removidos;
- espaços internos removidos da sequência;
- minúsculas convertidas;
- colunas opcionais ausentes;
- capitalização possivelmente inconsistente.

### Decisão

Normalizações determinísticas são permitidas. Inconsistências que mudariam o significado interrompem a análise.

---

## `src/reference/database.py`

### Responsabilidade

Representar um banco carregado e validado.

### Classe

```python
ReferenceDatabase
```

### Métodos

- `from_csv`;
- `from_files`;
- `iter_records`;
- `find_by_species`;
- `list_species`;
- `list_ids`;
- `statistics`.

### Encapsulamento

O DataFrame interno não é exposto diretamente.

`from_csv` mantém compatibilidade com bases genéricas. `from_files` carrega o CSV curado, aplica as duas validações, confere a metadata e expõe sua proveniência.

---

## `src/reference/curation_validator.py`

### Responsabilidade

Aplicar as regras científicas específicas da base BioTrace sem tornar o validador estrutural dependente de COI-5P.

### Regras principais

- nome binomial e accession.version;
- gene COI, região COI-5P e fonte NCBI GenBank;
- data ISO não futura;
- somente A/C/G/T e comprimento de 500–800 bp;
- mínimo de duas referências por espécie;
- sequência idêntica entre espécies como erro;
- sequência idêntica dentro da espécie como warning.

---

## `src/reference/metadata.py`

### Responsabilidade

Carregar e validar a proveniência versionada e a integridade do banco.

### Componentes

- `ReferenceDatabaseMetadata`;
- `ReferenceMetadataError`;
- cálculo SHA-256;
- validação de versão, data, marcador, fonte e contagens;
- comparação do checksum com o CSV atual.

---

# Scripts reproduzíveis

## `scripts/build_curated_reference_csv.py`

Constrói `species_database.csv` a partir do FASTA baixado, associa cada accession à espécie e ao ID interno e executa as validações antes da escrita.

## `scripts/generate_reference_metadata.py`

Valida o banco e gera `database_metadata.json` com versão, escopo, fonte, contagens, data e SHA-256.

## `scripts/generate_example_fasta.py`

Gera `data/examples/example_query.fasta` diretamente de uma referência curada, evitando cópia manual e mantendo o exemplo reproduzível.

---

# Serviço

## `src/services/analysis_service.py`

### Responsabilidade

Orquestrar o caso de uso completo.

### Tipos

```python
ProgressCallback
```

```python
AnalysisError
```

### Função principal

```python
analyze_fasta_file(...)
```

### Etapas coordenadas

1. logging;
2. leitura;
3. validação;
4. estatísticas;
5. carregamento do banco;
6. classificação;
7. montagem da resposta;
8. medição de tempo.

### Retorno

O dicionário contém:

- `summary`;
- `total_sequences`;
- `valid_count`;
- `invalid_count`;
- `invalid_sequences`;
- `results`;
- `rankings`;
- `reference_statistics`;
- `reference_warnings`;
- `reference_metadata`;
- `execution_time_seconds`.

### Limitação

O contrato ainda é um dicionário amplo. Modelos tipados são recomendados para uma versão futura.

---

# Testes

## `tests/conftest.py`

Fixtures compartilhadas, incluindo FASTA temporário.

## `tests/test_fasta.py`

Leitura e arquivo vazio.

## `tests/test_validation.py`

Bases inválidas, normalização, modo estrito e sequência vazia.

## `tests/test_similarity.py`

Igualdade, substituição, inserção, deleção, comprimentos diferentes, vazio e capitalização.

## `tests/test_stats.py`

Composição, mediana, desvio padrão e coleção vazia.

## `tests/test_taxonomy.py`

Melhor referência e limiar.

## `tests/test_logging_config.py`

Criação e gravação do log.

## `tests/reference/`

Carregamento, validação e consultas do banco.
