# Instalação, atualização e remoção

Requer Python 3.10+. Executar comandos a partir da raiz do pacote fonte. Testes desta
entrega foram feitos no ambiente registrado em validation.md; não se presume execução
em Windows/Linux apenas por usar pathlib e argv portáveis.

```sh
python3 -B scripts/eos.py validate-package
python3 -B scripts/eos.py install --dry-run
python3 -B scripts/eos.py install
python3 -B scripts/eos.py doctor
```

O destino global padrão é `$CODEX_HOME` quando não vazio, caso contrário `~/.codex`.
Use `--codex-home CAMINHO` para outro perfil explicitamente. O runtime autocontido fica
em `engineering-os/runtime`, estado em `engineering-os/install.json` e skills em `skills/`.
A descoberta desses caminhos deve ser confirmada no runtime Codex utilizado; runtimes
que não descubram o diretório precisam de adaptação explícita, sem duplicar skills.

Instalação específica em projeto, sem tocar o perfil global:

```sh
python3 -B scripts/eos.py install --project /caminho/projeto --dry-run
python3 -B scripts/eos.py install --project /caminho/projeto
python3 -B scripts/eos.py doctor --project /caminho/projeto
```

No projeto, usa `.agents/skills/` e `.engineering-os/`. Cada projeto pode manter seu
perfil JSON de verificações e passá-lo explicitamente a `run`/`gate` com `--profile`.
O instalador não escolhe a política nem executa comandos encontrados no projeto.

## Preservação e controle

O dry-run não cria diretórios, lock, backup ou arquivo. Pacote operacional completo é
validado antes do planejamento. Instalação existente com conteúdo idêntico é idempotente.
Diferenças do pacote exigem `update`, inclusive na mesma versão. Arquivo existente não
gerenciado causa conflito; não há `--force`. A única especialidade emprestável é
prompt-engineer reconhecível, preservada como pasta inteira. Empréstimo é explicitado
no estado e o uninstall não remove seu conteúdo.

O adaptador acrescenta um bloco delimitado ao AGENTS ativo: usa AGENTS.override.md se
ele já for não vazio, caso contrário AGENTS.md. Não altera config.toml, hooks, modelos,
credenciais ou outras preferências. Conteúdo fora do bloco fica preservado. Um override
criado posteriormente é diagnosticado como sombreamento; precisa de revisão explícita.

Antes de qualquer escrita, o instalador confere precondições, adquire lock e grava cópias
dos arquivos substituídos/removidos em backups privados com journal e hashes. Também
reconfere antes de cada operação. Links simbólicos no destino relativo ou pacote são
recusados. O caminho raiz explícito é canonicalizado, não tratado como isolamento.

```sh
python3 -B scripts/eos.py update --dry-run
python3 -B scripts/eos.py update
```

Usar o novo pacote fonte para atualizar. Downgrade é recusado; mudanças de versão maior
exigem revisar a migração e passar `--allow-major`. O flag não prova autorização humana.
Arquivos gerenciados alterados localmente bloqueiam update/uninstall antes de remover
qualquer arquivo. Compare com backup e decida manualmente como preservar a adaptação;
não apague alterações só para fazer o diagnóstico ficar verde.

```sh
python3 -B scripts/eos.py uninstall --dry-run
python3 -B scripts/eos.py uninstall
```

Uninstall remove somente bytes gerenciados intactos e o bloco exato de instrução.
Arquivos alheios, skills emprestadas, relatórios e backups ficam preservados. Diretórios
vazios podem permanecer. Execute uninstall pelo pacote fonte, pois o runtime gerenciado
será removido. Não existe daemon ou ação remota de desinstalação.

Se o processo for interrompido abruptamente, examine o journal de backup e o lock.
O journal registra paths, existência e hashes; cada backup de arquivo é nomeado pelo
SHA-256 do path relativo. Restaure apenas arquivos confirmados, preservando edições
concorrentes, e só então remova manualmente um lock comprovadamente obsoleto. Não há
recovery automático nem garantia contra falha de energia. Faça cópia dos artefatos
antes de qualquer recuperação destrutiva.
