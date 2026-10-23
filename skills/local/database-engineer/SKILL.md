---
name: database-engineer
description: "Analisar ou alterar modelo de dados, consultas, integridade, transações e migrations com recuperação. Usar quando persistência for afetada; não executar migrações reais por selecionar a skill."
---

# Database Engineer

## Objetivo e ativação

Analisar ou alterar modelo de dados, consultas, integridade, transações e migrations com recuperação. Usar quando persistência for afetada; não executar migrações reais por selecionar a skill.

## Entradas

Esquema e migrations atuais, invariantes, acessos/volume conhecidos e ambiente permitido.
Aproveitar contexto já investigado; buscar somente lacunas relevantes.

## Execução

1. Traçar escritores/leitores e invariantes: unicidade, nulidade, chaves estrangeiras, tenant, ordenação e atomicidade. Não inventar cardinalidade ou política de retenção.
2. Projetar transação e concorrência a partir do isolamento e driver reais. Para consultas, verificar plano de execução e carga representativa antes de propor índices; custo de escrita também importa.
3. Para evolução de schema, preferir expandir, migrar e contrair quando compatibilidade exigir. Distinguir rollback estrutural de recuperação de dados: remover coluna ou restaurar backup antigo pode perder gravações.
4. Testar migrations e falhas em banco descartável com dados sintéticos e contratos do driver disponível. Descrever backup, restore, validação e janela de mudança; aplicar em dados reais somente com autorização específica.

## Saídas e qualidade

Decisão/esquema/migration no escopo autorizado e evidências de integridade, compatibilidade, transação e recuperação.

Invariantes positivos e negativos testados; falha parcial não causa estado inválido; riscos de perda de dados explicitados.
Não declarar verificações aprovadas sem executá-las; registrar limitações e pendências.

## Limites e integrações

Não autoriza operações destrutivas, serviço pago ou mudança de regra comercial. Integrar software-architect, security-auditor e release-manager apenas nas superfícies afetadas.
Respeitar o modo solicitado, instruções superiores e decisões específicas do projeto.

## Exemplo

“Adicione coluna nullable com migration testada em banco descartável.”

## Avaliação da própria skill

Ao validar ou modificar esta skill, usar [evals/cases.json](evals/cases.json) em
fixtures isolados. Avaliar ações, diffs, evidências e proporcionalidade; casos definidos
não significam avaliação de modelo executada. Não carregar os casos no uso rotineiro.
