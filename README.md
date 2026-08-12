# 🌿 BioTrace

> Plataforma open source para análise automatizada de DNA ambiental (eDNA), identificação taxonômica simplificada e geração de indicadores iniciais de biodiversidade.

**Versão atual:** MVP v0.4.0
**Foco da versão:** banco COI-5P curado, validação científica, proveniência e integridade verificável.

---

## Sobre o projeto

O BioTrace é um projeto incremental criado para estudar Engenharia de Software e Bioinformática por meio da construção de um pipeline simplificado de análise de sequências.

A aplicação recebe arquivos FASTA, valida as sequências, calcula estatísticas, compara cada sequência com um banco local de referência e apresenta uma classificação taxonômica simplificada.

O objetivo atual não é substituir ferramentas consolidadas, como BLAST, Kraken2, QIIME 2 ou DADA2. O projeto prioriza:

- arquitetura compreensível;
- responsabilidades bem separadas;
- código testável;
- decisões documentadas;
- evolução incremental;
- transparência sobre limitações científicas.

> **Aviso científico:** os resultados produzidos pelo MVP são demonstrativos e não devem ser usados isoladamente para conclusões taxonômicas, ecológicas, clínicas ou ambientais.

---

## Escopo do MVP v0.4.0

O MVP v0.4.0 transforma a camada de referência preparada no v0.3.0 em um conjunto científico pequeno, controlado e reproduzível.

### Entregas desta versão

- banco v1.0.0 com 10 referências COI-5P de 5 espécies de Actinopterygii;
- duas referências por espécie, obtidas do NCBI GenBank;
- accessions com versão e data de recuperação;
- curadoria apoiada pela consulta a GenBank e BOLD;
- validação científica separada da validação estrutural;
- bloqueio de bases ambíguas, comprimentos inválidos e conflitos entre espécies;
- warning auditável para duplicidade intraespecífica em *Gadus morhua*;
- metadata versionada e checksum SHA-256 do CSV;
- carregamento integrado de CSV e metadata por `ReferenceDatabase.from_files()`;
- proveniência da base exibida na interface;
- construção reprodutível do CSV, da metadata e do FASTA de exemplo.

> Dez referências não constituem um banco taxonômico abrangente. O dataset foi construído para permitir estudo controlado e reprodutível dos componentes do BioTrace.

---

## Funcionalidades

### Leitura e validação

- upload de arquivos `.fasta`, `.fa` e `.fna`;
- leitura com Biopython;
- normalização das sequências para letras maiúsculas;
- aceitação configurável da base ambígua `N`;
- identificação de sequências vazias;
- identificação de caracteres inválidos;
- separação entre registros válidos e inválidos.

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

---

## Arquitetura

```text
Interface Streamlit
        |
        v
Analysis Service
        |
        +--> FASTA Reader
        +--> Sequence Validator
        +--> Statistics
        +--> Reference Layer
        |      +--> Loader
        |      +--> Validator
        |      +--> ReferenceDatabase
        +--> Similarity
        +--> Taxonomy
        +--> Logging
```

A interface não executa as regras centrais. Ela coleta os parâmetros, chama o serviço e apresenta os resultados.

O `analysis_service.py` atua como orquestrador do caso de uso, enquanto os demais módulos mantêm responsabilidades específicas.

Mais detalhes estão em [`docs/architecture.md`](docs/architecture.md).

---

## Fluxo da análise

1. O usuário envia um arquivo FASTA.
2. A interface salva o conteúdo em um arquivo temporário.
3. O serviço lê os registros.
4. As sequências são validadas.
5. Sequências inválidas são separadas.
6. As estatísticas são calculadas para as sequências válidas.
7. O banco local é carregado.
8. O banco é validado e normalizado.
9. Cada sequência válida é comparada às referências.
10. O ranking é calculado por espécie.
11. O limiar mínimo é aplicado.
12. Os resultados são apresentados e disponibilizados para exportação.
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
│   ├── reference_database.md
│   └── learning/
│       ├── MVP0.md
│       ├── MVP1.md
│       ├── MVP2.md
│       ├── MVP3.md
│       └── fundamentos.md
├── logs/
│   └── .gitkeep
├── src/
│   ├── reference/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── curation_validator.py
│   │   ├── loader.py
│   │   ├── metadata.py
│   │   └── validator.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── analysis_service.py
│   ├── __init__.py
│   ├── config.py
│   ├── fasta.py
│   ├── logging_config.py
│   ├── similarity.py
│   ├── stats.py
│   ├── taxonomy.py
│   └── validation.py
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

O MVP foi executado durante o desenvolvimento em ambiente Windows com Python 3.14.2. A compatibilidade com outras versões deve ser validada pela futura integração contínua.

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

Execute toda a suíte:

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

No MVP v0.4.0, a suíte também cobre:

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

A suíte ainda não cobre integralmente a interface e o fluxo completo do serviço.

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
- colunas obrigatórias e opcionais.

A versão atual usa configuração em código. Arquivo externo de configuração e variáveis de ambiente podem ser introduzidos quando houver necessidade real.

---

## Documentação

- [Arquitetura](docs/architecture.md)
- [Módulos](docs/modules.md)
- [Roadmap](docs/roadmap.md)
- [Banco de referência](docs/reference_database.md)
- [Fundamentos de Bioinformática](docs/learning/fundamentos.md)
- [Registro didático do MVP v0.4.0](docs/learning/MVP3.md)

---

## Limitações atuais

- cobertura taxonômica restrita a 5 espécies e 10 referências;
- dataset inadequado para inferências taxonômicas abrangentes;
- ausência de FASTQ e escores Phred;
- ausência de complemento reverso;
- ausência de alinhamento biológico;
- ausência de BLAST;
- comparação exaustiva com todas as referências;
- ausência de manifesto completo de cada execução;
- ausência de CI;
- ausência de testes de integração completos;
- ausência de empacotamento da aplicação;
- ausência de licença formal no repositório.

---

## Próxima versão

O MVP v0.5.0 será dedicado à reprodutibilidade de cada execução, incluindo manifesto, hashes das entradas, parâmetros, integração contínua e contratos mais tipados.

Consulte [`docs/roadmap.md`](docs/roadmap.md) para o plano completo.

---

## Licença

O repositório ainda precisa de um arquivo `LICENSE` para formalizar os direitos de uso, modificação e distribuição.

Até que uma licença seja adicionada, o código é público, mas seus termos jurídicos de reutilização não estão formalmente definidos.
