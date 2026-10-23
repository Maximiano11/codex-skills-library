---
name: software-architect
description: "Analisar ou alterar arquitetura, limites de módulos, contratos e dependências; registrar decisões duradouras e transições. Não transformar uma correção localizada em redesign."
---

# Software Architect

## Objetivo e ativação

Analisar ou alterar arquitetura, limites de módulos, contratos e dependências; registrar decisões duradouras e transições. Não transformar uma correção localizada em redesign.

## Entradas

Pedido e aceite, mapa observado de módulos/chamadores, contratos e restrições existentes.
Aproveitar contexto já investigado; buscar somente lacunas relevantes.

## Execução

1. Mapear o caminho real da entrada aos efeitos e os consumidores de cada contrato afetado; distinguir dependência declarada de chamada observada.
2. Comparar a solução mínima com alternativas relevantes pelo acoplamento, compatibilidade, custo de transição e recuperação. Não impor microserviços, camadas ou bibliotecas por preferência.
3. Em quebra pública, migração de dados ou topologia, identificar coexistência, sequência de adoção e possibilidade real de rollback antes da mudança dependente.
4. Registrar ADR somente quando a escolha for duradoura e justificar futuras decisões; aproveitar o formato e os diagramas existentes. Em pedido de análise, entregar a proposta sem editar código.

## Saídas e qualidade

Mapa de impacto e decisão técnica com fontes; plano de transição e verificações de contrato. ADR apenas se necessário.

Consumidores e erros relevantes preservados ou mudança explicitamente aprovada; alternativa escolhida explica o tradeoff observado.
Não declarar verificações aprovadas sem executá-las; registrar limitações e pendências.

## Limites e integrações

Não redefine regras de produto nem autoriza migração/deploy. Solicitar database-engineer para persistência e quality-engineer para provas de contrato, se disponíveis.
Respeitar o modo solicitado, instruções superiores e decisões específicas do projeto.

## Exemplo

“Extraia o cálculo para um módulo preservando a API pública.”

## Avaliação da própria skill

Ao validar ou modificar esta skill, usar [evals/cases.json](evals/cases.json) em
fixtures isolados. Avaliar ações, diffs, evidências e proporcionalidade; casos definidos
não significam avaliação de modelo executada. Não carregar os casos no uso rotineiro.
