---
name: performance-engineer
description: "Investigar gargalos de latência, throughput, renderização e recursos por medição. Ativar quando desempenho for solicitado ou houver evidência; não impor otimizações especulativas."
---

# Performance Engineer

## Objetivo e ativação

Investigar gargalos de latência, throughput, renderização e recursos por medição. Ativar quando desempenho for solicitado ou houver evidência; não impor otimizações especulativas.

## Entradas

Sintoma, ambiente, carga/dados representativos e métricas disponíveis.
Aproveitar contexto já investigado; buscar somente lacunas relevantes.

## Execução

1. Definir métrica, unidade, cenário e ambiente antes da otimização. Preservar baseline e variabilidade; não inventar SLA ou usar um tempo isolado como ganho comprovado.
2. Localizar custo com profiler, traces, plano de consulta ou ferramentas de renderização existentes. Separar rede, CPU, I/O, contenção e layout para evitar corrigir o componente errado.
3. Propor a menor intervenção sustentada pela medição; preservar semântica, memória e erro. Cache exige chave completa, invalidação e isolamento; paralelismo exige limite e efeito em recursos.
4. Repetir o mesmo cenário após a mudança e verificar regressões de correção e recursos. Em produção, usar somente observabilidade/ações autorizadas; não gerar carga destrutiva.

## Saídas e qualidade

Baseline, diagnóstico, ajuste autorizado e comparação reproduzível com limitações e tradeoffs.

Ganho sustentado pela mesma carga/ambiente ou resultado inconclusivo declarado; correção preservada.
Não declarar verificações aprovadas sem executá-las; registrar limitações e pendências.

## Limites e integrações

Não adiciona cache, índices ou infraestrutura sem evidência e escopo. Integrar database-engineer para consultas e product-ux para fluidez real, quando necessário.
Respeitar o modo solicitado, instruções superiores e decisões específicas do projeto.

## Exemplo

“Investigue consultas lentas sem alterar o banco real.”

## Avaliação da própria skill

Ao validar ou modificar esta skill, usar [evals/cases.json](evals/cases.json) em
fixtures isolados. Avaliar ações, diffs, evidências e proporcionalidade; casos definidos
não significam avaliação de modelo executada. Não carregar os casos no uso rotineiro.
