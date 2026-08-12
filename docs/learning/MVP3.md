# MVP v0.4.0 — Banco curado e proveniência científica

Este registro reúne os conceitos científicos e de engenharia introduzidos na quarta etapa do BioTrace.

## COI e DNA barcode

COI é a subunidade I da citocromo c oxidase, codificada pelo DNA mitocondrial. Em animais, uma região de COI é amplamente usada para comparar organismos porque costuma combinar conservação suficiente para amplificação e variação suficiente para distinguir muitos táxons.

Um DNA barcode é uma região padronizada do DNA usada como identificador comparável. Ele não é um “código de barras” infalível: identificação depende da qualidade da sequência, da cobertura do banco, da taxonomia correta e do método de comparação.

COI-5P designa a região próxima à extremidade 5' de COI usada no barcode animal. Registrar a região é importante porque sequências do mesmo gene, mas de trechos diferentes, podem não se sobrepor adequadamente.

## Accession e accession.version

Accession é o identificador estável atribuído por um banco a um registro. `HQ141077` identifica o registro; `HQ141077.1` identifica uma versão específica de seu conteúdo. Usar accession.version torna a análise mais reproduzível, pois uma atualização futura pode produzir `.2` sem apagar a identidade histórica da versão anterior.

## Voucher

Voucher é um espécime físico, amostra ou material de referência preservado e associado ao registro molecular. Quando existe e está bem documentado, permite reexaminar a identificação original. Ausência ou baixa qualidade dessa informação aumenta a incerteza da curadoria.

## GenBank e BOLD

GenBank é um repositório público de sequências de nucleotídeos e seus metadados. No MVP, ele é a fonte registrada dos dez registros finais.

BOLD, Barcode of Life Data System, é uma plataforma voltada a dados de DNA barcode. Foi usado como apoio à curadoria e conferência. GenBank e BOLD são fontes valiosas, mas registros depositados ainda precisam ser avaliados criticamente.

## Curadoria

Curadoria é o processo de selecionar, conferir, padronizar e justificar os dados aceitos. Neste MVP ela inclui espécie, accession.version, marcador, região, comprimento, bases válidas, fonte, data e duplicidades.

Curadoria não significa que o conjunto representa toda a biodiversidade. Significa que as decisões e limitações do conjunto escolhido são explícitas e verificáveis.

## Proveniência

Proveniência responde de onde os dados vieram, quando foram obtidos, quais critérios foram aplicados e qual versão está em uso. No BioTrace, ela aparece no CSV, na lista de accessions, na metadata, nos scripts de geração, nos testes e na interface.

## Checksum

Checksum é um resumo calculado do conteúdo de um arquivo. O BioTrace usa SHA-256. Se um único byte do CSV mudar, o hash esperado tende a mudar, permitindo detectar que o arquivo já não corresponde à metadata.

O checksum verifica integridade, não verdade científica. Um arquivo pode estar intacto e ainda conter uma identificação incorreta; por isso checksum e curadoria resolvem problemas diferentes.

## Warning e erro científico

Um erro científico representa uma condição incompatível com o contrato do banco e bloqueia seu uso. Exemplos: `N`, comprimento inválido, accession repetido ou sequência idêntica associada a espécies diferentes.

Um warning registra uma condição relevante que não invalida automaticamente o conjunto. KJ204884.1 e KJ204885.1 são idênticas dentro de *Gadus morhua*: o fato precisa aparecer para auditoria, mas não cria conflito taxonômico entre espécies.

Essa separação evita dois extremos: aceitar silenciosamente problemas importantes ou rejeitar dados por toda particularidade conhecida.

## Aprendizado central

Um banco de referência é parte do software científico, não apenas um arquivo auxiliar. Ele precisa de contrato, testes, versão, proveniência, integridade e limitações documentadas.

Dez referências não constituem um banco taxonômico abrangente. O dataset foi construído para permitir estudo controlado e reprodutível dos componentes do BioTrace.
