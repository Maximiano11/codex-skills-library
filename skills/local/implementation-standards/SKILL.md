---
name: implementation-standards
description: "Implementar ou corrigir código seguindo convenções, tipos, erros e contratos reais do projeto. Usar durante mudanças autorizadas; não aplicar refatorações gerais por estilo."
---

# Implementation Standards

## Objetivo e ativação

Implementar ou corrigir código seguindo convenções, tipos, erros e contratos reais do projeto. Usar durante mudanças autorizadas; não aplicar refatorações gerais por estilo.

## Entradas

Escopo autorizado, critérios de aceite e arquivos/chamadores relevantes.
Aproveitar contexto já investigado; buscar somente lacunas relevantes.

## Execução

1. Ler exemplos próximos, configuração de formatação/tipagem e convenções de erro antes de editar; preservar stack e dependências existentes.
2. Manter validação nas fronteiras de confiança e não esconder erro com fallback que mude a regra. Preservar semântica de vazio, nulo, erro e efeitos colaterais do contrato.
3. Fazer a menor mudança suficiente com nomes e tipos claros. Reutilizar abstrações existentes quando reduzirem duplicação real; não introduzir arquitetura para uma hipótese futura.
4. Revisar o diff por mudanças adjacentes e executar verificações afetadas compartilhadas com QA. Atualizar chamadores somente se necessários ao pedido.

## Saídas e qualidade

Código no escopo e síntese de decisões, verificações e limitações; sem relatório adicional obrigatório.

Comportamento solicitado e contratos preservados, erros tratados sem silenciosamente suprimir falhas e nenhuma dependência injustificada.
Não declarar verificações aprovadas sem executá-las; registrar limitações e pendências.

## Limites e integrações

Não escolhe regras de negócio ambíguas. quality-engineer valida regressões; code-reviewer revisa a alteração, sem repetir a mesma suíte sem motivo.
Respeitar o modo solicitado, instruções superiores e decisões específicas do projeto.

## Exemplo

“Corrija o parser mantendo os erros documentados.”

## Avaliação da própria skill

Ao validar ou modificar esta skill, usar [evals/cases.json](evals/cases.json) em
fixtures isolados. Avaliar ações, diffs, evidências e proporcionalidade; casos definidos
não significam avaliação de modelo executada. Não carregar os casos no uso rotineiro.
