# Avaliação independente: security-auditor aplicada ao Engineering OS

Data: 23/10/2026. Resultado da auditoria local: **REPROVADA no escopo verificado**, com um P1 de integridade/disponibilidade e dois P2 reproduzidos. Não é aprovação ou auditoria abrangente de release.

## Escopo e método

Skill lida e aplicada: `skills/security-auditor/SKILL.md`. Código examinado: `core/engineering_os/`, `adapters/codex/` e `scripts/`. Os contratos foram inferidos do próprio código, inclusive limites expressos; não foram lidos oráculos, casos de avaliações ou relatórios de outros avaliadores. Não houve subagentes, rede externa, instalação global, alteração do framework ou dados reais. Todas as instalações e execuções usaram diretórios temporários descartáveis e conteúdo sintético. O único artefato persistente criado nesta avaliação é este relatório.

Fronteiras investigadas: pacote → arquivos gerenciados/instruções; estado de instalação → atualização/remoção/diagnóstico; perfil/atestados → comandos locais/JUnit; árvore de código → fingerprint → estado de gate. O framework declara que não oferece sandbox e que evidência local pode ser forjada por quem possui escrita; esses limites não foram tratados como vulnerabilidades novas.

Critérios de aceite desta avaliação: achados devem ter localização, precondição, reprodução executada, esperado/observado, impacto delimitado e mitigação mínima; proteções negativas e superfícies não verificadas devem ser explícitas. Risco do alvo: alto, porque instala instruções/código e produz estados de validação.

Revisão auditada, identificada pelos bytes dos principais arquivos:

```text
3688b97252490ae1d041f916fe8fb0e23b7133ca9cc342cf030087f31e3ded24  core/engineering_os/util.py
89d622c113594e169fe3ec4b3d54889c6f91e8396df045b9f5061c78e9bbabcb  core/engineering_os/gates.py
8984f431f823a94784250c6a96691793132e997b0a7529d2eae4c21eabcb9feb  adapters/codex/install.py
61ad22f2f0f58e73a9a09e15b2d391cee579d85bc863e1c61bb84cd5dd9e86a6  scripts/eos.py
7e7df30dd7ba2c7b1cba81de50b5b7673e2bcb4ae3e1b8748a9b5bc09ee1c63c  scripts/test.py
```

## S1 — P1: atualização aceita distribuição incompleta, remove o runtime e informa integridade correta

**Local:** `adapters/codex/install.py:55-75`, `98-99`, `149-154`, `276-295`.

**Precondição:** operador aponta `update` para diretório de pacote truncado/incompleto que ainda contém `VERSION`, `LICENSE` e `README.md`. Não é necessário editar o estado da instalação, forjar hashes ou explorar uma corrida.

`package_files()` exige apenas esses três arquivos; `os.walk()` de partes ausentes não rejeita o pacote. `plan_install()` interpreta todos os arquivos anteriormente gerenciados ausentes como remoções legítimas. A transação termina com novo manifesto contendo apenas os três arquivos. `diagnose()` compara os arquivos desse novo manifesto e retorna `integrity: ok`, mesmo sem o entrypoint indicado no AGENTS.

**Esperado:** recusar distribuição incompleta antes de qualquer remoção, preservando a instalação anterior; o diagnóstico deve detectar ausência de entrypoints/estrutura essenciais.

**Observado:** na reprodução, foram removidos `runtime/core/engineering_os/__init__.py`, `runtime/scripts/eos.py`, `runtime/skills/engineering-os/SKILL.md` e a skill ativa `skills/engineering-os/SKILL.md`; `runtime_entrypoint_exists=false`, `owned_files=3`, mas `doctor` informou `installed=true`, `integrity=ok`, `drift=[]`.

**Impacto demonstrado:** perda de disponibilidade da instalação gerenciada e diagnóstico de saúde incorreto após uma atualização aceita. Não foi demonstrada execução remota ou comprometimento de credenciais. Classificado P1 porque quebra o fluxo essencial de atualização/uso, inclusive sem adulteração maliciosa.

**Mitigação mínima:** validar presença e tipo das partes/arquivos obrigatórios antes de construir remoções, reutilizando os invariantes de pacote apropriados. Validar o entrypoint e uma estrutura mínima também em `doctor`. Acrescentar regressão que atualiza instalação saudável com pacote truncado e comprova recusa sem mudança dos bytes anteriores. Não foram aplicadas correções.

## S2 — P2: mudança de permissão executável não invalida evidência

**Local:** `core/engineering_os/util.py:60-82`, especialmente `73-78`; `core/engineering_os/gates.py:188-190`.

**Precondição:** uma verificação obrigatória executa programa local versionado, e a permissão de execução desse arquivo muda após a coleta. O conteúdo permanece idêntico; não se altera `record.json`.

O fingerprint registra somente os bytes de arquivos regulares e ignora os bits de modo. Uma execução obrigatória pode deixar de ser possível sem que `verify()` considere a fonte obsoleta.

**Esperado:** alteração dos metadados que governam a execução local deve invalidar a evidência correspondente ou manter explicitamente esse aspecto como não verificado.

**Observado:** programa nativo local copiado para fixture com modo `0700` produziu `VALIDATED`. Após `chmod(0600)`, o fingerprint continuou igual e `verify()` devolveu `VALIDATED`; tentar executar o mesmo `argv` resultou em `PermissionError`. Como controle, alterar os bytes fez `verify()` retornar `PARTIALLY_VALIDATED`.

**Impacto demonstrado:** falso estado de atualidade para critério obrigatório que já não pode ser executado. Não é prova de falha no sistema de deploy externo nem de adulteração arbitrária da evidência.

**Mitigação mínima:** incluir ao menos bits executáveis/tipo de arquivo na identidade da fonte, documentando os metadados cobertos, e testar `chmod` sem alteração de conteúdo. Não foram aplicadas correções.

## S3 — P2: timeout não encerra descendentes da verificação

**Local:** `core/engineering_os/gates.py:141-148`, `175-182`.

**Precondição:** comando local autorizado inicia subprocesso e excede o timeout. A execução sem sandbox é um limite documentado; o achado específico é a limpeza incompleta no caminho de timeout.

`subprocess.run(..., timeout=...)` encerra o processo direto, sem gerenciar um grupo de processos. Descendentes podem continuar usando o diretório do projeto e os descritores herdados após `collect()` terminar.

**Esperado:** timeout deve encerrar/aguardar a árvore de processos iniciada pela verificação, ou a ferramenta deve registrar explicitamente que há processos remanescentes antes de concluir a coleta.

**Observado:** processo filho aguardou 0,5 s e alterou `source.txt` de `before` para `after`. O pai foi interrompido em 0,1 s; `collect()` retornou com `source.txt=before`, e 0,7 s depois o conteúdo era `after`.

**Impacto demonstrado:** efeitos locais tardios e possível interferência em comandos posteriores; recursos e tarefas podem continuar ativos após o timeout. **Não foi demonstrado bypass do gate:** o check ficou `not_verified` e o estado foi `PARTIALLY_VALIDATED`. A mutação posterior é detectável por nova verificação do fingerprint.

**Mitigação mínima:** iniciar e encerrar um grupo/sessão de processos por check e aguardar sua finalização, com tratamento equivalente nas plataformas suportadas. Documentar limites de descendentes que se desvinculem deliberadamente. Acrescentar regressão que aguarda além do atraso do filho e verifica ausência de efeitos tardios. Não foram aplicadas correções.

## Reprodução executada dos três achados

Executar a partir de qualquer diretório com Python 3 compatível e os bytes auditados acima. O exemplo usa somente a biblioteca padrão e fixtures temporárias; `-B` evita bytecode no framework. O programa copiado em S2 é o próprio interpretador local, executado apenas com `-c pass`.

```sh
python3 -B - <<'PY'
import json, pathlib, subprocess, sys, tempfile, time
ROOT = pathlib.Path('/Users/jeversonsolomon/Documents/skills codex/engineering-os')
sys.path[:0] = [str(ROOT/'core'), str(ROOT)]
from adapters.codex.install import Target, plan_install, apply, diagnose
from engineering_os.gates import collect, verify
from engineering_os.util import fingerprint

with tempfile.TemporaryDirectory(prefix='eos-security-forward-') as tmp:
    b = pathlib.Path(tmp)
    pkg = b/'package'; pkg.mkdir()
    for name, data in {'VERSION':'1.0.0', 'LICENSE':'synthetic',
                       'README.md':'synthetic'}.items():
        (pkg/name).write_text(data)
    for rel, data in {'core/engineering_os/__init__.py':'',
                      'scripts/eos.py':'print("synthetic runtime")\n',
                      'skills/engineering-os/SKILL.md':
                      '---\nname: engineering-os\ndescription: synthetic\n---\n'}.items():
        p = pkg/rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(data)
    target = Target(home=b/'home')
    apply(target, plan_install(pkg, target)[0])
    broken = b/'incomplete'; broken.mkdir()
    for name in ('VERSION', 'LICENSE', 'README.md'):
        (broken/name).write_bytes((pkg/name).read_bytes())
    changes, state = plan_install(broken, target, update=True)
    apply(target, changes)
    print('S1', json.dumps({'doctor':diagnose(target),
          'entrypoint_exists':(target.root/'engineering-os/runtime/scripts/eos.py').exists(),
          'removed':[p for p, (_, after) in changes.items() if after is None]}))

    project = b/'mode-project'; project.mkdir()
    program = project/'check'
    program.write_bytes(pathlib.Path(sys.executable).resolve().read_bytes())
    program.chmod(0o700)
    profile = {'schema_version':1, 'checks':[{'id':'accept', 'purpose':'acceptance',
               'kind':'command', 'required':True, 'argv':['./check','-c','pass']}]}
    evidence = b/'mode-evidence'
    initial = collect(project, profile, evidence, allow_exec=True)
    before = fingerprint(project); program.chmod(0o600)
    try:
        subprocess.run(['./check','-c','pass'], cwd=project, check=True)
        actual = 'success'
    except PermissionError:
        actual = 'PermissionError'
    print('S2', {'initial':initial['verdict']['state'],
          'fingerprint_equal':before == fingerprint(project),
          'verify':verify(project, profile, evidence)['state'], 'actual':actual})

    project = b/'timeout-project'; project.mkdir()
    (project/'source.txt').write_text('before')
    child = ('import time,pathlib;time.sleep(0.5);'
             'pathlib.Path("source.txt").write_text("after")')
    parent = ('import subprocess,sys,time;'
              'subprocess.Popen([sys.executable,"-c",sys.argv[1]]);time.sleep(2)')
    profile = {'schema_version':1, 'checks':[
        {'id':'slow', 'purpose':'security', 'kind':'command', 'required':True,
         'argv':[sys.executable,'-c',parent,child], 'timeout':0.1},
        {'id':'accept', 'purpose':'acceptance', 'kind':'command', 'required':True,
         'argv':[sys.executable,'-c','pass'], 'timeout':1}]}
    result = collect(project, profile, b/'timeout-evidence', allow_exec=True)
    at_return = (project/'source.txt').read_text()
    time.sleep(0.7)
    print('S3', {'check':result['checks'][0]['status'],
          'gate':result['verdict']['state'], 'at_return':at_return,
          'later':(project/'source.txt').read_text()})
PY
```

As reproduções foram executadas em chamadas locais reais. A primeira tentativa de S2 usou shell script e já produziu `not_verified` na coleta neste ambiente; ela **não** sustentou o achado. A reprodução conclusiva usou cópia do interpretador nativo e confirmou o resultado acima.

## Controles negativos executados e limites

Foram executados e observados: caminhos `../outside`, caminho absoluto e passagem por symlink rejeitados por `relative_file`; JSON com chave duplicada rejeitado; JUnit com DOCTYPE/entidade e com contagens incoerentes rejeitado; comando sem `allow_exec` rejeitado antes da execução; perfil vazio resultou em `PARTIALLY_VALIDATED`; critério obrigatório falho e achado crítico aberto resultaram em `BLOCKED`; mudança de bytes invalidou a evidência. Esses controles sustentam apenas esses cenários, sem afirmar ausência de outras vulnerabilidades.

Não executados: suíte do framework que poderia carregar avaliações/oráculos fora do escopo; pentest externo; credenciais, rede, produção ou instalações reais; corridas de filesystem e adulteração pelo mesmo usuário; limites de disco/CPU; todas as variantes de XML; testes multiplataforma; rollback com falhas injetadas; ciclos completos de remoção com perda de energia. Instalação/remoção foram revisadas por leitura e a remoção de arquivos durante atualização foi exercitada. Não há declaração de aprovação abrangente do uninstall.

## Avaliação da skill

A skill foi suficiente para orientar fronteiras, rastrear entradas até operações sensíveis e exigir precondições/efeitos demonstrados sem ampliar autorização. A execução distinguiu defeitos de integridade de exploração remota e registrou um teste inicial inconclusivo. Não houve necessidade de scanner externo, dependências novas ou correções para produzir evidência acionável. Isso é uma amostra independente de aplicação da skill, **não** uma avaliação formal de todos os seus casos ou prova geral de comportamento do modelo. Nenhuma correção foi validada nesta revisão.
