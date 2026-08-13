# Roadmap do BioTrace

## Princípios do roadmap

Cada MVP deve:

- entregar poucas capacidades;
- preservar o funcionamento anterior;
- incluir testes;
- registrar decisões;
- evitar abstrações prematuras;
- separar melhorias de código, dados e ciência;
- explicitar limitações.

---

## MVP v0.1.0 — Base inicial

**Status:** concluído.

- leitura FASTA;
- estatísticas básicas;
- conteúdo GC;
- similaridade simples;
- banco CSV local;
- interface Streamlit;
- tabela, gráfico e exportação.

---

## MVP v0.2.0 — Validação e classificação controlada

**Status:** concluído.

- validação de sequências;
- aceitação opcional de `N`;
- limiar mínimo;
- espécie não identificada;
- ranking;
- múltiplas referências por espécie;
- mensagens e progresso;
- camada de serviço.

---

## MVP v0.3.0 — Qualidade e confiabilidade

**Status:** concluído, com curadoria de dados transferida ao v0.4.0.

### Entregas

- pytest;
- 28 testes automatizados;
- configuração central;
- camada `reference`;
- validação do CSV;
- erros bloqueantes e avisos;
- `ReferenceDatabase`;
- distância de edição;
- inserções e deleções simples;
- métricas nucleotídicas;
- mediana e desvio padrão;
- logging rotativo;
- tempo de execução;
- novas exportações;
- interface atualizada.

### Limitação assumida

O banco continua demonstrativo.

---

## MVP v0.4.0 — Banco de referência e proveniência

**Status:** concluído.

**Foco:** banco de referência e proveniência científica.

### Objetivos

- [x] definir COI-5P como marcador-alvo;
- [x] documentar critérios de inclusão e exclusão;
- [x] selecionar 5 espécies e 10 sequências reais;
- [x] registrar accession.version, fonte e data de acesso;
- [x] manter duas referências por espécie;
- [x] validar A/C/G/T e comprimentos de 500–800 bp;
- [x] detectar duplicatas intra e interespecíficas;
- [x] versionar o banco como v1.0.0;
- [x] gerar e validar checksum SHA-256;
- [x] integrar metadata ao pipeline e à interface;
- [x] documentar proveniência e limitações taxonômicas;
- [x] criar testes para curadoria, dataset e metadata;
- [x] aprovar e fazer merge da PR do MVP v0.4.0.

### Por que vem agora?

A arquitetura já valida a estrutura. O próximo passo lógico é tornar o conteúdo rastreável sem misturar essa tarefa com FASTQ ou BLAST.

---

## MVP v0.5.0 — Reprodutibilidade e automação

**Status:** em desenvolvimento.

**Foco:** transformar cada execução em um resultado reproduzível.

### Objetivos

- [x] manifesto JSON da análise;
- [x] versão do BioTrace;
- [x] versão e hash do banco e da metadata;
- [x] hash do arquivo de entrada e dos resultados;
- [x] parâmetros e timestamps;
- [x] run ID e fingerprint determinístico;
- [x] contratos tipados para análise e manifesto;
- [x] testes integrados de sucesso e falha;
- [x] reprodução baseada em manifesto;
- [x] verificação local padronizada;
- [x] GitHub Actions com matriz Python 3.12–3.14;
- [x] documentação técnica e didática;
- [ ] preparar versão final `0.5.0`;
- [ ] aprovar a CI, mesclar a PR e publicar a tag.

### Resultado esperado

Outra pessoa poderá repetir uma análise e verificar quais entradas, parâmetros e dados foram usados.

---

## MVP v0.6.0 — FASTQ e controle de qualidade

**Foco:** entrada mais próxima de dados de sequenciamento.

### Objetivos

- leitura FASTQ;
- escores Phred;
- estatísticas de qualidade;
- filtragem por qualidade mínima;
- filtragem por comprimento;
- remoção ou corte de bases de baixa qualidade;
- relatório de registros aprovados e rejeitados;
- arquivos de exemplo pequenos;
- testes específicos.

### O que não deve entrar junto

DADA2, QIIME 2 e pipelines completos devem permanecer fora até o controle de qualidade básico estar estável.

---

## MVP v0.7.0 — Orientação e alinhamento biológico

**Foco:** melhorar a validade da comparação.

### Objetivos

- complemento reverso;
- estratégia selecionável;
- alinhamento global ou local;
- configuração de gaps;
- cobertura do alinhamento;
- identidade e cobertura separadas;
- testes com sequências biologicamente comparáveis;
- avaliação de desempenho.

### Possível integração

BLAST pode ser introduzido após existir um contrato estável para mecanismos de busca e comparação.

---

## MVP v0.8.0 — Integração com BLAST e bancos maiores

**Foco:** busca taxonômica mais realista.

### Objetivos

- adaptador para BLAST local;
- criação e versionamento do índice;
- parsing de hits;
- identidade, cobertura e e-value;
- cache;
- tratamento de timeout;
- comparação entre método didático e BLAST;
- testes de integração controlados.

### Restrições

Bancos online em tempo de execução devem ser opcionais. A execução reproduzível deve continuar possível localmente.

---

## MVP v0.9.0 — Indicadores e relatórios

**Foco:** transformar classificações em resultados analisáveis.

### Objetivos

- abundância de sequências;
- tabelas por táxon;
- filtros;
- índices ecológicos introdutórios;
- relatório HTML;
- metadados da amostra;
- exportação estruturada;
- explicação das limitações de inferir abundância a partir de reads.

---

## Versão v1.0.0 — Critérios sugeridos

O BioTrace poderá ser considerado uma primeira versão estável quando possuir:

- fluxo FASTA e FASTQ documentado;
- controle de qualidade;
- banco rastreável;
- manifesto reproduzível;
- testes unitários e integrados;
- CI;
- estratégia de alinhamento ou BLAST;
- resultados com identidade e cobertura;
- documentação de instalação;
- licença;
- exemplos reproduzíveis;
- mensagens claras de erro;
- limites de desempenho conhecidos.

---

## Quantidade aproximada de MVPs

### Para um bom protótipo educacional funcional

Mais **3 MVPs**:

- v0.4;
- v0.5;
- v0.6.

### Para uma ferramenta eDNA tecnicamente convincente

Mais **5 a 6 MVPs**:

- v0.4 até v0.9;
- depois v1.0.

A quantidade pode mudar conforme os testes e as decisões científicas revelarem novas necessidades.
