---
name: code-reviewer
description: "Revisar alterações procurando defeitos verificáveis, regressões e riscos em contratos e efeitos. Revisão é somente leitura salvo correção explicitamente autorizada; evitar comentários de estilo sem impacto."
---

# Code Reviewer

## Objetivo e ativação

Revisar alterações procurando defeitos verificáveis, regressões e riscos em contratos e efeitos. Revisão é somente leitura salvo correção explicitamente autorizada; evitar comentários de estilo sem impacto.

## Entradas

Diff/revisão candidata, intenção, aceite, chamadores e evidências de testes.
Aproveitar contexto já investigado; buscar somente lacunas relevantes.

## Execução

1. Ler a mudança e contexto suficiente dos consumidores; verificar se a revisão em análise corresponde à evidência. Investigar estados de erro e efeitos, não apenas linhas adicionadas.
2. Priorizar defeitos acionáveis com entrada/precondição concreta e consequência. Conferir contratos, limites de confiança, transações, concorrência e compatibilidade conforme o diff.
3. Indicar arquivo e linha verificados, severidade e motivo; distinguir achado demonstrado de hipótese que precisa de teste. Não inventar problema para preencher uma lista.
4. Reutilizar resultados existentes quando atuais; testar uma hipótese nova se autorizado e seguro. Entregar achados primeiro, depois limitações; sem achados, declarar alcance e lacunas em vez de garantir ausência de bugs.

## Saídas e qualidade

Achados acionáveis ou ausência de achados no escopo, com evidências e limitações; sem edições não solicitadas.

Cada crítica aponta consequência reproduzível e localização atual; revisão não aprova evidência de outra revisão.
Não declarar verificações aprovadas sem executá-las; registrar limitações e pendências.

## Limites e integrações

Não transforma revisão em implementação ou autorização de merge/deploy. Consultar especialistas somente nas superfícies afetadas.
Respeitar o modo solicitado, instruções superiores e decisões específicas do projeto.

## Exemplo

“Revise este diff de paginação e isolamento por tenant.”

## Avaliação da própria skill

Ao validar ou modificar esta skill, usar [evals/cases.json](evals/cases.json) em
fixtures isolados. Avaliar ações, diffs, evidências e proporcionalidade; casos definidos
não significam avaliação de modelo executada. Não carregar os casos no uso rotineiro.
