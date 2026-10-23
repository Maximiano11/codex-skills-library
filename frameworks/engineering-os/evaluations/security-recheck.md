# Rechecagem independente de segurança

Data: 23/10/2026. Resultado: **APROVADA exclusivamente a correção dos três comportamentos reproduzidos na avaliação anterior, no ambiente POSIX local**. Nenhum dos três achados permaneceu reproduzível nestes cenários. Não é aprovação abrangente de release nem certificação de segurança.

## Escopo e método

A skill `skills/security-auditor/SKILL.md` foi reaplicada com os mesmos limites. Foram lidos os componentes atuais de instalação, validação operacional, fingerprint e execução. O relato do autor e os testes adicionados não foram usados como prova: as reproduções abaixo foram construídas e executadas independentemente, com assertions reais e fixtures sintéticas descartáveis. Não houve leitura de oráculos, outras avaliações ou dos novos testes, nem rede, subagentes, instalação global ou dados reais. O relatório histórico não foi alterado.

O pacote sintético de S1 atende aos invariantes estruturais atuais (13 skills e nove workflows), com conteúdo demonstrativo. Não se afirma que implementa o framework. Ele exercita transações e validação estrutural, sem executar seu conteúdo.

## Resultados

| Achado anterior | Verificação | Efeito observado |
| --- | --- | --- |
| S1/P1 — atualização truncada | Instalar pacote sintético estruturalmente válido; tentar update com somente VERSION/LICENSE/README; comparar todos os bytes | Update recusado antes do plano; instalação/estado intactos; doctor continua `ok` |
| S1/P1 — diagnóstico estrutural | Remover entrypoint da fixture e omiti-lo do manifesto, simulando estado histórico incompleto | Doctor retorna `drift` e `incomplete-or-invalid-runtime-package` |
| S2/P2 — modo ignorado | Coletar VALIDATED; chmod 0700→0600; verificar; tentar mesmo argv | Fingerprint muda; gate vira `PARTIALLY_VALIDATED` com `stale-source-or-profile`; execução dá `PermissionError`; modo restaurado permite VALIDATED |
| S3/P2 — filho sobrevive ao timeout | Confirmar início do filho; exceder timeout; aguardar além do atraso do filho | Check `not_verified`; gate `PARTIALLY_VALIDATED`; nenhuma alteração tardia |
| S3 — saída normal | Pai termina com exit 0 deixando filho iniciado | Gate VALIDATED; nenhuma alteração tardia; limpeza do grupo também no sucesso |

Locais atuais: `adapters/codex/install.py:98-101` e `294-298`; `core/engineering_os/validation.py:14-26`; `core/engineering_os/util.py:74-79`; `core/engineering_os/gates.py:16-38` e `214-216`.

Hashes conferidos antes e após a execução, sem alteração durante a reprodução:

```text
372d4390b618b731d8902d4897f493cc7f9421db90f58a00a8f408fa8f3182fc  adapters/codex/install.py
efe760a4e136ecd282a5a747ffbcf6a4285d58846e143ed47658a204af2a7917  core/engineering_os/validation.py
31d685aeaa07eb25414339efc39338e41c80bbb91b1af7b8ac72c8f12f8ff14b  core/engineering_os/util.py
db83e567e1678196ab186cb64d23d40ed1a072960081fbc177aec07c44cbb031  core/engineering_os/gates.py
```

## Comando executado e saída

O código completo foi executado por `python3 -B`, sem depender dos testes do autor; usa biblioteca padrão. A cópia do interpretador local em S2 é executada somente com `-c pass`. O `-B` evita bytecode no framework.

```sh
python3 -B - <<'PY'
import json, os, pathlib, subprocess, sys, tempfile, time
ROOT=pathlib.Path('/Users/jeversonsolomon/Documents/skills codex/engineering-os')
sys.path[:0]=[str(ROOT/'core'),str(ROOT)]
from adapters.codex.install import Target, plan_install, apply, diagnose
from engineering_os.validation import REQUIRED_SKILLS, REQUIRED_WORKFLOWS, validate_package
from engineering_os.gates import collect, verify
from engineering_os.util import ContractError, digest, fingerprint

def snapshot(root):
    return {p.relative_to(root).as_posix():digest(p.read_bytes())
            for p in root.rglob('*') if p.is_file()}

with tempfile.TemporaryDirectory(prefix='eos-security-recheck-') as tmp:
    b=pathlib.Path(tmp); pkg=b/'package'; pkg.mkdir()
    essential=['LICENSE','README.md','scripts/eos.py','policies/governance.md',
      'core/engineering_os/__init__.py','core/engineering_os/cli.py',
      'core/engineering_os/util.py','core/engineering_os/gates.py',
      'core/engineering_os/orchestrator.py','core/engineering_os/validation.py',
      'adapters/codex/install.py']
    for rel in essential:
        p=pkg/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text('# synthetic\n')
    (pkg/'VERSION').write_text('1.0.0\n')
    for name in REQUIRED_SKILLS:
        folder=pkg/'skills'/name; (folder/'agents').mkdir(parents=True)
        (folder/'SKILL.md').write_text(f'---\nname: {name}\ndescription: synthetic\n---\nSynthetic.\n')
        (folder/'agents/openai.yaml').write_text('synthetic: true\n')
    (pkg/'workflows').mkdir()
    for name in REQUIRED_WORKFLOWS:
        item={'schema_version':1,'id':name,'activation':['synthetic'],
          'skills':['engineering-os'],'steps':[{'id':'inspect','depends_on':[],
          'action':'Synthetic inspection'}],'approval':['synthetic'],
          'stop':['synthetic'],'outputs':['synthetic'],'mode_rule':'synthetic'}
        (pkg/'workflows'/(name+'.json')).write_text(json.dumps(item))
    assert validate_package(pkg)['passed']
    target=Target(home=b/'home'); apply(target,plan_install(pkg,target)[0])
    assert diagnose(target)['integrity']=='ok'
    before=snapshot(target.root); broken=b/'incomplete'; broken.mkdir()
    for name in ('VERSION','LICENSE','README.md'):
        (broken/name).write_bytes((pkg/name).read_bytes())
    try:
        plan_install(broken,target,update=True)
        raise AssertionError('Truncated update unexpectedly accepted')
    except ContractError as error:
        refusal=str(error)
    assert snapshot(target.root)==before
    assert diagnose(target)['integrity']=='ok'
    print('S1-update',json.dumps({'refused':refusal,'installation_bytes_unchanged':True,
      'doctor_after_rejection':'ok'}))
    # Historical incomplete manifest: omission of the missing entrypoint.
    state=json.loads(target.state_path.read_text()); rel='engineering-os/runtime/scripts/eos.py'
    del state['files'][rel]; target.path(rel).unlink(); target.state_path.write_text(json.dumps(state))
    diagnosis=diagnose(target)
    assert diagnosis['integrity']=='drift'
    assert 'incomplete-or-invalid-runtime-package' in diagnosis['drift']
    print('S1-doctor',json.dumps({'integrity':diagnosis['integrity'],'drift':diagnosis['drift']}))

    project=b/'mode-project'; project.mkdir(); program=project/'check'
    program.write_bytes(pathlib.Path(sys.executable).resolve().read_bytes()); program.chmod(0o700)
    profile={'schema_version':1,'checks':[{'id':'accept','purpose':'acceptance',
      'kind':'command','required':True,'argv':['./check','-c','pass']}]}
    evidence=b/'mode-evidence'; initial=collect(project,profile,evidence,allow_exec=True)
    assert initial['verdict']['state']=='VALIDATED'
    before=fingerprint(project); program.chmod(0o600)
    assert before != fingerprint(project)
    stale=verify(project,profile,evidence)
    assert stale['state']=='PARTIALLY_VALIDATED' and 'stale-source-or-profile' in stale['pending']
    try:
        subprocess.run(['./check','-c','pass'],cwd=project,check=True)
        raise AssertionError('Non-executable program unexpectedly ran')
    except PermissionError:
        pass
    program.chmod(0o700); restored=verify(project,profile,evidence)
    assert restored['state']=='VALIDATED'
    print('S2',json.dumps({'initial':'VALIDATED','chmod_invalidated_fingerprint':True,
      'after_chmod':stale,'actual_execution':'PermissionError','restored_mode':restored['state']}))

    assert os.name=='posix', 'Process-group recheck requires POSIX'
    for variant in ('timeout','normal-exit'):
        project=b/variant; project.mkdir(); (project/'source.txt').write_text('before')
        ready=b/(variant+'-ready')
        child=('import pathlib,time,sys;pathlib.Path(sys.argv[1]).write_text("ready");'
          'time.sleep(0.5);pathlib.Path("source.txt").write_text("after")')
        parent=('import pathlib,subprocess,sys,time;'
          'subprocess.Popen([sys.executable,"-c",sys.argv[1],sys.argv[2]]);'
          'end=time.monotonic()+0.15;'
          '\nwhile not pathlib.Path(sys.argv[2]).exists() and time.monotonic()<end: time.sleep(0.005)\n'
          + ('time.sleep(2)' if variant=='timeout' else ''))
        profile={'schema_version':1,'checks':[{'id':'accept','purpose':'acceptance',
          'kind':'command','required':True,'argv':[sys.executable,'-c',parent,child,str(ready)],
          'timeout':0.25}]}
        result=collect(project,profile,b/(variant+'-evidence'),allow_exec=True)
        assert ready.exists(), 'Child did not start; inconclusive reproduction'
        at_return=(project/'source.txt').read_text(); time.sleep(0.7)
        later=(project/'source.txt').read_text()
        assert at_return==later=='before', 'Child remained active after collection'
        expected='PARTIALLY_VALIDATED' if variant=='timeout' else 'VALIDATED'
        assert result['verdict']['state']==expected
        print('S3-'+variant,json.dumps({'child_started':True,
          'check':result['checks'][0]['status'],'gate':result['verdict']['state'],
          'source_at_return':at_return,'source_after_0_7s':later}))
print('ALL_INDEPENDENT_ASSERTIONS_PASSED')
PY
```

Saída real:

```text
S1-update {"refused": "Incomplete operational package: scripts/eos.py", "installation_bytes_unchanged": true, "doctor_after_rejection": "ok"}
S1-doctor {"integrity": "drift", "drift": ["incomplete-or-invalid-runtime-package"]}
S2 {"initial": "VALIDATED", "chmod_invalidated_fingerprint": true, "after_chmod": {"state": "PARTIALLY_VALIDATED", "failed": [], "pending": ["stale-source-or-profile"], "critical_findings": false, "scope": "configured local mandatory criteria only; no deployment authorization"}, "actual_execution": "PermissionError", "restored_mode": "VALIDATED"}
S3-timeout {"child_started": true, "check": "not_verified", "gate": "PARTIALLY_VALIDATED", "source_at_return": "before", "source_after_0_7s": "before"}
S3-normal-exit {"child_started": true, "check": "passed", "gate": "VALIDATED", "source_at_return": "before", "source_after_0_7s": "before"}
ALL_INDEPENDENT_ASSERTIONS_PASSED
```

Houve uma chamada inicial de preparação rejeitada pelo parser do shell por colisão de delimitador de heredoc, antes da execução da reprodução. A chamada corrigida acima terminou com exit 0 e todas as assertions passaram; não se registrou a tentativa rejeitada como teste aprovado.

## Limites

- Escopo incremental: não se repetiu toda a auditoria nem se executou a suíte do autor; os três achados foram rechecados independentemente.
- S1 comprova validação estrutural e preservação dos bytes na recusa. Não avalia autenticidade/procedência do pacote, semântica do código distribuído ou perda de energia.
- S2 cobre modo de arquivo regular. ACL, proprietário, permissões de diretórios, xattrs e mudanças externas em alvos de symlink não foram testados.
- S3 cobre filhos no grupo POSIX. Windows, processos que deliberadamente criem outra sessão/grupo, limites de recursos e isolamento de comandos maliciosos não foram testados. A ferramenta continua sem sandbox.
- A espera de 0,7 s excede o atraso de 0,5 s dos filhos. O arquivo de confirmação comprova que cada filho iniciou, evitando conclusão baseada em falha de lançamento.
- Nenhuma correção foi aplicada. O único novo artefato persistente é este relatório. Sem autorização adicional de deploy, produção ou dados reais.
