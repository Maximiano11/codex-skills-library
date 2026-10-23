# Integração Codex

Ambiente observado em 22/10/2026: aplicativo ChatGPT/Codex desktop, macOS, shell zsh.
Existem dois executáveis: `codex` no PATH é 0.133.0; o runtime fornecido pelo app
em `CODEX_CLI_PATH` é **0.163.0-alpha.11**. Esses são números das CLIs, não uma
versão independente da interface desktop. Python do sistema executa os helpers.
Permissões da sessão não ampliam a autorização humana para sistemas reais.

Fontes oficiais abertas em 22/10/2026:
[Agent Skills](https://learn.chatgpt.com/docs/build-skills) e
[AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md).
Estrutura suportada: pasta com SKILL.md (`name`, `description` no frontmatter),
referências/scripts/assets opcionais e metadados em agents/openai.yaml.

## Instalação atual e ativação

Instalada em `.agents/skills/software-engineering-governance` deste workspace.
A localização é suportada para skills do projeto. `AGENTS.md` local orienta a
ativação em tarefas de software. Invocação explícita: `$software-engineering-governance`.
Seleção implícita depende de descrição/contexto e permite `allow_implicit_invocation`;
instalação por si só não garante execução em toda tarefa. Mudanças são detectáveis
pelo Codex; se não aparecerem, iniciar nova sessão/reiniciar conforme documentação.

A evidência de descoberta/ativação deve vir de uma sessão/runtime nova, não somente
da existência de arquivos. Os dois modos foram validados em novas sessões: a
invocação explícita leu SKILL.md e a automática aplicou o bloco AGENTS.md sem nome
da skill no prompt. Ambos executaram testes e reprovaram um fixture defeituoso.
Consultar [evidências atuais](../validation/codex-integration-2026-10-22/report.md).
O registro anterior de falha permanece histórico em validation/activation-report.md.

## Executar com o runtime correto

O teste inicial usava `codex` do PATH (0.133.0), que recusou o modelo configurado.
Com o runtime do aplicativo (0.163.0-alpha.11), o mesmo modelo `gpt-6.1-sol` e o mesmo
prompt funcionaram. Isso foi reproduzido; não foi necessário trocar modelo,
credencial ou configuração global. A seleção do executável foi corrigida no
launcher local, mantendo a instalação antiga no PATH intacta.

Resolver caminhos abaixo a partir desta pasta da skill:

```sh
python3 scripts/codex_runtime.py --print-runtime
python3 scripts/codex_runtime.py -- --version
python3 scripts/codex_runtime.py -- exec --ephemeral --skip-git-repo-check --sandbox read-only -C /projeto '$software-engineering-governance Analise esta demanda'
python3 scripts/codex_runtime.py -- exec --ephemeral --skip-git-repo-check --sandbox read-only -C /projeto 'Analise esta demanda conforme as instrucoes do projeto'
```

O último comando pressupõe a skill e o bloco AGENTS.md instalados no projeto alvo
ou no escopo global do usuário.
`read-only` é apropriado para auditoria/verificação; escolher as permissões adequadas
ao trabalho autorizado quando for implementar. O launcher não altera permissões,
modelo ou argumentos passados ao Codex e não é uma camada de segurança.

Ordem de resolução: `--codex /caminho/executavel` explícito; `CODEX_CLI_PATH` fornecido
por este desktop; bundle macOS conhecido quando presente; `codex` do PATH como
fallback. A variável é um dado observado deste ambiente, não uma API universal
prometida. Caminho explícito/ambiental inválido falha, sem fallback silencioso.
Fora deste ambiente, passar o executável compatível explicitamente:

```sh
python3 scripts/codex_runtime.py --codex /caminho/codex -- exec --sandbox read-only -C /projeto 'Analise a demanda'
```

O fallback PATH não garante compatibilidade de versão/modelo. Conferir executável,
versão e `model/list` no runtime em uso. Catálogo/conta/cliente determinam modelos
disponíveis; não fixar substitutos nem trocar o modelo escolhido sem necessidade.
Fontes oficiais: [CLI](https://learn.chatgpt.com/docs/cli/reference),
[model/list](https://learn.chatgpt.com/docs/app-server#models) e
[modelos](https://learn.chatgpt.com/docs/models).

## Reutilizar em outro repositório

Com autorização para configurar o repositório alvo, copiar **esta pasta inteira**
para `<repo>/.agents/skills/software-engineering-governance/`. Acrescentar o bloco
`assets/AGENTS.governance.md` ao AGENTS.md existente, sem sobrescrever outras
instruções nem duplicar marcadores. Resolver conflitos com instruções específicas.
O bloco é relativo à raiz onde a skill foi instalada.

Para instalação pessoal entre projetos, copiar esta pasta inteira para
`~/.agents/skills/software-engineering-governance` (escopo USER documentado).
Não sobrescrever uma instalação existente sem revisar diferenças. O desktop também
expõe skills legadas em `~/.codex/skills`; evitar duplicar a instalação nos dois locais.
Com autorização específica, acrescentar [bloco global](../assets/AGENTS.global-governance.md)
ao `~/.codex/AGENTS.md`, preservando o conteúdo e sem duplicar marcadores. Se existir
`AGENTS.override.md` global não vazio, ele tem precedência: examinar e integrar a
orientação no arquivo efetivamente ativo. Instruções específicas dos projetos prevalecem.
Não copiar o bloco local com caminho relativo para o AGENTS global.

A integração original foi validada sem alterações globais. A instalação global
foi autorizada posteriormente em 22/10/2026. Confirmar `skills/list` em um projeto
sem cópia local e testar uma nova sessão sem mencionar a skill no prompt. Guardar
backup do AGENTS e hashes de preservação; instruções já carregadas numa sessão podem
exigir nova tarefa/sessão para refletir a atualização. Se a skill não aparecer,
reiniciar o Codex conforme a documentação.

## Atualizar e remover

Atualizar: preservar evidências e adaptações locais; comparar versão/CHANGELOG,
validar pacote novo em pasta temporária, substituir apenas a pasta da skill após
revisar diff e executar testes. Novo catálogo/versão requer novo plano de avaliação.
Evitar duas cópias de mesmo nome no mesmo escopo de descoberta.

Desinstalar: remover apenas a pasta instalada e o bloco delimitado
`software-engineering-governance:start/end` do AGENTS.md alvo. Preservar instruções,
ADRs, evidências e relatórios do projeto. Não remover bloco QA compartilhado usado
por outra skill. Nenhum daemon, hook global ou configuração remota é instalado.

## Responsabilidades e limites

Workflows implementam os seis papéis lógicos sem dependência de API multiagente.
Se execução paralela autorizada estiver disponível, evitar escrita concorrente,
separar implementação de revisão quando exigido e consolidar evidências. Ausência
de agentes especializados não torna verificações facultativas.

Reutilizar runners reais do projeto. Git: inspecionar status/diff e preservar
trabalho existente; commits/branches/PRs somente quando autorizados pelo contexto.
Nunca reescrever histórico ou fazer force push sem autorização explícita.
GitHub: propor checks/branch protection e dependência do deploy; não presumir
permissão remota. Não há API fictícia de hooks, skill-on-every-task ou autoaprovação.

Decisões persistem em ADRs, contratos e docs versionados, não só na conversa.
Ler contexto relevante na próxima tarefa e corrigir divergências documentais reais.
