# MVP6 — Evolução do pipeline FASTQ

## Evolução posterior

O controle de qualidade FASTQ introduzido no MVP v0.6.0 passou a alimentar etapas posteriores do pipeline.

No v0.7.0, as sequências passaram por resolução de orientação e alinhamento biológico.

No v0.8.0, o BioTrace passou a oferecer dois mecanismos de busca:

- alinhamento pairwise;
- BLAST local.

Assim, FASTA e FASTQ passam a convergir para uma camada comum de busca e classificação.
