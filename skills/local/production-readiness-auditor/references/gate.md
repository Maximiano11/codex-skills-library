# Gate executável

O runner é um componente de bloqueio local para repositórios Git; só é um bloqueio de
deploy quando o CI/CD depende do seu exit code e da mesma revisão/artefato. Requer
Python 3.10+, Git e os comandos de projeto escolhidos após a descoberta da stack.
Não instala pacotes nem modifica pipelines.

## Preparar uma política real

Crie um JSON com `version: 1`, `checks` e `review`. Não execute comandos vindos de
políticas não revisadas: a configuração autoriza execução de programas locais.
Não coloque tokens em argumentos ou logs; preserve evidências em armazenamento
com controle de acesso.

Cada check tem `id` único (`[a-z0-9-]+`), `kind` e `argv`, uma lista de argumentos sem
shell, com `timeout_seconds` opcional (padrão 600). Todos os checks são obrigatórios.
Declare as categorias `build`, `lint`, `types`, `tests` e `regression`. Pode haver
múltiplos checks de testes para unitários, integração, API, E2E e acessibilidade.
Se uma ferramenta não se aplica, build/lint/types podem ter `not_applicable` com
justificativa revisada em vez de `argv`. Não use isso para dispensar um build existente.
Testes e regressão não podem ser dispensados.

Checks de testes/regressão precisam de `junit`, caminho relativo ao diretório de
evidência exclusivo daquele check. A variável `QA_EVIDENCE_DIR` e o token
`{evidence_dir}` nos argumentos apontam para esse diretório. Configure o reporter
nativo para gerar XML ali; não reutilize XML de outra execução. Nunca fabrique
testcases para fazer um comando sem assertions parecer um teste.

O parser aceita JUnit com `testsuite`/`testsuites` e casos reais, incluindo suites
aninhadas. Recusa zero casos, falhas, erros, skips, totais divergentes e marcadores
conhecidos de retries/flakiness. Desative retries na execução obrigatória e confira
o formato do seu runner: nem todo formato JUnit registra retries ou asserts. Adapte
e teste o parser para formatos diferentes; não suprima informações incompatíveis.

`review` exige:

- `completed: true`, apenas depois da auditoria de fato.
- `revision`: SHA completo de HEAD revisado. Gere a política fora do checkout depois
  de revisar a revisão final, evitando referência circular no commit.
- `evidence`: arquivo não vazio relativo ao repositório com o relatório de revisão.
- `limitations`: lista de limitações documentadas; não use para dispensar testes
  obrigatórios pendentes. Uma pendência obrigatória mantém `completed: false`.
- `findings`: lista, inclusive vazia se a auditoria de fato não encontrou defeitos.
  Cada item tem `id`, `severity` (P0–P3), `status` (open/resolved) e `evidence` textual.
  P2 aberto exige `release_decision` (block/accept), `owner` e `rationale`.

P0/P1 abertos sempre bloqueiam; P2 bloqueia conforme decisão documentada. Resolução
precisa de evidência de correção e reteste na revisão. O script valida formato e
coerência, não autentica o revisor nem comprova a veracidade do inventário.

## Executar e interpretar

```sh
python3 /caminho/production-readiness-auditor/scripts/release_gate.py \
  --repo /caminho/repositorio \
  --policy /caminho/externo/politica-revisada.json \
  --out /caminho/externo/nova-execucao
```

Use um diretório de saída novo a cada execução. Prefira fora do checkout; qualquer
arquivo gerado dentro dele deve seguir os padrões de artefatos ignorados do projeto.
A árvore precisa estar limpa e no SHA revisado antes e depois dos comandos. Arquivos
ignorados, serviços externos e ambiente não são cobertos por identidade Git: use
lockfiles, builds reproduzíveis, ambiente isolado e versões fixadas no CI.

- `0 / APROVADO`: todos os checks declarados passaram e não há bloqueadores declarados.
- `1 / REPROVADO`: falha de comando, XML ausente/inválido ou finding bloqueante.
- `2 / NÃO VERIFICADO`: configuração/revisão/ambiente incompleto, fonte modificada ou
  execução sem condições de comprovação. Também bloqueia deploy.

`report.json` contém revisão, horários, comandos, resultados, contagens, justificativas
de inaplicabilidade e hashes SHA-256 de política, revisão, logs e XML aprovado.
Hashes são rastreabilidade local, não assinatura nem defesa contra adulteração por
quem controla o checkout. O CI deve guardar os artefatos da execução atual.

## Integração com CI/CD

Depois de identificar o provedor, prepare um diff com:

1. Checkout da revisão exata, dependências por lockfile, ambiente e dados de teste
   isolados, revisão e política para a mesma revisão.
2. Execução do gate sem `continue-on-error`, `allow_failure`, `|| true` ou redução
   silenciosa dos cenários.
3. Upload de logs/relatório mesmo na falha, com retenção e sigilo apropriados.
4. Check obrigatório na proteção da branch; job de deploy dependente do sucesso do
   gate e usando o mesmo SHA/artefato validado, incluindo todos os caminhos de deploy.
5. Aprovação antes de alterar pipeline de produção, sem publicar automaticamente.

Se não há provedor/deploy informado, registre estas dependências como pendentes.
Não invente GitHub Actions, Vercel ou outro destino. Regras no AGENTS.md orientam
agentes, mas não impõem proteção no servidor.

## Testar o próprio gate

```sh
python3 /caminho/production-readiness-auditor/scripts/test_release_gate.py
```

A suíte cria repositórios Git temporários, executa a CLI e verifica aprovação e
bloqueios, incluindo testes com assertion falhando mesmo quando o processo retorna
zero. Usa apenas biblioteca padrão e dados descartáveis. Os fixtures validam o
comportamento do gate; não representam funcionalidades de um produto do usuário.
