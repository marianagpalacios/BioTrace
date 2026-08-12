# Dados de referência do BioTrace

Esta pasta contém os artefatos definitivos do banco curado usado pelo BioTrace v0.4.0. O banco possui versão própria, v1.0.0, independente da versão do software.

## Arquivos

- `species_database.csv`: 10 referências COI-5P de 5 espécies de Actinopterygii, com duas referências por espécie e as colunas `species`, `id`, `gene`, `marker_region`, `accession`, `source`, `retrieved_at` e `sequence`.
- `accessions.txt`: lista dos 10 identificadores accession.version usados para recuperar e auditar os registros.
- `database_metadata.json`: nome, versão, marcador, escopo taxonômico, fonte, data, contagens e checksum SHA-256 do CSV.

`selected_sequences.fasta` é um artefato intermediário do download e não faz parte da distribuição final. Após a validação e preservação das sequências no CSV, ele deve ser removido conforme o passo de limpeza.

## Escopo

As espécies incluídas são *Danio rerio*, *Cyprinus carpio*, *Oreochromis niloticus*, *Salmo salar* e *Gadus morhua*. O marcador é COI-5P, a fonte registrada é NCBI GenBank e a curadoria utilizou informações de GenBank e BOLD para conferir identidade e adequação dos registros.

Cada sequência deve conter somente A/C/G/T, medir entre 500 e 800 bp e possuir accession com versão. O banco exige ao menos duas referências por espécie.

As referências KJ204884.1 e KJ204885.1 são idênticas dentro de *Gadus morhua*. Essa condição conhecida gera warning, não erro. Sequências idênticas atribuídas a espécies diferentes são bloqueadas.

O SHA-256 em `database_metadata.json` vincula a metadata ao conteúdo exato de `species_database.csv`. Qualquer alteração no CSV exige nova validação, nova metadata e uma decisão explícita de versionamento.

Dez referências não constituem um banco taxonômico abrangente. Este dataset existe para estudo controlado e reprodutível dos componentes do BioTrace.
