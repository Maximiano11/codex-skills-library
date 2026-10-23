---
name: technical-documentation
description: "Manter conhecimento técnico persistente: arquitetura, contratos, regras, ADRs, operação e evidências. Atualizar fontes existentes e documentar apenas o necessário à mudança."
---

# Technical Documentation

## Objetivo e ativação

Manter conhecimento técnico persistente: arquitetura, contratos, regras, ADRs, operação e evidências. Atualizar fontes existentes e documentar apenas o necessário à mudança.

## Entradas

Pedido, documentos existentes, código/contratos observados e decisões confirmadas.
Aproveitar contexto já investigado; buscar somente lacunas relevantes.

## Execução

1. Localizar a fonte mantida pelo projeto e sua audiência; distinguir comportamento observado, comportamento desejado, hipótese e decisão aprovada.
2. Conferir comandos, caminhos, versões e exemplos executáveis no contexto permitido. Não publicar documentação antiga como verdade absoluta nem redefinir regra de negócio apenas porque um bug existe no código.
3. Atualizar apenas páginas afetadas, conectando decisão à fonte e consequências. Usar ADR para escolha duradoura, runbook para operação e relatório para evidência, sem duplicar a mesma informação em todos.
4. Revisar links e exemplos com ferramentas disponíveis; registrar não executados e manter histórico relevante. Não incluir segredos, dados reais, métricas ou resultados fictícios.

## Saídas e qualidade

Documentação rastreável e proporcional no formato do projeto, com fontes, exemplos e limites.

Leitor consegue reproduzir o procedimento a partir de evidência atual; divergências não são silenciosamente apagadas.
Não declarar verificações aprovadas sem executá-las; registrar limitações e pendências.

## Limites e integrações

Não cria obrigação de documentação em tarefa trivial nem presume autorização para publicar. Compartilhar decisões com software-architect e procedimentos com production-reliability/release-manager.
Respeitar o modo solicitado, instruções superiores e decisões específicas do projeto.

## Exemplo

“Atualize o guia após mudar o contrato de paginação.”

## Avaliação da própria skill

Ao validar ou modificar esta skill, usar [evals/cases.json](evals/cases.json) em
fixtures isolados. Avaliar ações, diffs, evidências e proporcionalidade; casos definidos
não significam avaliação de modelo executada. Não carregar os casos no uso rotineiro.
