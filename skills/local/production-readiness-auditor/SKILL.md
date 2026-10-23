---
name: production-readiness-auditor
description: "Auditar qualidade de software com evidências executadas e gate de pré-produção. Usar em revisões de release, novas funcionalidades, mudanças de regras de negócio, formulários ou APIs, correções de bugs, refatorações com risco de regressão e auditorias solicitadas; dimensionar os testes ao risco da mudança."
---

# Production Readiness Auditor

Código compilado não significa funcionalidade validada. Teste escrito não significa
teste executado. Teste aprovado não significa ausência absoluta de defeitos.

## Descobrir antes de modificar

Confirme o repositório alvo. Inspecione AGENTS.md aplicáveis, skills locais, estrutura,
manifestos, lockfiles, scripts, testes, build, deploy e CI/CD. Mapeie frontend,
backend, persistência, serviços externos, autenticação, formulários e regras de
negócio. Registre arquivos e comandos que sustentam o inventário; não presuma stack.
Se o projeto estiver ausente, peça sua localização, avance apenas em entregas
independentes e declare a aplicação NÃO VERIFICADA. Não invente uma aplicação
demonstrativa como evidência de validação do produto.

Reutilize ferramentas existentes. Prefira Playwright para novos E2E de navegador
quando compatível; preserve infraestrutura equivalente já adequada. Escolha testes
unitários compatíveis com a stack e o gerenciador existente. Não instale ferramentas
redundantes. Antes de executar scripts, confira seu destino, efeitos e uso de dados.

## Escolher o alcance

- **Incremental:** selecione cenários afetados e regressões proporcionais ao risco;
  registre o que não foi executado. Não execute a suíte inteira em alterações
  triviais. Um resultado incremental nunca equivale à aprovação de release.
- **Pré-produção:** cubra fluxos críticos, integrações, segurança e regressões com
  a suíte mais ampla exigida pela política do projeto. Execute o gate sobre a revisão
  que será publicada. Mudanças críticas em autorização, dinheiro, migrações,
  concorrência ou exclusão exigem revisão ampliada.

Leia [checklists.md](references/checklists.md) conforme as superfícies afetadas.
Construa uma matriz regra → fonte → cenário positivo/negativo/fronteira/regressão →
asserção observável → evidência. Diferencie regra existente, hipótese e decisão
pendente. Não invente limites, formatos ou regras de negócio; proponha e peça
confirmação apenas quando uma decisão ambígua impedir a implementação correta.

## Executar, corrigir e comprovar

Use dados isolados, determinísticos e descartáveis, com limpeza ao final, contas
de teste por perfil e organizações distintas. Nunca altere dados de clientes nem
execute testes destrutivos contra produção. Não publique nem contrate serviços.

Teste resultados de negócio: valores persistidos, efeitos e ausência de efeitos,
respostas e permissões; abrir página ou encontrar elemento sozinho não comprova
funcionalidade. Para cada defeito, registre reprodução, resultado esperado/observado,
causa provável e severidade; crie teste de regressão que falhe, corrija dentro do
escopo autorizado, execute o teste novamente e as regressões relacionadas. Se não
for viável automatizar, documente a razão e a evidência manual. Corrija falhas sob seu
controle antes de concluir. Nunca suprima asserts, enfraqueça regras, remova cenários
ou esconda skips/retries/flakiness para obter verde.

- **P0:** risco crítico de segurança, perda de dados ou indisponibilidade grave.
- **P1:** fluxo essencial quebrado ou violação relevante de regra.
- **P2:** falha funcional secundária, validação incorreta ou UX significativa.
- **P3:** inconsistência ou melhoria de baixo impacto.

P0/P1 conhecidos e abertos bloqueiam release. P2 requer decisão documentada segundo
impacto e política de release; incerteza não equivale a aceite.

## Persistência e gate

Acrescente o conteúdo de [AGENTS.qa.md](assets/AGENTS.qa.md) ao AGENTS.md do projeto
sem substituir instruções existentes ou duplicar o bloco. Antes de alterar CI/CD
de produção, apresente o diff concreto e obtenha aprovação, conforme a autorização
do usuário. Prepare a proposta localmente, fora do pipeline ativo, até essa etapa.
Um script local sozinho não bloqueia deploys externos.

Leia [gate.md](references/gate.md) para adaptar e executar `scripts/release_gate.py`.
O script usa Python 3.10+ e biblioteca padrão; não exige instalar ferramentas de
teste de aplicação. O gate recusa configuração incompleta, evidência de testes
ausente, nenhum teste executado, skips, falhas, revisão divergente e árvore suja.
Use o relatório do runner real, nunca sintetize JUnit a partir de um simples exit 0.
Caso a stack não exporte JUnit, adapte um parser estrito do formato nativo com testes
antes de usar o gate, ou mantenha o release NÃO VERIFICADO.

Não aplique uma política de exemplo como se já fosse aprovada para o projeto.
Os critérios automatizáveis incluem build, lint/tipos quando disponíveis, testes
obrigatórios e regressões. A revisão humana cobre regras, inventário de problemas,
erros críticos de integração, limitações e adequação da cobertura. O gate não prova
que essa revisão é verdadeira nem que a lista de defeitos é completa.

## Relatório de cada auditoria

Use [report-template.md](assets/report-template.md). Inclua escopo, revisão, arquivos
e funcionalidades, comandos realmente executados, resultados, problemas e severidade,
correções, evidências, testes não executados com razões e riscos residuais.

- **REPROVADO:** falha obrigatória observada, P0/P1 aberto ou bloqueio da política.
- **NÃO VERIFICADO:** evidência, ambiente, teste obrigatório ou decisão necessária
  ausente; nunca inferir aprovação de ausência de erro.
- **APROVADO:** todos os critérios aplicáveis comprovados, sem bloqueadores.

Qualifique sempre o alcance: aprovação da infraestrutura, de testes incrementais e
de release são conclusões diferentes. Referencie evidências da execução atual,
com revisão/horário, sem expor segredos, tokens ou dados de clientes.
