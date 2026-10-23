# QA — responsáveis: QA e segurança

Escolher critérios pelo impacto, não por quantidade fixa. Usar article-120.json para
rastreabilidade, engineering.json para controles adicionais; toda verificação precisa
de fonte, cenário, asserção e evidência. Validar aplicabilidade: não transformar
todos os 120 itens em obrigação de uma correção localizada.

Detectar comandos reais: npm/pnpm/yarn e scripts, pytest/unittest, Maven/Gradle/JUnit
ou equivalentes conforme manifestos/CI. Não inferir 'sem testes' só pela ausência de
`package.json`. Inspecionar scripts/imports e destino de dados antes de executar.

Testar unidade para regras/cálculos/validações; integração para contratos, banco,
transações e falhas externas; E2E para fluxos completos quando aplicável. Verificar
valor persistido e ausência de efeito indevido, além de resposta/status. Testar
autorização no servidor, acesso por recurso, perfis e duas organizações isoladas.
Revisar segredos, dependências e configuração sem imprimir credenciais. ASVS é
referência verificável; Top 10 é conscientização de riscos, não suíte completa.

Para UI, inspecionar aplicação real em viewport desktop e móvel pertinente; operar
fluxos afetados, teclado/foco, rótulos, contraste, carregamento, vazio e erro.
Screenshot precisa ser inspecionado; código ou mockup não comprova UI real. Sem
aplicação disponível, marcar verificação visual/interativa não realizada. Reutilizar
ui-ux-visual-auditor quando disponível. Nenhuma estética nova é autorizada por QA.

Registrar comando, ambiente/versão, horário, revisão/estado de fonte, exit code,
casos executados/falhas/skips e artefatos. Reporter nativo ou resultado observável;
não sintetizar testes a partir de `exit 0`. Falta de testes/ambiente mantém pendência.
Corrigir falhas autorizadas e executar novamente; não ignorar flaky/skip obrigatório.
Gates 4/5 exigem testes e segurança aplicáveis comprovados, sem bloqueadores.
