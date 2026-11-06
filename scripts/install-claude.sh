#!/usr/bin/env sh
# Instala as skills de skills/local no Claude Code como symlinks (git pull atualiza).
# Uso: scripts/install-claude.sh [destino]   (padrão: ~/.claude/skills)
set -eu
ROOT=$(cd "$(dirname "$0")/.." && pwd)
DEST=${1:-$HOME/.claude/skills}
SKIP="migrate-to-codex"   # específica do Codex
mkdir -p "$DEST"
for d in "$ROOT"/skills/local/*/; do
  n=$(basename "$d")
  case " $SKIP " in *" $n "*) continue;; esac
  t="$DEST/$n"
  if [ -e "$t" ] && [ ! -L "$t" ]; then echo "pulando (já existe): $n"; continue; fi
  ln -sfn "${d%/}" "$t" && echo "ok: $n"
done
