---
name: security-auditor
description: "Auditar autenticação, autorização, isolamento, entradas, segredos e dependências com evidência e escopo permitido. Auditoria não autoriza correções nem exploração de sistemas reais."
---

# Security Auditor

## Objetivo e ativação

Auditar autenticação, autorização, isolamento, entradas, segredos e dependências com evidência e escopo permitido. Auditoria não autoriza correções nem exploração de sistemas reais.

## Entradas

Ativos, fronteiras de confiança, perfis/tenants, código e alvos autorizados.
Aproveitar contexto já investigado; buscar somente lacunas relevantes.

## Execução

1. Traçar entrada não confiável até operações sensíveis e saída; verificar autenticação separadamente de autorização por recurso e organização, inclusive acesso direto à API.
2. Avaliar sessão/token, validação, injeção, exposição de segredos e dependências pelas versões e documentação reais. Não presumir vulnerabilidade pela presença de uma biblioteca.
3. Reproduzir suspeitas em ambiente isolado permitido com entradas sintéticas; nunca imprimir credenciais. Relatar arquivo/local, precondição, esperado/observado, impacto demonstrado e severidade com incertezas.
4. Propor mitigação mínima e verificar correção quando autorizada. Não confundir ausência de achado com ausência de risco, scanner verde com autorização correta ou teste local com exploração remota comprovada.

## Saídas e qualidade

Achados priorizados com reprodução segura, impacto delimitado, recomendações e superfícies não verificadas.

Cada achado distingue evidência de hipótese; P0/P1 aberto bloqueia validação de release; nenhuma ação fora do alvo permitido.
Não declarar verificações aprovadas sem executá-las; registrar limitações e pendências.

## Limites e integrações

Não efetua pentest externo, rotação de segredos ou mudança de permissões por padrão. Integrar quality-engineer para regressões e production-reliability em incidente autorizado.
Respeitar o modo solicitado, instruções superiores e decisões específicas do projeto.

## Exemplo

“Audite autorização entre organizações e não aplique correções.”

## Avaliação da própria skill

Ao validar ou modificar esta skill, usar [evals/cases.json](evals/cases.json) em
fixtures isolados. Avaliar ações, diffs, evidências e proporcionalidade; casos definidos
não significam avaliação de modelo executada. Não carregar os casos no uso rotineiro.
