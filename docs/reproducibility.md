# Reprodutibilidade no BioTrace

## Objetivo

O BioTrace registra a proveniência de execuções FASTA e FASTQ, incluindo qualidade, busca, reporting e ambiente computacional.

## Run ID

`run_id` é um UUID que identifica uma execução específica. Ele muda em toda execução, mesmo quando entrada, parâmetros e resultados são iguais.

## Run fingerprint

`run_fingerprint` é um SHA-256 calculado a partir de:

- hash do arquivo de entrada FASTA ou FASTQ;
- formato da entrada;
- hash do banco de referência;
- hash da metadata;
- parâmetros;
- parâmetros de controle de qualidade FASTQ;
- versão do BioTrace;
- commit Git;
- versão do esquema do manifesto.

Duas execuções equivalentes devem produzir o mesmo fingerprint, embora tenham `run_id` diferentes.

## Manifesto

Cada execução registra:

- versão do esquema;
- run ID e fingerprint;
- timestamps UTC e duração;
- status;
- nome, tamanho e SHA-256 da entrada;
- banco e metadata de referência;
- parâmetros;
- software e commit Git;
- ambiente Python e plataforma;
- contagens;
- hash dos resultados;
- erro, quando existente.

Os manifestos são gravados em `runs/`. Apenas `runs/.gitkeep` é versionado; os JSONs são artefatos locais da execução.

## Versão do schema

A v1.0.0 utiliza o schema `1.4`.

```text
schema 1.0
→ manifesto FASTA do MVP v0.5

schema 1.1
→ formato da entrada
→ parâmetros FASTQ
→ resumo e relatório de QC no hash dos resultados

schema 1.2
→ orientação e alinhamento

schema 1.3
→ backend, BLAST, banco, timeout e cache

schema 1.4
→ indicadores, warnings, exports e duração da análise
```

O script de reprodução recusa manifestos de schema incompatível e orienta o uso da versão do BioTrace registrada na execução.

## Parâmetros por formato

Parâmetros compartilhados:

- `min_similarity`;
- `allow_n`;
- `top_n`.

Para FASTQ, o manifesto também registra:

- `min_mean_quality`;
- `min_length`;
- `max_length`;
- `trim_ends`;
- `trim_quality_threshold`.

Em execuções FASTA, os campos exclusivos de FASTQ são registrados como `null`.

## Estados

### `completed`

A análise terminou com uma ou mais sequências válidas.

### `stopped`

A execução terminou de forma controlada sem sequência válida para classificar.

### `failed`

O pipeline encontrou um erro que impediu a conclusão. O wrapper tenta persistir um manifesto com a classe e a mensagem da exceção.

## SHA-256

Hashes são usados para detectar alterações nos artefatos. O hash dos resultados considera apenas campos científicos estáveis e exclui valores voláteis como UUID, timestamps e duração.

O hash dos resultados também considera:

- `input_format`;
- `quality_summary`;
- `quality_report`.

Assim, mudanças nas métricas ou decisões do controle de qualidade são detectadas na reprodução.

SHA-256 comprova igualdade de bytes, não qualidade científica. Curadoria, validação e checksum resolvem problemas diferentes.

Arquivos científicos versionados usam finais de linha LF para que seus bytes sejam estáveis entre Windows e Linux.

## Git

O manifesto registra:

- commit atual;
- working tree dirty ou clean.

Execuções produzidas com alterações não commitadas recebem `git_dirty: true` e não possuem a mesma garantia de reprodução. O comando de reprodução recusa manifestos originais gerados com árvore suja.

## Reproduzindo uma execução

Com a mesma entrada, banco, metadata, código, parâmetros e working tree limpa:

```powershell
python scripts\reproduce_run.py `
  --manifest runs\<manifest>.json `
  --input data\examples\example_query.fasta
```

Para reproduzir uma execução FASTQ:

```powershell
python scripts\reproduce_run.py `
  --manifest runs\<manifest-fastq>.json `
  --input data\examples\example_reads.fastq
```

O script lê `parameters.input_format` e reaplica os parâmetros de qualidade registrados no manifesto.

O comando verifica os hashes dos artefatos, reutiliza os parâmetros, executa novamente o pipeline e compara fingerprint e hash dos resultados.

Saída esperada:

```text
REPRODUCTION OK
Original run: ...
New run: ...
Fingerprint: ...
```

## Verificação e CI

Execute localmente:

```powershell
python scripts\verify_project.py
```

O mesmo comando é executado pelo GitHub Actions em Python 3.12, 3.13 e 3.14.

## Busca de referências no schema 1.3

A partir do MVP v0.8.0, o manifesto registra também a configuração do mecanismo de busca.

São registrados:

- backend selecionado (`pairwise` ou `blast`);
- timeout;
- versão do NCBI BLAST+;
- caminho lógico do banco BLAST;
- SHA-256 do banco;
- estado do cache;
- parâmetros de alinhamento anteriores;
- resultados com identidade e cobertura;
- e-value e bit score quando disponíveis.

O script `reproduce_run.py` rejeita reproduções quando a configuração registrada não corresponde à configuração atual.

## Limitações

O MVP não cria ambientes herméticos completos. Versões do sistema operacional, bibliotecas nativas, arquitetura do processador e dependências externas ainda podem afetar determinadas execuções.

O manifesto não incorpora o arquivo FASTA ou FASTQ nem o banco de referência. Esses artefatos precisam continuar disponíveis e corresponder aos hashes registrados.

A reprodução verifica igualdade computacional dentro das condições registradas. Ela não comprova validade taxonômica, qualidade experimental ou adequação científica do protocolo.
