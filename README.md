# Codex Skills Library

Biblioteca open source de skills para Codex e do **Engineering OS**: um framework local
para transformar pedidos de software em requisitos verificáveis, selecionar o workflow
adequado e validar a execução com evidências.

| Conteúdo | Quantidade | Disponibilidade |
| --- | ---: | --- |
| Skills com licença aberta | 36 | Código, scripts e recursos incluídos |
| Referências externas | 43 | Somente catálogo; instalação pelo fornecedor |
| Catálogo completo | 79 | Inventário em [CATALOG.md](CATALOG.md) |
| Engineering OS | 13 skills · 9 workflows | Runtime Python, instalador, gates e testes |

**O instalador do Engineering OS instala suas 13 skills, não todas as 36 da biblioteca.**
As demais são opcionais. Plugins referenciados não incluem ferramentas MCP, contas ou
runtimes nativos neste repositório.

## Navegação

- [Instalação global](#instalação-global-do-engineering-os)
- [Exemplos no Codex](#exemplos-de-uso-no-codex)
- [CLI e validação](#cli-e-validação)
- [Skills individuais](#instalar-skills-individuais)
- [Skills incluídas](#skills-incluídas-36)
- [Referências externas](#referências-externas-43)
- [Atualização e remoção](#atualização-e-remoção)
- [Licenças](#licenças)

## Instalação global do Engineering OS

### Requisitos

- Git para clonar este repositório.
- Python **3.10 ou superior**; o framework usa somente a biblioteca padrão.
- Codex instalado para usar as skills no agente. O CLI do Engineering OS também
  funciona de forma independente, sem serviço em nuvem ou credenciais obrigatórias.

Os exemplos de shell abaixo são para macOS/Linux. A entrega foi verificada em macOS;
o funcionamento em Windows/Linux não é afirmado como testado.

### 1. Clonar e conferir o pacote

```sh
git clone https://github.com/Maximiano11/codex-skills-library.git
cd codex-skills-library
python3 --version
python3 -B frameworks/engineering-os/scripts/eos.py validate-package
```

Todos os comandos seguintes partem da raiz deste clone.

### 2. Revisar e instalar

```sh
python3 -B frameworks/engineering-os/scripts/eos.py install --dry-run
python3 -B frameworks/engineering-os/scripts/eos.py install
python3 -B frameworks/engineering-os/scripts/eos.py doctor
```

O destino padrão é `${CODEX_HOME:-$HOME/.codex}`. Para um perfil diferente, passe
`--codex-home /caminho/do/perfil` em `install`, `doctor`, `update` e `uninstall`.
Não é necessário usar `sudo`.

| Destino relativo ao perfil | Conteúdo |
| --- | --- |
| `skills/` | As 13 skills do Engineering OS |
| `engineering-os/runtime/` | Runtime autocontido e CLI `scripts/eos.py` |
| `engineering-os/install.json` | Estado e propriedade dos arquivos instalados |
| `AGENTS.md` ou `AGENTS.override.md` ativo | Bloco delimitado de orientação do Engineering OS |

O instalador preserva instruções fora do seu bloco e não altera `config.toml`, modelos,
credenciais ou hooks. Registra backups das substituições gerenciadas; conflitos com
arquivos alheios interrompem a operação, sem opção `--force`. Uma instalação reconhecida
de `prompt-engineer` pode ser reutilizada e preservada. **Não apague skills existentes
para contornar conflitos:** revise o diagnóstico e o [guia de instalação](frameworks/engineering-os/docs/installation.md).

### 3. Confirmar a ativação no Codex

1. Confirme que `doctor` conclui sem pendências para o perfil instalado.
2. Abra uma nova sessão/tarefa do Codex e confira se `engineering-os` e `prompt-engineer`
   aparecem entre as skills disponíveis. Reinicie o aplicativo se necessário.
3. Em um projeto de teste, envie o exemplo de planejamento abaixo e confirme que o
   agente preserva o modo somente planejamento.

`doctor` verifica a instalação local; ele não comprova sozinho que a sessão do Codex
carregou as skills. O bloco global orienta o agente a aplicar `prompt-engineer` antes
de tarefas de software e usar `engineering-os` para selecionar o workflow necessário.
Skills e `AGENTS.md` são instruções, sem interceptação técnica garantida de mensagens.
Instruções específicas do projeto e autorizações do usuário continuam válidas.
Veja a documentação oficial de [skills](https://learn.chatgpt.com/docs/build-skills) e
[AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

## Exemplos de uso no Codex

Envie os textos abaixo no chat do Codex, dentro do projeto afetado. A chamada explícita
`$engineering-os` torna a seleção visível; com a orientação global instalada, o agente
também pode selecionar as skills automaticamente conforme a tarefa.

### Correção simples de interface

```text
$engineering-os Corrija o espaçamento do botão Salvar no formulário de cadastro.
Preserve o fluxo e a identidade visual. Verifique a alteração na interface real
quando a aplicação estiver disponível e informe o que conseguiu validar.
```

O processo deve ser proporcional: ajuste localizado, revisão e verificação afetada,
sem refatorações adjacentes.

### Nova funcionalidade

```text
$engineering-os Implemente um filtro por status na listagem de pedidos.
Investigue os padrões existentes de filtros e paginação, defina critérios de aceite
com base no pedido e valide os comportamentos afetados. Esclareça decisões de negócio
que não possam ser resolvidas pelo contexto antes de implementar essas partes.
```

### Investigação de bug

```text
$engineering-os Investigue por que a confirmação de pagamento aparece duplicada.
Primeiro reproduza o problema e identifique a causa. Corrija dentro desse escopo
e inclua uma verificação de regressão quando viável. Não opere sobre dados reais.
```

### Auditoria somente leitura

```text
$engineering-os Audite autenticação e autorização deste projeto sem modificar código.
Relacione achados a evidências, indique severidade e diferencie falhas confirmadas
de hipóteses. Não execute exploração contra sistemas reais.
```

### Planejamento sem implementação

```text
$engineering-os Planeje a separação do módulo de faturamento.
Mapeie dependências, riscos, etapas e critérios de aceite. Não altere arquivos
nem implemente o plano nesta tarefa.
```

Explicações, análises, auditorias e planos não autorizam implementação. O framework
seleciona especialidades pertinentes e reutiliza governança/QA disponíveis, sem executar
todas as skills para cada pedido.

## CLI e validação

### Inventariar contexto e gerar um plano

```sh
python3 -B frameworks/engineering-os/scripts/eos.py discover --project /caminho/do/projeto
python3 -B frameworks/engineering-os/scripts/eos.py plan \
  --change frameworks/engineering-os/examples/css-change.json \
  --project /caminho/do/projeto
```

O arquivo de exemplo descreve uma mudança de espaçamento CSS. Adapte pedido e aceite
ao projeto antes de utilizá-lo. `discover` inventaria arquivos e scripts declarados sem
executá-los; `plan` faz triagem determinística, sem interpretar integralmente linguagem
natural ou substituir investigação técnica.

### Workflows disponíveis

| Workflow | Uso |
| --- | --- |
| `feature-development` | Nova funcionalidade |
| `bug-investigation` | Investigação e correção de bug |
| `architecture-change` | Mudança arquitetural |
| `refactoring` | Refatoração |
| `security-review` | Revisão de segurança |
| `quality-audit` | Auditoria de qualidade |
| `release-readiness` | Preparação e avaliação de release |
| `incident-response` | Investigação de incidente |
| `project-bootstrap` | Fundação de um projeto |

### Evidências e gates

Após revisar os comandos, efeitos e critérios do perfil do projeto:

```sh
python3 -B frameworks/engineering-os/scripts/eos.py run \
  --project /caminho/do/projeto --profile /caminho/perfil.json \
  --out /caminho/externo/evidencia-nova --allow-exec
python3 -B frameworks/engineering-os/scripts/eos.py gate \
  --project /caminho/do/projeto --profile /caminho/perfil.json \
  --evidence /caminho/externo/evidencia-nova
```

Crie o perfil conforme os testes e contratos reais do projeto; o
[perfil de exemplo](frameworks/engineering-os/examples/profile.json) documenta o formato.
O diretório de evidências deve ser novo e externo ao projeto. `run` executa os comandos
revisados e não fornece sandbox; `--allow-exec` não concede autorização para produção.
Testes exigem resultados reais de runner, como JUnit; exit code zero sozinho não
comprova testes aprovados. Consulte [uso e contratos](frameworks/engineering-os/docs/usage.md).

| Estado do gate | Significado no escopo configurado | Saída |
| --- | --- | ---: |
| `VALIDATED` | Critérios obrigatórios comprovados | 0 |
| `BLOCKED` | Falha obrigatória ou risco crítico | 1 |
| `PARTIALLY_VALIDATED` | Evidência obrigatória ausente, pendente ou desatualizada | 2 |
| Erro de contrato/IO | Entrada inválida ou falha de operação | 3 |

Esses estados não equivalem a autorização de deploy ou certificação de segurança.

### Verificar o framework

```sh
python3 -B frameworks/engineering-os/scripts/eos.py validate-package
python3 -B frameworks/engineering-os/scripts/eos.py evaluate
python3 -B frameworks/engineering-os/scripts/test.py --out /tmp/engineering-os-tests-novos
```

Escolha um caminho de saída ainda inexistente. Os testes verificam o framework;
não validam automaticamente seu projeto, o comportamento de modelos ou integrações externas.

## Instalar skills individuais

Para skills fora das 13 do Engineering OS, escolha uma entrada na tabela abaixo e
copie **a pasta inteira**, incluindo scripts, referências, assets e licença, para o
diretório de skills descoberto pelo seu Codex. Não copie todas indiscriminadamente.

Exemplo opcional para `brandkit`, no perfil usado por este instalador, a partir da raiz
do clone; interrompe se o destino já existir:

```sh
python3 - <<'PYTHON'
import os
import shutil
from pathlib import Path

source = Path('skills/local/brandkit')
profile = Path(os.environ.get('CODEX_HOME') or Path.home() / '.codex').expanduser()
target = profile / 'skills' / source.name
if target.exists() or target.is_symlink():
    raise SystemExit(f'Destino existente; revise antes de atualizar: {target}')
shutil.copytree(source, target)
print(f'Skill copiada para {target}')
PYTHON
```

Confirme a descoberta em uma nova sessão. Clientes que utilizem outro diretório pessoal
precisam de adaptação explícita; evite duplicar a mesma skill em múltiplos locais.
Instalação manual não acrescenta regras globais ao `AGENTS.md` nem fica sob gerenciamento
do instalador Engineering OS. Scripts de imagens, integrações e outras skills podem exigir
dependências próprias: leia seu `SKILL.md`. Evite copiar skills `system` já fornecidas pelo cliente.

## Skills incluídas (36)

As 13 marcadas **EOS** compõem o Engineering OS. As demais são opcionais.
Os links abrem as instruções completas; as licenças de cada pasta permanecem aplicáveis.

| Skill | Grupo | Licença |
| --- | --- | --- |
| [brandkit](skills/local/brandkit/SKILL.md) | Opcional | MIT |
| [code-reviewer](skills/local/code-reviewer/SKILL.md) | EOS | MIT |
| [database-engineer](skills/local/database-engineer/SKILL.md) | EOS | MIT |
| [design-taste-frontend](skills/local/design-taste-frontend/SKILL.md) | Opcional | MIT |
| [design-taste-frontend-v1](skills/local/design-taste-frontend-v1/SKILL.md) | Opcional | MIT |
| [design-taste-frontend-v2-experimental](skills/local/design-taste-frontend-v2-experimental/SKILL.md) | Opcional | MIT |
| [engineering-os](skills/local/engineering-os/SKILL.md) | EOS | MIT |
| [full-output-enforcement](skills/local/full-output-enforcement/SKILL.md) | Opcional | MIT |
| [gpt-taste](skills/local/gpt-taste/SKILL.md) | Opcional | MIT |
| [high-end-visual-design](skills/local/high-end-visual-design/SKILL.md) | Opcional | MIT |
| [image-to-code](skills/local/image-to-code/SKILL.md) | Opcional | MIT |
| [imagegen](skills/system/imagegen/SKILL.md) | Sistema | Apache-2.0 |
| [imagegen-frontend-mobile](skills/local/imagegen-frontend-mobile/SKILL.md) | Opcional | MIT |
| [imagegen-frontend-web](skills/local/imagegen-frontend-web/SKILL.md) | Opcional | MIT |
| [implementation-standards](skills/local/implementation-standards/SKILL.md) | EOS | MIT |
| [industrial-brutalist-ui](skills/local/industrial-brutalist-ui/SKILL.md) | Opcional | MIT |
| [migrate-to-codex](skills/local/migrate-to-codex/SKILL.md) | Opcional | Apache-2.0 |
| [minimalist-ui](skills/local/minimalist-ui/SKILL.md) | Opcional | MIT |
| [openai-docs](skills/system/openai-docs/SKILL.md) | Sistema | Apache-2.0 |
| [performance-engineer](skills/local/performance-engineer/SKILL.md) | EOS | MIT |
| [product-ux](skills/local/product-ux/SKILL.md) | EOS | MIT |
| [production-readiness-auditor](skills/local/production-readiness-auditor/SKILL.md) | Opcional | MIT |
| [production-reliability](skills/local/production-reliability/SKILL.md) | EOS | MIT |
| [prompt-engineer](skills/local/prompt-engineer/SKILL.md) | EOS | MIT |
| [quality-engineer](skills/local/quality-engineer/SKILL.md) | EOS | MIT |
| [redesign-existing-projects](skills/local/redesign-existing-projects/SKILL.md) | Opcional | MIT |
| [release-manager](skills/local/release-manager/SKILL.md) | EOS | MIT |
| [security-auditor](skills/local/security-auditor/SKILL.md) | EOS | MIT |
| [skill-creator](skills/system/skill-creator/SKILL.md) | Sistema | Apache-2.0 |
| [skill-installer](skills/system/skill-installer/SKILL.md) | Sistema | Apache-2.0 |
| [software-architect](skills/local/software-architect/SKILL.md) | EOS | MIT |
| [software-engineering-governance](skills/local/software-engineering-governance/SKILL.md) | Opcional | MIT |
| [stitch-design-taste](skills/local/stitch-design-taste/SKILL.md) | Opcional | MIT |
| [system-demo-video](skills/local/system-demo-video/SKILL.md) | Opcional | MIT |
| [technical-documentation](skills/local/technical-documentation/SKILL.md) | EOS | MIT |
| [ui-ux-visual-auditor](skills/local/ui-ux-visual-auditor/SKILL.md) | Opcional | MIT |

## Referências externas (43)

As entradas abaixo registram skills disponíveis no ambiente de origem, **sem distribuir
seus arquivos**. Elas não são instaladas por nenhum comando deste README. Obtenha os
plugins pelos canais oficiais do Codex/fornecedor, confirme disponibilidade na sua conta
e habilite as integrações necessárias. A presença no catálogo não garante acesso atual.

| Origem | Skills referenciadas |
| --- | --- |
| `local` | `web-design-guidelines` |
| `plugins/documents` | `documents` |
| `plugins/figma` | `figma-code-connect`, `figma-code-workflows`, `figma-create-new-file`, `figma-design-to-code`, `figma-generate-design`, `figma-generate-diagram`, `figma-generate-library`, `figma-generative-plugins`, `figma-implement-motion`, `figma-shaders`, `figma-spec`, `figma-swiftui`, `figma-use`, `figma-use-figjam`, `figma-use-motion`, `figma-use-slides` |
| `plugins/google-drive` | `google-docs`, `google-drive`, `google-drive-comments`, `google-sheets`, `google-slides` |
| `plugins/pages` | `maintain-space`, `manage-schedules`, `organize-space`, `write-page` |
| `plugins/pdf` | `pdf` |
| `plugins/plugin-creator` | `create-plugin`, `prepare-plugin-submission`, `update-plugin` |
| `plugins/plugin-management` | `plugin-management` |
| `plugins/presentations` | `Presentations` |
| `plugins/sites` | `sites`, `sites-remix` |
| `plugins/spreadsheets` | `Spreadsheets`, `excel-live-control` |
| `plugins/template-creator` | `template-creator` |
| `plugins/visualize` | `visualize` |
| `plugins/work-pets` | `create-pet`, `pets`, `update-pet` |
| `system` | `review-agent` |

As referências incluem componentes com redistribuição restrita e outros sem licença
aberta confirmada. `documents` possui restrição expressa de redistribuição na licença
original; não é disponibilizada como MIT. Consulte [atribuições](THIRD_PARTY_NOTICES.md)
e o [manifesto](manifest.json) para origem e classificação de cada entrada.

## Atualização e remoção

Para atualizar o **Engineering OS**, obtenha a versão nova e revise o plano antes de aplicar:

```sh
git pull --ff-only
python3 -B frameworks/engineering-os/scripts/eos.py update --dry-run
python3 -B frameworks/engineering-os/scripts/eos.py update
python3 -B frameworks/engineering-os/scripts/eos.py doctor
```

Use o pacote fonte atualizado. Alterações locais em arquivos gerenciados bloqueiam a
atualização para preservar adaptações; mudanças de versão maior exigem revisão adicional.
Skills copiadas manualmente precisam de comparação e atualização separadas.

Para remover o Engineering OS, execute pelo clone fonte, que permanece disponível:

```sh
python3 -B frameworks/engineering-os/scripts/eos.py uninstall --dry-run
python3 -B frameworks/engineering-os/scripts/eos.py uninstall
```

A remoção atua apenas nos arquivos gerenciados intactos e no bloco exato de instrução.
Preserva arquivos alheios, skills emprestadas, relatórios e backups. Consulte o
[guia completo](frameworks/engineering-os/docs/installation.md) antes de recuperar uma
instalação interrompida ou resolver conflitos.

## Estrutura e documentação

```text
frameworks/engineering-os/  Framework completo: runtime, 13 skills, 9 workflows e testes
skills/local/              Skills abertas locais e de terceiros
skills/system/             Skills abertas de sistema incluídas no snapshot
CATALOG.md                 Inventário das 79 entradas
manifest.json              Origens, distribuição, licenças e hashes do snapshot
THIRD_PARTY_NOTICES.md      Atribuições e escopo de licenciamento
```

- [Instalação e preservação](frameworks/engineering-os/docs/installation.md)
- [Uso do CLI e contrato de evidências](frameworks/engineering-os/docs/usage.md)
- [Arquitetura](frameworks/engineering-os/docs/architecture.md)
- [Capacidades e limites no Codex](frameworks/engineering-os/docs/codex-capabilities.md)
- [Validação do framework](frameworks/engineering-os/docs/validation.md)
- [Validação da distribuição open source](VALIDATION.md)

## Licenças

[MIT](LICENSE) para Engineering OS e contribuições originais identificadas no manifesto.
As skills de [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) mantêm sua
licença MIT e atribuição. Skills Apache-2.0 mantêm os arquivos de licença originais;
a licença da raiz não as relicencia. Veja [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

Não inclui credenciais, configurações pessoais, caches ou logs brutos de sessão.
A disponibilidade local de um componente não concede direitos adicionais de redistribuição.
