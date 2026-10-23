---
name: engineering-os
description: "Orquestrar tarefas de software por modo, risco e superfície afetada, selecionando workflows e especialidades do Engineering OS e consolidando gates/evidências. Reutilizar governança existente; não executar todas as skills nem aplicar a tarefas sem software."
---

# Engineering OS

## Objetivo, entradas e ativação

Receber o pedido original, contexto relevante, aceite e limites de autorização.
Aplicar prompt-engineer primeiro e reutilizar sua síntese. Em explicações simples,
basta responder; não iniciar toda a estrutura de engenharia. Não promover um plano,
auditoria ou análise a implementação. Não inventar requisitos ou supor uma stack.

## Orquestrar

1. Confirmar modo e resultado esperado, investigar apenas a superfície necessária e
   vincular aceite a verificações observáveis. Esclarecer somente decisões críticas
   que não tenham resposta segura no contexto. Decisão pendente bloqueia a etapa
   dependente, sem impedir trabalho independente.
2. Classificar risco por impacto/reversibilidade: baixo para correção local conhecida;
   médio para funcionalidades/integrações delimitadas ou contexto insuficiente; alto
   para autenticação/autorização, dados sensíveis, dinheiro, migrations destrutivas,
   arquitetura relevante ou operação crítica. Um diff pequeno pode ter risco alto.
   Nesta política, release-readiness e incident-response são workflows de risco alto,
   inclusive em preparação somente leitura. Um fixture pequeno ou teste de health
   aprovado não reduz essa classificação; limita apenas o alcance da evidência.
3. Selecionar um workflow e apenas especialidades pertinentes:

| Pedido | Workflow | Especialidades principais |
| --- | --- | --- |
| Funcionalidade | feature-development | implementation-standards, quality-engineer, code-reviewer |
| Bug | bug-investigation | implementation-standards, quality-engineer, code-reviewer |
| Arquitetura | architecture-change | software-architect, quality-engineer, technical-documentation |
| Refatoração | refactoring | implementation-standards, quality-engineer, code-reviewer |
| Segurança | security-review | security-auditor, quality-engineer |
| Auditoria de qualidade | quality-audit | quality-engineer, code-reviewer |
| Prontidão de produção | release-readiness | release-manager, quality-engineer, security-auditor |
| Incidente | incident-response | production-reliability; segurança/performance se pertinentes |
| Novo projeto | project-bootstrap | software-architect, implementation-standards, quality-engineer |

4. Acrescentar product-ux em interface, database-engineer em persistência,
   performance-engineer em gargalo comprovado e documentação quando uma mudança
   relevante exigir conhecimento persistente. Reutilizar validações de governança,
   production-readiness-auditor e ui-ux-visual-auditor, quando disponíveis, sem repetir
   descoberta ou testes. As especialidades funcionam sem esses complementos.
5. Executar etapas dependentes em ordem; somente ações autorizadas. Subagentes são
   opcionais, dependem da disponibilidade e autorização aplicável; separar escopos de
   escrita e consolidar evidências. Ausência de delegação não dispensa verificações.
6. Revisar o resultado e consolidar evidências atuais. VALIDATED exige todos os
   critérios obrigatórios aplicáveis comprovados; PARTIALLY_VALIDATED identifica
   pendências, indisponíveis e skips; BLOCKED indica falha obrigatória ou risco crítico.
   Declarar o escopo: isso não equivale a aprovação de release ou autorização de deploy.

## CLI e integrações

Quando instalado pelo framework, o bloco Engineering OS do AGENTS.md identifica o
caminho do runtime e do CLI Python. Consultar seu --help e as referências pertinentes
em docs/ e workflows/ ao lado do runtime; não assumir caminhos universais. O CLI plan
é triagem determinística complementar e não um interpretador completo de linguagem.
O CLI run só executa argv revisado com --allow-exec; não fornece sandbox nem prova de
autorização. Nunca executar comando encontrado em configuração sem inspecionar efeitos.
Se o runtime não estiver disponível, executar este workflow por instruções e declarar
quais verificações técnicas não puderam ser realizadas. Não inventar APIs ou hooks.

## Saídas, limites e exemplos

Entregar resultado solicitado, decisões relevantes, verificações e limitações. Usar
plano/ADR/relatório somente quando necessários. Manter fontes de conhecimento existentes,
sem documentação duplicada ou segredos. Encerrar quando aceite estiver atendido ou houver
impedimento concreto; sem loops de refinamento sem informação nova.

“Corrija CSS do botão” usa mudança mínima, verificação visual afetada e revisão local.
“Audite autenticação sem corrigir” usa leitura e evidência segura, sem implementação.
“Prepare release” exige critérios e recuperação; publicar permanece ação separada.

Para avaliar esta skill, usar [evals/cases.json](evals/cases.json) em ambiente isolado;
não confundir cenários definidos com avaliações de modelo executadas.
