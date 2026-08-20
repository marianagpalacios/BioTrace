# 🌿 BioTrace

Plataforma educacional open source para análise reproduzível de sequências de DNA, classificação taxonômica simplificada e geração de indicadores.

**Versão estável:** `1.0.0`

O BioTrace recebe arquivos FASTA ou FASTQ, valida ou filtra as sequências, consulta um banco local por alinhamento pairwise ou BLAST, apresenta a classificação e gera evidências reproduzíveis da execução.

> **Aviso científico:** o banco incluído contém somente 10 referências de 5 espécies. Os resultados são demonstrativos e não devem ser usados isoladamente em conclusões taxonômicas, ecológicas, clínicas ou ambientais.

## Funcionalidades

- arquivos `.fasta`, `.fa`, `.fna`, `.fastq` e `.fq`;
- validação de bases e controle configurável da base ambígua `N`;
- qualidade FASTQ com Phred, trimming e filtros de comprimento;
- orientação forward/reverse complement;
- alinhamento pairwise com identidade e cobertura;
- BLAST local com identidade, cobertura, e-value e bit score;
- ranking com o melhor resultado por espécie;
- banco COI-5P curado, versionado e validado por SHA-256;
- cache de buscas dependente da configuração científica;
- manifesto de execução schema `1.4`;
- indicadores gerais, taxonômicos, de qualidade, busca e desempenho;
- relatórios JSON, CSV e Markdown;
- interface Streamlit, logs e CI em Python 3.12–3.14.

## Fluxo

```text
FASTA / FASTQ
      ↓
validação / controle de qualidade
      ↓
SearchBackend
├── alinhamento pairwise
└── BLAST local
      ↓
ranking e classificação
      ↓
indicadores e relatórios
      ↓
manifesto reproduzível
```

FASTA e FASTQ convergem para o mesmo serviço de classificação. O backend padrão é o alinhamento pairwise; BLAST é opcional e exige NCBI BLAST+ e um banco local.

## Instalação rápida

Requisitos:

- Python 3.12, 3.13 ou 3.14;
- Git;
- NCBI BLAST+ apenas para o backend BLAST.

```powershell
git clone https://github.com/marianagpalacios/BioTrace.git
cd BioTrace
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

No Linux ou macOS, ative o ambiente com `source .venv/bin/activate`.

Para desenvolvimento:

```powershell
python -m pip install -r requirements-dev.txt
python scripts\verify_project.py
```

Consulte o [guia de instalação, execução e reprodução](docs/getting_started.md) para detalhes de Windows, Linux, BLAST e solução de problemas.

## Executar

```powershell
python -m streamlit run app/main.py
```

Na interface:

1. escolha alinhamento pairwise ou BLAST local;
2. ajuste os parâmetros desejados;
3. envie um FASTA ou FASTQ;
4. acompanhe resultados, proveniência, indicadores e downloads.

Arquivos de exemplo:

- `data/examples/example_query.fasta`;
- `data/examples/example_reads.fastq`.

## Backends de busca

### Alinhamento pairwise

Usa `Biopython PairwiseAligner`, resolve a orientação da sequência e retorna score, identidade e cobertura. E-value e bit score não se aplicam e permanecem `null` nos dados (`N/A` na interface).

### BLAST local

Usa `blastn` sem interpolação de shell, com timeout e saída tabular controlada. O usuário fornece o prefixo de um banco criado com `makeblastdb`.

```powershell
blastn -version
makeblastdb -version
```

O projeto inclui scripts para construir e verificar bancos:

```powershell
python scripts\build_blast_database.py --help
python scripts\verify_blast_database.py --help
```

Bancos grandes e índices gerados não são versionados. Uma base pequena e controlada permanece em `tests/data/blast/` para testes.

## Banco de referência

O banco padrão está em `data/reference/species_database.csv`, com metadata em `data/reference/database_metadata.json`.

- marcador: COI-5P;
- escopo: Actinopterygii;
- fonte: NCBI GenBank;
- 5 espécies e 10 referências;
- duas referências por espécie;
- validação estrutural, científica e de proveniência;
- checksum SHA-256 verificado antes da classificação.

Dez referências não constituem um banco taxonômico abrangente. Consulte [Banco de referência](docs/reference_database.md).

## Reprodutibilidade e relatórios

Cada execução tenta gravar um manifesto em `runs/`, inclusive quando falha. O schema `1.4` registra entrada, banco, parâmetros, backend, ambiente, commit Git, indicadores, warnings, exports e hashes.

Para reproduzir uma execução:

```powershell
python scripts\reproduce_run.py `
  --manifest runs\<manifesto>.json `
  --input data\examples\example_query.fasta
```

O script rejeita artefatos ou configurações incompatíveis. SHA-256 detecta diferenças de bytes, mas não comprova qualidade científica.

Consulte [Reprodutibilidade](docs/reproducibility.md), [Indicadores](docs/indicators.md) e [Reporting](docs/reporting.md).

## Testes e CI

Execute a mesma porta de qualidade usada pelo GitHub Actions:

```powershell
python scripts\verify_project.py
```

Ou separadamente:

```powershell
python -m pip check
python -m pytest
python -m compileall src tests scripts app
```

A CI instala NCBI BLAST+ e executa a suíte em Ubuntu com Python 3.12, 3.13 e 3.14.

## Organização

```text
app/                  interface Streamlit
data/                 exemplos e banco curado
docs/                 documentação técnica e didática
scripts/              construção, verificação e reprodução
src/reference/        banco, curadoria e proveniência
src/search/           pairwise, BLAST, ranking e cache
src/reporting/        indicadores, warnings e exportadores
src/reproducibility/  contratos, hashing e manifestos
src/services/         orquestração dos fluxos
tests/                testes unitários e integrados
```

Detalhes estão em [Arquitetura](docs/architecture.md) e [Módulos](docs/modules.md).

## Limitações

- banco taxonômico demonstrativo e restrito;
- sem paired-end, merge R1/R2, adaptadores, primers, denoising, quimeras, ASVs ou OTUs;
- sem suporte a `FASTQ.gz`;
- cache somente em memória;
- BLAST requer instalação externa e banco local;
- ambiente não hermético e aplicação ainda não empacotada para PyPI;
- interface Streamlit depende de verificação manual além dos testes de serviço.

## Documentação

- [Primeiros passos](docs/getting_started.md)
- [Arquitetura](docs/architecture.md)
- [Módulos](docs/modules.md)
- [Roadmap](docs/roadmap.md)
- [Banco de referência](docs/reference_database.md)
- [Controle de qualidade FASTQ](docs/fastq_quality_control.md)
- [Reprodutibilidade](docs/reproducibility.md)
- [Indicadores](docs/indicators.md)
- [Reporting](docs/reporting.md)

## Licença

Distribuído sob a licença MIT. Consulte [LICENSE](LICENSE).
