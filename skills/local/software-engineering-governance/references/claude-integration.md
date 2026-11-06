# Integração Claude Code

Equivalências com a [integração Codex](codex-integration.md):

| Codex | Claude Code |
| --- | --- |
| `AGENTS.md` / `AGENTS.override.md` | `CLAUDE.md` (projeto), `~/.claude/CLAUDE.md` (global), `CLAUDE.local.md` |
| `$CODEX_HOME/skills/<nome>` | `~/.claude/skills/<nome>` (global) ou `.claude/skills/<nome>` (projeto) |
| `$skill-name` | `/skill-name` ou ativação automática pela `description` |
| hooks em `.codex/hooks.json` | `hooks` em `.claude/settings.json` |
| `codex_runtime.py` | Não se aplica; usar `claude -p "..."` para execução não interativa |

Ativação persistente: adicionar o conteúdo de `assets/AGENTS.governance.md` (ou
`AGENTS.global-governance.md`) ao `CLAUDE.md` correspondente, sem duplicar blocos.
`CLAUDE.md` orienta o agente; não impõe proteção no servidor nem bloqueia deploy.
