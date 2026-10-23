---
name: release-manager
description: "Preparar release com revisão candidata, gates, migrações, observabilidade e recuperação. Prontidão não autoriza publicação, alteração de pipeline ou operação em produção."
---

# Release Manager

## Objetivo e ativação

Preparar release com revisão candidata, gates, migrações, observabilidade e recuperação. Prontidão não autoriza publicação, alteração de pipeline ou operação em produção.

## Entradas

Revisão/conteúdo candidato, critérios e destino pretendido, evidências e procedimento existente.
Aproveitar contexto já investigado; buscar somente lacunas relevantes.

## Execução

Classificar release-readiness como risco alto nesta política, inclusive na preparação
somente leitura. Poucos arquivos, dados sintéticos ou health verde não reduzem o rigor
dos gates de produção; declarar as limitações do escopo separadamente.

1. Fixar o conteúdo avaliado e conferir se build/testes/revisão correspondem a ele, incluindo alterações locais relevantes. Não reutilizar verde de revisão anterior.
2. Selecionar verificações obrigatórias conforme risco e política existente: build, testes afetados, segurança, compatibilidade, documentação e migrations. Indisponível ou skip não conta como aprovado.
3. Preparar sequência de implantação e recuperação realista: backup restaurável, compatibilidade durante transição, sinais de saúde e condições de abortar. Rollback de binário não recupera automaticamente dados removidos.
4. Entregar VALIDATED/PARTIALLY_VALIDATED/BLOCKED no escopo de prontidão. Executar deploy ou pipeline somente com autorização específica para destino e operação, respeitando controles externos.

## Saídas e qualidade

Decisão de prontidão, evidências atuais e plano operacional/recuperação pertinente; autorização operacional separada.

Nenhum P0/P1 aberto, nenhum critério obrigatório pendente/falhando para VALIDATED e revisão candidata compatível com evidências.
Não declarar verificações aprovadas sem executá-las; registrar limitações e pendências.

## Limites e integrações

Não cria proteção remota de deploy com um arquivo local. Integrar quality-engineer e database-engineer/production-reliability apenas conforme o release.
Respeitar o modo solicitado, instruções superiores e decisões específicas do projeto.

## Exemplo

“Prepare a release sem publicar.”

## Avaliação da própria skill

Ao validar ou modificar esta skill, usar [evals/cases.json](evals/cases.json) em
fixtures isolados. Avaliar ações, diffs, evidências e proporcionalidade; casos definidos
não significam avaliação de modelo executada. Não carregar os casos no uso rotineiro.
