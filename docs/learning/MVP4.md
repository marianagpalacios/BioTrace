# MVP v0.5.0 — Reprodutibilidade e manifesto de execução

## O problema

Um resultado sem contexto é difícil de auditar. Saber que o BioTrace classificou uma sequência não informa qual arquivo, banco, parâmetro ou versão do código produziu aquela resposta.

O MVP v0.5.0 transforma cada análise em uma execução identificável e verificável.

## Identidade e equivalência

`run_id` identifica uma ocorrência. Duas execuções sempre têm IDs diferentes.

`run_fingerprint` identifica as condições que definem o cálculo. Se entrada, referência, metadata, parâmetros, versão e commit forem iguais, o fingerprint deve ser igual.

Essa separação permite afirmar ao mesmo tempo:

- “foram duas execuções distintas”;
- “foram realizadas sob as mesmas condições”.

## JSON canônico

Objetos JSON podem representar a mesma informação com chaves em ordens diferentes. Antes de calcular o hash, o BioTrace ordena as chaves, usa separadores estáveis e rejeita valores não finitos. Assim, o hash representa a informação, não a formatação casual.

## Hash de resultado

O hash dos resultados exclui elementos voláteis como duração, horário e run ID. Caso contrário, duas execuções equivalentes nunca poderiam produzir o mesmo hash.

## Estados como parte da proveniência

- `completed` registra sucesso com dados válidos;
- `stopped` registra uma interrupção controlada;
- `failed` registra uma exceção impeditiva.

Falhas também são resultados operacionais importantes. Registrar a falha ajuda a explicar o que foi tentado e por que não terminou.

## Git dirty

Um commit identifica código versionado. Se existem mudanças locais não commitadas, o hash do commit sozinho não descreve exatamente o código executado. Por isso o manifesto registra `git_dirty` e a reprodução exata é recusada quando o manifesto original nasceu de uma árvore suja.

## CI e reprodutibilidade

A integração contínua executa a mesma porta de qualidade usada localmente. Testar Python 3.12, 3.13 e 3.14 reduz a dependência de uma única máquina e torna explícita a faixa de compatibilidade.

Durante a implementação, a CI revelou que finais de linha CRLF e LF alteravam o SHA-256 do CSV. A solução foi padronizar artefatos científicos em LF, mostrando que reprodutibilidade depende dos bytes reais, não apenas do conteúdo visual.

## Limite do MVP

Manifestos e hashes aumentam a auditabilidade, mas não congelam todo o ambiente. Containers, lockfiles completos, imagens versionadas e preservação de artefatos podem ampliar essa garantia em versões futuras.
