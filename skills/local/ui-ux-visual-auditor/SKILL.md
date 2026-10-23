---
name: ui-ux-visual-auditor
description: "Validar UI e UX de sistemas, dashboards, aplicativos e sites com inspeção visual real, fluxos interativos, responsividade, acessibilidade e regressão visual. Usar em auditorias de interface, novas telas, mudanças de componentes/layout/estados e revisões visuais pré-release; não aplicar a alterações exclusivamente de backend."
---

# Ui Ux Visual Auditor

Inspecione a interface que o usuário realmente usa. Código correto, screenshot bonito
ou scanner sem alertas não comprovam uma experiência utilizável.

## Escopo e descoberta

Leia AGENTS.md aplicáveis. Identifique plataforma, rotas/telas, componentes,
design system, tokens, temas, referências aprovadas, perfis, idiomas e jornadas.
Localize comandos para executar a aplicação e testes já existentes. Preserve marca,
stack, padrões e decisões aprovadas; não imponha outra estética ou um redesign.
Não adicione ferramentas redundantes nem altere regras de negócio para facilitar a UI.

Use o alvo informado pelo usuário ou disponível no projeto. Se faltar acesso,
credencial de teste ou ambiente, peça apenas o necessário e continue a inspeção
independente. Nunca registre uma tela de login como evidência de uma área que não
foi acessada.

- **Incremental:** valide telas e estados afetados, componentes compartilhados e
  regressões relacionadas. Evite auditar o produto inteiro em mudanças triviais.
- **Auditoria visual/pré-release:** inventarie jornadas críticas e cubra a matriz
  definida de telas, perfis, estados, viewports e plataformas.
- **Código, mockup ou imagens somente:** produza análise parcial. Sem execução,
  interatividade e comportamento real permanecem NÃO VERIFICADOS.

Defina uma matriz verificável antes de testar. Use contrato de suporte e analytics
disponíveis; na ausência, declare uma amostra exploratória, sem inventar suporte.
Leia [checklist.md](references/checklist.md) para selecionar critérios aplicáveis.

## Inspeção real

Abra a aplicação com ferramentas de navegador disponíveis e autorizadas. Para
automação web, prefira Playwright quando já disponível/compatível; preserve ferramentas
equivalentes. Para interfaces nativas, use as ferramentas disponíveis da plataforma,
emulador ou dispositivo e informe qual foi usado. Emulação não comprova dispositivo real.

Capture **e abra para inspecionar** screenshots das telas e estados relevantes,
incluindo viewport inteiro e detalhes do defeito. Combine imagem, interação e
DOM/árvore de acessibilidade quando disponíveis. Não use imagens geradas por IA,
mockups ou capturas de outra revisão como evidência do sistema funcionando.
Siga [evidence-and-regression.md](references/evidence-and-regression.md).

Exercite tarefas completas: navegação, preenchimento, validação, confirmação,
cancelamento, recuperação de erro e resultado visível. Use dados sintéticos e contas
de teste. Não envie mensagens, compre, publique ou altere dados reais sem autorização
específica. Uma solicitação de auditoria não autoriza modificar o produto; se também
for solicitada implementação/correção, corrija localmente dentro desse escopo.

Inspecione com atenção:

- Hierarquia, legibilidade, densidade, alinhamento, espaçamento, consistência e
  correspondência à referência aprovada.
- Cortes, sobreposições, conteúdo longo, rolagem, temas e tamanhos de viewport.
- Descoberta das ações, orientação, feedback, prevenção e recuperação de erros.
- Estados normal, foco, hover quando aplicável, loading, disabled, vazio, sucesso,
  erro e permissões — não apenas o estado inicial.
- Teclado, foco, semântica, contraste, zoom, toque e movimento reduzido.

Para critérios web, leia [accessibility.md](references/accessibility.md). Consulte
fontes oficiais quando precisar confirmar requisito ou exceção. Um achado de
acessibilidade não é automaticamente pequeno: classifique pelo impedimento causado.
Não apresente inspeção heurística como pesquisa com usuários nem aprovação parcial
como certificação WCAG.

## Achados e correções

Distinga **defeito observado**, **hipótese a verificar** e **sugestão estética**.
Todo defeito deve trazer tela/estado, ambiente, passos, esperado, observado, impacto,
evidência e, quando inspecionado, arquivo/linha. Não invente localização de código
nem métricas como taxa de conversão, satisfação ou tempo de tarefa.

- **P0:** impacto crítico comprovado, como UI revelando dados sensíveis ou causando
  perda irreversível grave; não atribua por aparência.
- **P1:** jornada essencial inviável, inclusive barreira de teclado/acessibilidade
  que impeça um público suportado de concluir a tarefa.
- **P2:** dificuldade significativa, inconsistência funcional ou falha visual que
  prejudique compreensão/uso sem bloquear a jornada principal.
- **P3:** acabamento e inconsistências de baixo impacto.

Priorize impacto, alcance e frequência observável. Não invente nota geral para
substituir evidência. P0/P1 abertos bloqueiam aprovação; P2 segue política e decisão
documentada. Sugestões fora do contrato não viram bloqueadores só por preferência.

Quando a correção estiver autorizada, registre o antes, ajuste a menor superfície
necessária, execute a mesma reprodução, capture/inspecione o depois e teste os
consumidores afetados de componentes compartilhados. Nunca esconda conteúdo,
desative zoom/foco ou aprove novas baselines indiscriminadamente para eliminar falhas.

## Integração e conclusão

Com `production-readiness-auditor`, compartilhe a matriz, evidências e IDs de achados:
esta skill cobre UI/UX; a outra consolida regras, backend e release. Não repita testes
sem necessidade. Se a outra skill não estiver disponível, entregue a auditoria
visual de forma independente.

Use [report-template.md](assets/report-template.md) e identifique o alcance:

- **APROVADO:** critérios exigidos no escopo executados com evidências atuais e sem
  bloqueadores; não equivale a aprovação geral de produção.
- **REPROVADO:** falha observada que bloqueia os critérios definidos.
- **NÃO VERIFICADO:** falta execução, acesso, evidência ou teste obrigatório.

Liste explicitamente combinações não testadas, limitações e riscos. Uma auditoria
visual não pode ser aprovada só pela análise do código ou por screenshots não
inspecionados. Relatórios devem apontar evidências reais sem dados pessoais/segredos;
o agente precisa ter permissão antes de compartilhar capturas externamente.
