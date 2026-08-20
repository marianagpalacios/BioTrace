# Arquitetura do BioTrace

## 1. Objetivo arquitetural

O BioTrace foi projetado para evoluir de forma incremental, sem antecipar a complexidade de ferramentas maduras de Bioinformática.

A arquitetura da v1.0.0 prioriza:

- responsabilidade única;
- baixo acoplamento;
- alta coesão;
- regras de negócio fora da interface;
- validação explícita;
- testabilidade;
- observabilidade;
- transparência científica;
- possibilidade de substituição futura dos componentes.

---

## 2. Visão geral

```text
                         Streamlit
                            |
                            v
              Reproducible Analysis Service
                            |
                            v
               Sequence Analysis Dispatcher
                  /                 \
                 /                   \
                v                     v
        FASTA Analysis          FASTQ Analysis
             |                       |
             v                       v
        FASTA Reader            FASTQ Reader
             |                       |
             v                       v
     Sequence Validation       Phred Quality Control
                 \                   /
                  \                 /
                   v               v
                 Valid Sequences
                       |
                       v
              Classification Service
                       |
                       v
                  SearchBackend
                 /             \
                v               v
          Pairwise          BLAST local
                 \             /
                  v           v
                 SearchHit ranking
                       |
                       v
             Reporting + Manifest
```

O `Reproducible Analysis Service` envolve a execução com proveniência, hashing e manifesto. O `Sequence Analysis Dispatcher` encaminha cada entrada para o serviço correspondente.

FASTA e FASTQ possuem etapas de entrada diferentes:

- FASTA passa pela validação de sequência;
- FASTQ passa pelo controle de qualidade Phred.

Depois dessas etapas, apenas sequências aprovadas chegam ao `Classification Service`, que centraliza estatísticas, acesso ao banco de referência, classificação e ranking. Essa separação evita duplicar a regra científica comum.

---

## 3. Camadas

### 3.1 Interface

Localização:

```text
app/main.py
```

Responsabilidades:

- receber o arquivo;
- coletar parâmetros;
- apresentar progresso;
- chamar o serviço;
- mostrar erros e avisos;
- renderizar métricas, tabelas e gráficos;
- disponibilizar exportações.

A interface não deve:

- validar diretamente o banco;
- calcular similaridade;
- classificar sequências;
- definir regras científicas;
- acessar detalhes internos do DataFrame de referência.

### 3.2 Aplicação

Localização:

```text
src/services/analysis_service.py
src/services/fastq_analysis_service.py
src/services/sequence_analysis_service.py
src/services/classification_service.py
```

Os serviços de aplicação representam os casos de uso de análise FASTA e FASTQ. O dispatcher seleciona o fluxo de entrada e ambos convergem para o núcleo compartilhado de classificação.

Ele coordena os componentes, mas não implementa seus algoritmos internos.

Responsabilidades:

1. iniciar a medição do tempo;
2. registrar o início da execução;
3. ler FASTA ou FASTQ;
4. validar sequências ou aplicar controle de qualidade;
5. calcular estatísticas;
6. carregar e validar o banco;
7. classificar as sequências;
8. montar a resposta para a interface;
9. registrar conclusão ou erro.

O wrapper em `src/services/reproducible_analysis_service.py` cria o `run_id`, mede a execução externamente, classifica seu estado e persiste o manifesto sem misturar essa responsabilidade com a análise científica.

### 3.3 Reprodutibilidade

Localização:

```text
src/reproducibility/
```

Responsabilidades:

- produzir SHA-256 de arquivos e JSON canônico;
- registrar snapshots da entrada, referência, software e ambiente;
- calcular o fingerprint determinístico;
- calcular o hash dos campos estáveis dos resultados;
- gravar e carregar manifestos JSON.

### 3.4 Domínio e utilitários científicos

Localização:

```text
src/
```

Inclui:

- leitura FASTA;
- validação das sequências;
- estatísticas;
- distância de edição;
- ranking e classificação;
- configuração;
- logging.

### 3.5 Camada de referência

Localização:

```text
src/reference/
```

A camada separa carregamento, validação estrutural, validação científica, proveniência e acesso:

```text
CSV
 ↓
loader
 ↓
structural validator
 ↓
curation validator
 ↓
metadata validator
 ↓
ReferenceDatabase
 ↓
classification
```

Essa separação permite trocar a origem dos dados no futuro sem obrigar o algoritmo taxonômico a conhecer CSV ou Pandas.

---

## 4. Fluxo detalhado

### 4.1 Entrada

A interface aceita arquivos:

- `.fasta`;
- `.fa`;
- `.fna`;
- `.fastq`;
- `.fq`.

A extensão permite ao dispatcher distinguir FASTA de FASTQ. O conteúdo enviado é gravado em um arquivo temporário com o sufixo correspondente antes de ser encaminhado ao serviço apropriado.

### 4.2 Leitura

`src/fasta.py` usa `Bio.SeqIO.parse` e transforma cada registro em:

```python
{
    "id": "identificador",
    "sequence": "ATCG..."
}
```

`src/fastq.py` também utiliza o Biopython, mas preserva os escores Phred:

```python
{
    "id": "identificador",
    "sequence": "ATCG...",
    "qualities": [30, 32, 29, 35],
}
```

O leitor FASTQ exige um escore para cada base. Registros inconsistentes geram um erro de leitura.

### 4.3 Validação das consultas

`src/validation.py` separa os registros em:

- válidos;
- inválidos.

O modo padrão aceita:

```text
A, T, C, G, N
```

O modo estrito aceita:

```text
A, T, C, G
```

Para FASTQ, `src/quality.py` executa trimming terminal, validação das bases, filtragem por comprimento e filtragem por qualidade média. O relatório preserva as métricas e os motivos de rejeição de cada read.

FASTA e FASTQ convergem para uma lista de sequências válidas antes de entrar no núcleo compartilhado de classificação.

### 4.4 Estatísticas

`src/stats.py` calcula métricas agregadas e por sequência.

O desvio padrão usado é populacional (`pstdev`), pois o arquivo analisado é tratado como o conjunto completo daquela execução.

### 4.5 Banco de referência

O loader verifica se o caminho existe e se o CSV pode ser lido.

O validador estrutural verifica e normaliza:

- colunas obrigatórias;
- linhas vazias;
- espécies sem nome;
- IDs vazios;
- IDs duplicados;
- sequências vazias;
- caracteres inválidos;
- espaços;
- letras minúsculas;
- colunas opcionais;
- possíveis inconsistências de capitalização.

O validador de curadoria aplica as regras do banco COI-5P: colunas científicas obrigatórias, accession.version, fonte, data, A/C/G/T, comprimento de 500–800 bp, duas referências por espécie e duplicidades de sequência. Duplicidade entre espécies bloqueia a base; duplicidade dentro da mesma espécie gera warning.

O validador de metadata confere versão, marcador, fonte, contagens e o SHA-256 do CSV. `ReferenceDatabase.from_files()` somente disponibiliza a base após todas essas etapas.

### 4.6 Busca e alinhamento

O backend pairwise usa alinhamento biológico para resolver orientação, identidade, cobertura e score. O backend BLAST executa `blastn` local e acrescenta e-value e bit score. Ambos retornam `SearchHit` e obedecem ao mesmo ranking normalizado.

### 4.7 Classificação

`src/taxonomy.py` e `src/search/`:

1. executam a busca no backend selecionado;
2. conserva a melhor referência de cada espécie;
3. ordena as espécies;
4. limita o ranking;
5. aplica o limiar mínimo;
6. retorna a identificação ou o rótulo de não identificada.

### 4.8 Saída

O serviço retorna um dicionário com:

- resumo;
- contagens;
- registros inválidos;
- resultados;
- rankings;
- estatísticas do banco;
- avisos;
- metadata e proveniência da base;
- tempo de execução.

---

## 4.9 Busca de referências no v0.8

```text
FASTA / FASTQ
      ↓
validação + QC
      ↓
classification_service
      ↓
SearchBackend
├── PairwiseAlignmentBackend
└── LocalBlastBackend
      ↓
SearchHit
      ↓
ranking
      ↓
classificação
      ↓
reprodutibilidade
```

A camada `src/search/` separa o contrato de busca das implementações concretas:

- `src/search/contracts.py` define os contratos comuns;
- `src/search/pairwise_backend.py` adapta o alinhamento introduzido no v0.7;
- `src/search/blast_backend.py` executa o `blastn` local com timeout e erros de domínio;
- `src/search/blast_parser.py` interpreta a saída tabular e ordena os hits;
- `src/search/cache.py` gera chaves reproduzíveis e mantém o cache de busca em memória;
- `src/search/factory.py` seleciona o backend pairwise ou BLAST.

Essa separação permite que FASTA e FASTQ compartilhem a mesma classificação normalizada sem conhecer os detalhes de execução de cada mecanismo.

## 5. Decisões arquiteturais

### ADR-001 — Manter Streamlit apenas como interface

**Decisão:** regras de negócio ficam em `src/`.

**Benefício:** testes não dependem da interface.

**Trade-off:** ainda existe alguma transformação de DataFrames em `app/main.py`, aceitável no MVP.

### ADR-002 — Usar um serviço orquestrador

**Decisão:** `analysis_service.py` coordena o fluxo.

**Benefício:** existe um ponto central para o caso de uso.

**Trade-off:** o serviço pode crescer. Se novos casos de uso surgirem, será necessário dividi-lo.

### ADR-003 — Separar loader, validator e database

**Decisão:** leitura, qualidade e acesso ao banco são responsabilidades independentes.

**Benefício:** prepara a troca do CSV por outra origem.

**Trade-off:** cria mais arquivos e conceitos do que um script único.

### ADR-004 — Erros bloqueantes e avisos

**Decisão:** inconsistências estruturais interrompem a análise; normalizações seguras geram avisos.

**Benefício:** evita descarte silencioso de dados.

**Trade-off:** bancos imperfeitos exigem correção antes da execução.

### ADR-005 — Backends intercambiáveis

**Decisão:** preservar alinhamento pairwise e BLAST local sob o contrato `SearchBackend`.

**Benefício:** FASTA e FASTQ compartilham classificação e resultados normalizados.

**Trade-off:** BLAST exige executável e banco externos; o pairwise não escala para bancos grandes.

### ADR-006 — Configuração em Python

**Decisão:** valores padrão ficam em `src/config.py`.

**Benefício:** solução simples e tipável.

**Trade-off:** mudanças exigem alteração de código. Configuração externa será considerada quando houver ambientes distintos.

### ADR-007 — Logging padrão do Python

**Decisão:** usar `logging` e `RotatingFileHandler`.

**Benefício:** sem dependência adicional e com rotação.

**Trade-off:** não há estrutura JSON, correlação distribuída ou agregação centralizada.

### ADR-008 — DataFrame encapsulado

**Decisão:** módulos externos usam métodos de `ReferenceDatabase`.

**Benefício:** reduz dependência direta de Pandas.

**Trade-off:** novos tipos de consulta exigem métodos explícitos.

### ADR-009 — Banco real adiado

**Decisão:** a arquitetura de referência entra no v0.3.0; a curadoria científica entra no v0.4.0.

**Benefício:** separa Engenharia de Software de curadoria de dados, permitindo revisar cada tema com profundidade.

**Trade-off:** a classificação do v0.3.0 permanece apenas demonstrativa.

### ADR-010 — Dataset e software possuem versões independentes

**Decisão:** o software usa v0.4.0 e o banco curado usa v1.0.0.

**Benefício:** o banco pode evoluir sem exigir a mesma numeração do aplicativo.

### ADR-011 — Integridade por SHA-256

**Decisão:** a metadata armazena o hash do CSV e ele é verificado antes da classificação.

**Benefício:** alterações acidentais ou não documentadas no banco são detectadas.

### ADR-012 — Wrapper reproduzível separado

**Decisão:** manter proveniência em um serviço externo ao serviço científico.

**Benefício:** a análise permanece testável e independente da persistência de manifestos.

### ADR-013 — Run ID e fingerprint são conceitos diferentes

**Decisão:** UUID identifica uma ocorrência; SHA-256 identifica as condições determinísticas.

**Benefício:** execuções distintas podem ser reconhecidas como equivalentes sem perder identidade individual.

---

## 6. Tratamento de falhas

### Falhas de entrada

- FASTA sem registros: `AnalysisError`;
- todas as sequências inválidas: resposta sem classificação;
- registros parcialmente inválidos: válidos continuam, inválidos são relatados.

### Falhas do banco

- arquivo inexistente;
- caminho que não é arquivo;
- CSV vazio;
- CSV malformado;
- colunas ausentes;
- conteúdo inválido.
- violação das regras científicas;
- metadata ausente ou inválida;
- checksum ou contagens incompatíveis.

Essas falhas são convertidas em mensagens compreensíveis para a interface.

### Falhas inesperadas

A interface possui tratamento genérico para impedir que a aplicação encerre sem retorno ao usuário. Em versões futuras, exceções internas devem ser classificadas com mais precisão.

---

## 7. Testabilidade

A suíte atual cobre funções e componentes isolados:

- parser FASTA;
- validação;
- loader;
- validator;
- banco;
- similaridade;
- classificação;
- estatísticas;
- logging.

Lacunas:

- teste automatizado da interface Streamlit;
- benchmark formal com arquivos e bancos grandes;
- ambiente hermético ou imagem de container.

---

## 8. Pontos de extensão

A arquitetura já permite:

- substituir o CSV por outra fonte dentro da camada de referência;
- adicionar novos backends por meio do contrato `SearchBackend`;
- criar novos exportadores;
- adicionar manifesto de execução;
- criar uma CLI;
- introduzir modelos tipados para respostas;
- ampliar bancos BLAST mantendo índices e proveniência versionados;
- adicionar FASTQ antes da validação taxonômica.

---

## 9. Limitações arquiteturais

- contratos baseados em dicionários;
- ausência de interface formal para algoritmos de similaridade;
- ausência de injeção explícita de dependências;
- serviço principal ainda retorna estrutura ampla;
- logging global configurado no import;
- CI limitada a testes, dependências e compilação, sem empacotamento ou implantação;
- ausência de empacotamento;
- ausência de versionamento formal do esquema do banco, embora o conteúdo já possua versão e checksum.

Essas limitações são aceitáveis no MVP e devem ser atacadas apenas quando houver necessidade concreta.
