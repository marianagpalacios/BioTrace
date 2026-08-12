# Banco de referência científico

## 1. Objetivo científico

O banco v1.0.0 fornece um conjunto pequeno, rastreável e estável para desenvolver e testar carregamento, validação, classificação e proveniência no BioTrace v0.4.0.

Dez referências não constituem um banco taxonômico abrangente. O dataset foi construído para permitir estudo controlado e reprodutível dos componentes do BioTrace.

## 2. Escopo taxonômico

O escopo declarado é Actinopterygii. Foram escolhidas cinco espécies de peixes: *Danio rerio*, *Cyprinus carpio*, *Oreochromis niloticus*, *Salmo salar* e *Gadus morhua*. Há duas referências por espécie.

## 3. Marcador COI-5P

O gene-alvo é COI, e a região registrada é COI-5P, a porção 5' frequentemente usada como DNA barcode animal. O MVP exige essa combinação em todos os registros para evitar misturar regiões ou marcadores não comparáveis.

## 4. Espécies escolhidas

As cinco espécies oferecem um conjunto limitado e conhecido para testar classificações corretas, rankings, múltiplas referências por táxon e tratamento de duplicidades.

## 5. Processo de busca e curadoria

Os candidatos foram pesquisados e conferidos antes da engenharia desta versão. O processo registrou accession.version, espécie, marcador, comprimento, alfabeto da sequência, fonte e data de recuperação. A lista final foi baixada em FASTA e transformada em CSV por script reproduzível.

## 6. NCBI GenBank

O NCBI GenBank é a fonte efetiva das sequências distribuídas. `source` é fixado como `NCBI GenBank`, `retrieved_at` registra a data de recuperação e cada registro conserva seu accession com versão.

## 7. BOLD

O Barcode of Life Data System (BOLD) foi usado como apoio à curadoria e conferência do contexto de DNA barcode. A presença de um registro em uma fonte não elimina a necessidade de verificar espécie, marcador, voucher e demais metadados disponíveis.

## 8. Critérios de inclusão

- espécie dentro do escopo definido;
- identificação binomial;
- gene COI e região COI-5P;
- accession com versão;
- origem rastreável no NCBI GenBank;
- sequência entre 500 e 800 bp;
- somente bases A/C/G/T;
- pelo menos duas referências por espécie.

## 9. Critérios de exclusão

- registros sem versão do accession;
- sequência com `N` ou outro símbolo ambíguo;
- comprimento fora do intervalo;
- gene, região, fonte ou espécie incompatível;
- accession duplicado;
- sequência idêntica atribuída a espécies diferentes;
- metadata insuficiente para sustentar a inclusão.

## 10. Accessions finais

| Espécie | Accessions |
|---|---|
| *Danio rerio* | HQ141077.1, HQ141079.1 |
| *Cyprinus carpio* | HQ600722.1, KR809733.1 |
| *Oreochromis niloticus* | PV812904.1, PP727595.1 |
| *Salmo salar* | KX781876.1, KX781935.1 |
| *Gadus morhua* | KJ204885.1, KJ204884.1 |

KJ204884.1 e KJ204885.1 possuem sequência idêntica dentro de *Gadus morhua*. A condição é mantida como warning auditável porque não cria conflito entre espécies.

## 11. Validação automática

O CSV passa pelo loader, pelo validador estrutural e pelo validador científico. Erros bloqueiam o uso; normalizações seguras e duplicidades intraespecíficas conhecidas são comunicadas como warnings. Testes automatizados conferem regras isoladas e o dataset real.

## 12. Proveniência e versionamento

`database_metadata.json` identifica o banco como v1.0.0 e registra nome, marcador, escopo, fonte, data de criação, quantidade de registros e espécies. A versão do banco é independente da versão v0.4.0 do software.

## 13. SHA-256

O checksum SHA-256 representa os bytes exatos de `species_database.csv`. Antes da classificação, o BioTrace compara o hash atual com a metadata, além de conferir contagens, marcador e fonte. Se houver divergência, o banco é recusado.

## 14. Limitações

- somente cinco espécies e dez referências;
- cobertura insuficiente da diversidade intra e interespecífica;
- ausência de representação geográfica ampla;
- dependência da qualidade das identificações depositadas nas fontes;
- similaridade por distância de edição, sem alinhamento biológico completo;
- inadequado para conclusões taxonômicas, ecológicas, clínicas ou ambientais isoladas.
