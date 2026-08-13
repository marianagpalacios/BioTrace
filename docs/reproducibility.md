# Reprodutibilidade no BioTrace

## Objetivo

O MVP v0.5.0 introduz rastreabilidade para cada execução do BioTrace. O objetivo é registrar as condições científicas e computacionais, detectar alterações nos artefatos e verificar se uma nova execução produz o mesmo resultado.

## Run ID

`run_id` é um UUID que identifica uma execução específica. Ele muda em toda execução, mesmo quando entrada, parâmetros e resultados são iguais.

## Run fingerprint

`run_fingerprint` é um SHA-256 calculado a partir de:

- hash do FASTA;
- hash do banco de referência;
- hash da metadata;
- parâmetros;
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

## Estados

### `completed`

A análise terminou com uma ou mais sequências válidas.

### `stopped`

A execução terminou de forma controlada sem sequência válida para classificar.

### `failed`

O pipeline encontrou um erro que impediu a conclusão. O wrapper tenta persistir um manifesto com a classe e a mensagem da exceção.

## SHA-256

Hashes são usados para detectar alterações nos artefatos. O hash dos resultados considera apenas campos científicos estáveis e exclui valores voláteis como UUID, timestamps e duração.

SHA-256 comprova igualdade de bytes, não qualidade científica. Curadoria, validação e checksum resolvem problemas diferentes.

Arquivos científicos versionados usam finais de linha LF para que seus bytes sejam estáveis entre Windows e Linux.

## Git

O manifesto registra:

- commit atual;
- working tree dirty ou clean.

Execuções produzidas com alterações não commitadas recebem `git_dirty: true` e não possuem a mesma garantia de reprodução. O comando de reprodução recusa manifestos originais gerados com árvore suja.

## Reproduzindo uma execução

Com o mesmo FASTA, banco, metadata, código e working tree limpa:

```powershell
python scripts\reproduce_run.py `
  --manifest runs\<manifest>.json `
  --input data\examples\example_query.fasta
```

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

## Limitações

O MVP não cria ambientes herméticos completos. Versões do sistema operacional, bibliotecas nativas, arquitetura do processador e dependências externas ainda podem afetar determinadas execuções.

O manifesto também não incorpora o arquivo FASTA nem o banco: esses artefatos precisam continuar disponíveis e corresponder aos hashes registrados.
