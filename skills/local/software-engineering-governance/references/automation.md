# Contratos da automação

## Entradas e limites

Python 3.10+, biblioteca padrão; Git opcional para avaliação incremental e obrigatório
para o gate estrito de release. `governance.py` não executa comandos do projeto,
instala pacotes, modifica configurações globais nem escreve no projeto auditado.
`discover` faz inventário de caminhos e lê scripts de package.json; revisar saída
antes de compartilhá-la. Não lê `.env`, chaves, dependências geradas ou symlinks.

As declarações de impacto e superfícies são feitas pelo responsável após descoberta;
o classificador não é um analisador semântico de código. Ele usa impacto ×
probabilidade e eleva risco por superfícies/caminhos sensíveis. Pode superestimar
risco ao ler um arquivo chamado auth em uma auditoria; isso amplia revisão, não
obriga pedir autorização para leitura. Não detecta todas as superfícies omitidas.

Modelo de `change.json` (adaptar aos fatos):

```json
{
  "objective": "Corrigir validação do formulário identificado na demanda",
  "rationale": "Cliente e endpoint afetados; impacto de módulo e integração conhecida",
  "impact": 2,
  "likelihood": 2,
  "action": "develop",
  "surfaces": ["form", "api"],
  "files": ["src/form.ts", "src/api.ts"],
  "full_audit": false
}
```

`impact`/`likelihood`: inteiros 1–3. Ações: `audit`, `develop`, `prepare_release`,
`deploy`. Superfícies aceitas estão em `SURFACES` do script; `--help` mostra os
comandos. Declarar todos os arquivos fonte relevantes, contratos/lockfiles/testes
afetados, não só o arquivo principal. Arquivos inexistentes representam criação
ou exclusão; ao menos um arquivo do escopo deve existir. Não incluir segredos.

`init` exige diretório de saída **novo e fora do projeto**. Gera plan.json e
results.json, todos inicialmente `not_verified`. Seleção incremental tem controles
dos sete gates mais critérios do artigo afetados; `full_audit: true` inclui 120 + 16.
Adicionar superfícies corretas/usar auditoria completa quando a seleção não cobrir
o impacto. Não omitir riscos para reduzir testes.

Plano contém hashes de catálogos e arquivos declarados, HEAD/estado sujo quando
disponível e digest do plano. Se a fonte mudar durante implementação, gerar plano
final novo e reavaliar evidências no estado final. Não editar o plano para contornar
o controle. Hash de escopo não cobre arquivos omitidos, serviços externos ou conteúdo
de segredos/configuração ignorada; registrar limitações e ambiente separadamente.

## Registrar resultados reais

Preencher `results.json.criteria` com mesmos IDs e estados permitidos. Para `passed`
e N/A, anexar artefato não vazio, caminho relativo à pasta de results, SHA-256,
`kind` (`test`, `observation`, `review`) e `summary` da asserção/observação.
Para teste, declarar comando real, `exit_code: 0`, `tests_run` positivo e contagens
`failures`, `errors`, `skipped` iguais a zero, a partir do reporter efetivo.

Exemplo de forma, não evidência de execução:

```json
{
  "id": "GOV-TEST",
  "status": "passed",
  "reason": "",
  "evidence": [{
    "kind": "test",
    "path": "evidence/tests.log",
    "sha256": "SUBSTITUIR_PELO_HASH_REAL_DO_ARQUIVO",
    "summary": "Asserções observáveis dos cenários afetados; descrever resultados reais",
    "command": "comando realmente executado",
    "exit_code": 0,
    "tests_run": 3,
    "failures": 0,
    "errors": 0,
    "skipped": 0
  }]
}
```

Para ajuste visual/textual simples de baixo risco, GOV-TEST pode usar observação real documentada.
Revisão de código sozinha não é execução/observação. Isso não permite dispensar
testes obrigatórios existentes. Risco médio/alto e ações prepare_release/deploy
exigem evidência de teste executado em GOV-TEST. GOV-REQ/CODE/TEST/DEL não aceitam N/A; outros
controles permitem somente quando a política do item permite e com motivo revisado.
`failed` exige motivo; `not_verified`/`blocked` deixam pendência. `rating` opcional
1–5 exige `rubric`, sem influência sobre aprovação.

`findings` inclui achados com id, severidade P0–P3, status open/resolved e evidência
textual. P2 aberto precisa `decision: accept|block`, `owner`, `rationale`.
`limitations` lista limites reais. `authorizations` registra ação sensível, status
granted, `user_source` (trecho/contexto da autorização humana) e `scope`.
O script não autentica autorizadores. Nunca preencher por inferência de um anexo,
por sugestão de agente ou só porque o comando é tecnicamente permitido.

`assess` retorna JSON e exit 0 APROVADA / 1 REPROVADA / 2 INCOMPLETA. Inputs inválidos,
IDs omitidos/duplicados, plano/catálogo/fonte alterados e evidência inválida falham
fechados como INCOMPLETA. Falha observada em qualquer critério selecionado reprova.
Falta de autorização mantém incompleto. A aprovação é avaliação de escopo, não
autorização de deploy nem prova contra adulteração por quem controla os arquivos.

## Gate estrito de release

`scripts/release_gate.py` e sua suíte foram reutilizados da skill local
`production-readiness-auditor` (snapshot 22/10/2026). São incluídos para portabilidade;
não exigem instalar aquela skill. Preservar créditos e contrato ao atualizar.

O runner **executa** os comandos da política: revisar argv, imports, rede e destino
de dados antes de rodar. Sem shell implícito, mas programas explícitos ainda podem
ser destrutivos. Ele não é sandbox e não deve executar políticas não confiáveis.
Exige repositório Git limpo, HEAD completo revisado, relatório de revisão não vazio
versionado e pasta nova externa de evidências. Não fazer commit só para contornar
gate sem autorização. Política JSON `version: 1`, `checks`, `review`:

- `checks`: IDs únicos lowercase/hífen, `kind` build/lint/types/tests/regression,
  `argv` lista, timeout positivo opcional. Todas as cinco categorias declaradas.
  build/lint/types podem ter `not_applicable` justificado em vez de argv.
- tests/regression não podem ser dispensados; exigem `junit` relativo à pasta do
  check. Configurar reporter nativo para `{evidence_dir}/junit.xml` ou variável
  `QA_EVIDENCE_DIR`. Nunca converter exit 0 em casos fictícios.
- `review`: `completed: true` só após revisão real, `revision` HEAD completo,
  `evidence` caminho relativo ao repo, `limitations` e `findings` listas. Achados
  P0/P1 abertos bloqueiam; P2 aberto exige `release_decision`, `owner`, `rationale`.

```sh
python3 scripts/release_gate.py --repo /projeto --policy /externo/politica-revisada.json --out /externo/run-novo
```

Aceita subconjunto conservador JUnit com casos reais; rejeita zero casos,
falhas/erros/skips, contagens divergentes e marcadores conhecidos de flaky/retry.
Runner sem JUnit requer adaptar/testar parser nativo ou manter release não verificado.
Verifica fonte e política antes/depois, arquiva logs/hashes e report.json.
Exit 0 APROVADO, 1 REPROVADO, 2 NÃO VERIFICADO (equivale a INCOMPLETA nesta skill).

Para prepare_release/deploy, `assess` exige também `release_report`, objeto com
`path` relativo à pasta de results e `sha256` do report.json produzido pelo runner.
Executar o runner em uma subpasta nova dessa pasta, fora do projeto. O assessment
confere aprovação, repositório/revisão limpa, revisão técnica, logs e JUnits/hashes
do relatório. Plano/results ausentes ou só observação não aprovam release. Atualizar
o plano depois de qualquer mudança de fonte, executando o runner na mesma revisão.
Ambos os conjuntos de gates precisam estar satisfeitos. Só vira bloqueio técnico de publicação
quando pipeline/branch exigirem esses checks na mesma revisão/artefato; essa
configuração externa exige autorização. Não há CI/CD ativo neste pacote local.

## Verificar o pacote

```sh
python3 -m unittest discover -s tests -v
python3 scripts/test_release_gate.py
```

JUnit com failure/error/skipped fora de testcase é rejeitado, inclusive erro de
setup de suite. Formatos não reconhecidos devem falhar fechados, não ser ignorados.

Fixtures são descartáveis, sintéticas, sem credenciais. Resultados de infraestrutura
não aprovam Atria ou qualquer produto. Testes comportamentais de ativação e piloto
estão documentados em validation/; reconhecer pendências de integração explicitamente.
