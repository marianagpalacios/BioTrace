# Instalação, execução e reprodução

## Requisitos

- Git;
- Python 3.12, 3.13 ou 3.14;
- NCBI BLAST+ somente para buscas BLAST locais.

O alinhamento pairwise funciona sem BLAST+.

## Instalação no Windows PowerShell

```powershell
git clone https://github.com/marianagpalacios/BioTrace.git
cd BioTrace
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Para executar testes, instale também as dependências de desenvolvimento:

```powershell
python -m pip install -r requirements-dev.txt
```

## Instalação no Linux ou macOS

```bash
git clone https://github.com/marianagpalacios/BioTrace.git
cd BioTrace
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## NCBI BLAST+

Confirme a instalação:

```powershell
blastn -version
makeblastdb -version
```

No Windows, adicione a pasta `bin` do BLAST+ ao `PATH` do usuário e abra um terminal novo. O BioTrace apresenta uma mensagem específica quando `blastn` não está disponível.

O campo “Banco BLAST” da interface recebe o prefixo do banco, sem extensão. Bancos locais podem ser construídos e verificados com:

```powershell
python scripts\build_blast_database.py --help
python scripts\verify_blast_database.py --help
```

## Executar a interface

```powershell
python -m streamlit run app/main.py
```

Use `data/examples/example_query.fasta` ou `data/examples/example_reads.fastq` para uma primeira execução. A interface detecta o formato pela extensão aceita e mostra o backend selecionado.

## Erros esperados

- arquivo sem registros: a análise informa que nenhum registro foi encontrado;
- sequências inválidas: os registros são separados e documentados;
- nenhum read aprovado no QC: a execução termina de forma controlada;
- BLAST ausente: instale BLAST+ e confirme `blastn` no `PATH`;
- timeout BLAST: aumente o timeout ou revise banco e consulta;
- banco ou metadata incompatível: reconstrua ou restaure os artefatos corretos.

## Verificar o projeto

```powershell
python scripts\verify_project.py
```

Esse comando executa `pip check`, testes e compilação. Para etapas isoladas:

```powershell
python -m pip check
python -m pytest
python -m compileall src tests scripts app
```

## Reproduzir uma execução

Faça a execução original com o working tree limpo. Em seguida:

```powershell
python scripts\reproduce_run.py `
  --manifest runs\<manifesto>.json `
  --input data\examples\example_query.fasta
```

Para FASTQ, forneça o FASTQ original. A reprodução valida hashes, versão, commit, parâmetros científicos, backend e configuração do banco antes de comparar os resultados.

Saída esperada:

```text
REPRODUCTION OK
Original run: ...
New run: ...
Fingerprint: ...
```

Manifestos em `runs/` e logs em `logs/` são artefatos locais e não devem ser commitados.
