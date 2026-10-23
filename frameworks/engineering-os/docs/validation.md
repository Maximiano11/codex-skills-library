# Validação da entrega — 23/10/2026

**VALIDATED no escopo local do núcleo, catálogo e instalador no ambiente executado.**
Isso não equivale a certificação universal, deploy ou validação de um produto cliente.

## Evidências executadas

- Fundação: 24 testes aprovados antes de ampliar as especialidades.
- Consolidação: 62 testes unittest aprovados, sem skips, incluindo integração por CLI,
  dry-run, instalação idempotente, atualização controlada, remoção, preservação de
  conteúdo e skill emprestada, conflitos/symlinks, rollback, estados e evidência obsoleta.
- 13/13 skills passaram no quick_validate.py da skill-creator; catálogo e referências
  também verificados pelo validador do pacote.
- 10/10 avaliações determinísticas de roteamento passaram. Elas verificam modo, risco,
  seleção e ausência de mutação pelo planner; não são resultados de modelo.
- 18 arquivos Python mantidos compilados em memória, sem criação de bytecode.
- Orçamento medido: os entrypoints das 13 skills somam 39.203 bytes UTF-8; o percurso
  CSS selecionado, incluindo orquestração, soma 21.528 bytes. Cem chamadas locais de
  triagem tiveram mediana aproximada de 0,33 ms. São medidas locais de bytes e tempo
  de regras; não representam tokens, latência de modelo ou ganho de produção.
- Dez solicitações executadas por dois avaliadores independentes em fixtures isolados.
  A revisão principal conferiu todos os escopos/diffs e repetiu os testes dos quatro
  fixtures Python: endpoint (5), refatoração (6), schema (3) e prontidão (1).
- CSS/formulário/scroll-drag exercitados em navegador CUA real. Screenshots e relatos
  estão em evaluations/model-run-2026-10-23; os estados de formulário e handle também
  foram inspecionados visualmente pela revisão principal.
- Segurança do framework: três achados reproduzidos, corrigidos e rechecados por
  avaliador independente. Relatórios histórico e atual foram preservados.

| Avaliação com modelo | Resultado e limites |
| --- | --- |
| CSS | Alteração única e margem computada 8px; VALIDATED no escopo |
| Formulário | Erro associado, confirmação, Enter e ausência de persistência exercitados |
| Endpoint | Contrato HTTP, constante, health e 404 testados sem dependências |
| Refatoração | Paridade de API, erros, iteráveis e centavos; contexto elevou risco monetário |
| Scroll/drag | Roda, mouse/handle e teclado passaram; tarefa PARTIALLY_VALIDATED por toque não exercitado |
| Schema | Migration aditiva/repetível e transação do chamador testadas em SQLite em memória |
| Auditoria de autenticação | Violações demonstradas; código preservado e alvo auditado BLOCKED por P1 |
| Prontidão | Integração obrigatória indisponível → PARTIALLY_VALIDATED; nenhum deploy |
| Ambiguidade | Nenhum desconto inventado; pergunta comercial e implementação pendente |
| Somente análise | Cache entre organizações reproduzido sem modificar arquivos |

Na primeira avaliação de prontidão, o agente classificou risco como médio apesar da
política do workflow. A evidência original permanece em release/response.md. A regra
foi explicitada nas skills de orquestração e release e um terceiro avaliador recebeu
somente o pedido e fixture, sem a conclusão esperada: classificou **alto** e manteve
**PARTIALLY_VALIDATED**, registrado em release-recheck/response.md. Não apresentar a
primeira rodada como 10/10 classificações corretas.

## Falhas detectadas e corrigidas

1. Triagem não reconhecia `GET /items` sem palavra API/endpoint: detecção de método/rota
   e regressão adicionadas.
2. P1: update de pacote truncado podia remover runtime/skills e doctor indicar ok.
   Pacote operacional agora é validado antes do plano; doctor também valida estrutura.
3. P2: alteração de modo de arquivo não invalidava evidência. Fingerprint inclui modos.
4. P2: timeout deixava filho herdado ativo. Executor POSIX cria e encerra grupo próprio,
   inclusive ao terminar normalmente; testes e rechecagem confirmaram ausência de
   escrita tardia pelos filhos iniciados. Processos destacados ainda podem escapar.
5. Teste do empacotador expôs comparação com raiz não canonicalizada; paths agora são
   resolvidos antes da checagem. Falha histórica e aprovação posterior foram registradas.
6. Regra de risco de release explicitada após a inconsistência comportamental acima.

Não há P0/P1 conhecido aberto nos comportamentos do framework auditados. A auditoria
é limitada ao código e reproduções indicadas, não afirma ausência de vulnerabilidades.

## Instalação e integração

O instalador é verificado em perfis e projetos descartáveis, incluindo CODEX_HOME e
paths com espaços. O diretório output/engineering-os-delivery-2026-10-23 ao lado deste
projeto concentra logs, JUnit, plano de instalação, diagnóstico, probes de runtime,
integridade e pacote ZIP. Os scripts permitem reproduzir os controles; relatórios
de modelo e artefatos sintéticos ficam no código fonte para auditoria.

Na integração real com app-server de ambos os executáveis disponíveis, um perfil
isolado expôs as 13 skills únicas habilitadas sem erros de parsing, sem iniciar turno
de modelo. A primeira sondagem usou o diretório pessoal como CWD e também encontrou
a prompt-engineer daquele diretório como skill de projeto; a sondagem de controle
em projeto vazio removeu essa sobreposição de escopos. Os registros foram preservados.

A instalação global real do usuário não faz parte das mutações desta entrega. Seu
AGENTS.md e a prompt-engineer anterior ficam preservados; há dry-run preparado para
o perfil real e instalação exercitada em perfil isolado. Para ativar globalmente,
revisar o plano e executar `python3 -B scripts/eos.py install` na raiz do pacote.

## Não executados e riscos residuais

- Ambiente efetivamente executado: macOS/POSIX, Python 3.14.4. Python 3.10 é o mínimo
  de sintaxe/APIs escolhido, mas não foi executado aqui. Windows/Linux não testados.
- Não houve lint ou typecheck externo: nenhuma ferramenta dessa classe era parte da
  stack inicial. Compilação, unittest e validação de contratos são controles distintos;
  não são apresentados como lint/typecheck. Perfis permitem adicionar ferramentas reais.
- Toque real/emulado do exemplo de scroll-drag ficou não verificado. Outros engines,
  leitores de tela e matriz ampla de dispositivos não foram exercitados.
- Não foram executados deploy, migration real, carga de produção, SDK, hooks ou alteração
  de pipeline. Não há proteção remota contra deploy nem sandbox no runner.
- Dados sintéticos e fixtures pequenos; não validam todo repositório/arquitetura, nem
  estimam redução estatística de falhas, retrabalho, tokens ou custos. Cinco casos por
  avaliador compartilharam contexto; a rechecagem de release teve contexto independente.
- Casos definidos por especialidade são material de avaliação futura, não todos
  executados por modelo nesta rodada. Bytes/palavras são orçamento de contexto,
  não medição de tokens de um modelo específico.
- Hashes e atestações não resistem a escritor com os mesmos privilégios; não provam
  veracidade humana. Rollback do instalador cobre exceções em processo, não falha de
  energia, crash abrupto ou filesystem hostil. Backups/journal permanecem disponíveis.
