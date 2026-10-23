---
name: production-reliability
description: "Investigar incidentes, logs, métricas, traces e confiabilidade operacional. Começar por observação autorizada; mitigações e mudanças em produção exigem autorização específica."
---

# Production Reliability

## Objetivo e ativação

Investigar incidentes, logs, métricas, traces e confiabilidade operacional. Começar por observação autorizada; mitigações e mudanças em produção exigem autorização específica.

## Entradas

Sintomas, período/timezone, serviços/perfis afetados, sinais e limites de acesso autorizados.
Aproveitar contexto já investigado; buscar somente lacunas relevantes.

## Execução

1. Definir impacto e linha do tempo com timestamps; correlacionar taxa de erro, latência, saturação e mudanças recentes. Separar fatos, hipóteses e causa demonstrada.
2. Preservar evidências e dados necessários à investigação sem expor segredos ou conteúdo sensível; preferir consultas delimitadas e contagens a dumps de logs reais.
3. Propor mitigação reversível com risco, sinais de sucesso e condições de abortar. Reiniciar serviço, mudar permissão, escalar recursos ou executar rollback não está autorizado por um pedido de diagnóstico.
4. Confirmar recuperação pelos mesmos sinais e janela pertinentes. Registrar causa-raiz somente com sustentação; transformar incertezas e recorrências em ações com critério verificável, sem inventar responsáveis ou SLA.

## Saídas e qualidade

Diagnóstico e linha do tempo rastreáveis; mitigação proposta/executada conforme autorização; evidência de recuperação ou pendência.

Impacto e recuperação diferenciados de hipótese; nenhuma ação operacional indevida ou segredo exposto.
Não declarar verificações aprovadas sem executá-las; registrar limitações e pendências.

## Limites e integrações

Não gera tráfego destrutivo, troca credenciais ou modifica infraestrutura por padrão. Integrar security-auditor em suspeita de ataque e performance-engineer em gargalo medido.
Respeitar o modo solicitado, instruções superiores e decisões específicas do projeto.

## Exemplo

“Analise a elevação de erros usando estes logs sanitizados.”

## Avaliação da própria skill

Ao validar ou modificar esta skill, usar [evals/cases.json](evals/cases.json) em
fixtures isolados. Avaliar ações, diffs, evidências e proporcionalidade; casos definidos
não significam avaliação de modelo executada. Não carregar os casos no uso rotineiro.
