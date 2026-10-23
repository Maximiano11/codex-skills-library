---
name: product-ux
description: "Projetar ou validar fluxos, interações, estados, acessibilidade e responsividade de interfaces. Preservar identidade visual; não equivale a rebranding nem auditoria de backend."
---

# Product UX

## Objetivo e ativação

Projetar ou validar fluxos, interações, estados, acessibilidade e responsividade de interfaces. Preservar identidade visual; não equivale a rebranding nem auditoria de backend.

## Entradas

Fluxo solicitado, perfis, estados, design system existente e acesso à interface quando disponível.
Aproveitar contexto já investigado; buscar somente lacunas relevantes.

## Execução

1. Mapear tarefa do usuário, entrada, foco, confirmação, erro, vazio, carregamento e recuperação pertinentes. Não criar campos ou etapas por preferência.
2. Preservar componentes e tokens existentes; definir navegação por teclado, rótulos, foco visível e anúncios de estado conforme o componente. Em formulários, relacionar erros aos campos sem depender só de cor.
3. Em scroll versus drag, separar gesto, handle, área rolável, sensores, captura de ponteiro e alternativa por teclado. Investigar handlers reais antes de bloquear scroll ou aplicar preventDefault global.
4. Inspecionar a UI em execução, exercitar interação e tamanhos pertinentes e guardar evidência visual quando necessário. Se não houver acesso, registrar não verificado; teste de DOM ou screenshot de mockup não comprova o fluxo real.

## Saídas e qualidade

Critérios de uso observáveis, alterações autorizadas e evidências de interação/visual; limitações de acesso explícitas.

Tarefa principal, erro e recuperação exercitados, teclado e foco coerentes, sem regressão observada no layout ou identidade.
Não declarar verificações aprovadas sem executá-las; registrar limitações e pendências.

## Limites e integrações

Não autoriza redesign ou mexer em dados reais. Reutilizar ui-ux-visual-auditor se disponível; para páginas públicas, uma skill visual compatível pode orientar estilo, sem substituir validação.
Respeitar o modo solicitado, instruções superiores e decisões específicas do projeto.

## Exemplo

“Corrija o conflito de scroll com drag mantendo a alternativa por teclado.”

## Avaliação da própria skill

Ao validar ou modificar esta skill, usar [evals/cases.json](evals/cases.json) em
fixtures isolados. Avaliar ações, diffs, evidências e proporcionalidade; casos definidos
não significam avaliação de modelo executada. Não carregar os casos no uso rotineiro.
