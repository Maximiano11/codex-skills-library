# Software Engineering Governance 1.0.0

Skill local para orientar requisitos, arquitetura, implementação, QA, documentação
e revisão de entrega com controles proporcionais ao risco. Entrypoint: [SKILL.md](SKILL.md).

## Estado desta entrega

**Integração local CONCLUÍDA e validada** no runtime do desktop 0.163.0-alpha.11:
descoberta habilitada, invocação explícita e ativação automática por AGENTS.md em
novas sessões. As sessões leram a skill, executaram testes e reprovaram o fixture
defeituoso. [Relatório de integração](validation/codex-integration-2026-10-22/report.md).

O bloqueio anterior vinha da chamada à CLI 0.133.0 do PATH. O launcher incluído
seleciona o runtime do aplicativo, mantendo o mesmo modelo configurado e sem alterar
configurações globais. Os 65 testes do pacote atual passaram; o validador de formato
também passou. AGENTS.md é orientação persistente, sem garantia universal de adesão
em qualquer pedido e sem impor proteção técnica de deploy.

Piloto Atria **concluído na demanda real ATR-GATE-01**, após autorização específica:
parser local corrigido, 33 testes aprovados e 13 critérios dos sete gates comprovados.
Foi registrada comparação da mesma regressão antes/depois, sem alegar redução causal
de retrabalho. [Relatório do piloto concluído](validation/atria-parser-pilot/report.md).
A etapa inicial de auditoria e seus 18 testes estão preservados como histórico.
No piloto, nenhuma configuração global, pipeline, dado de cliente, deploy ou
funcionalidade da aplicação foi alterado; a mudança foi restrita à infraestrutura local de QA.

## Usar

No Codex deste projeto: `$software-engineering-governance` seguido da demanda.
O AGENTS.md local também orienta o uso para desenvolvimento. Para execução pela CLI,
usar o runtime correto, especialmente se o PATH contiver uma instalação antiga:

```sh
python3 scripts/codex_runtime.py --print-runtime
python3 scripts/codex_runtime.py -- exec --ephemeral --skip-git-repo-check --sandbox read-only -C /projeto '$software-engineering-governance Analise esta demanda'
```

Executar a partir desta pasta da skill. Permissões read-only são adequadas para
auditoria; testes que criam fixtures precisam de temporários graváveis autorizados.
Detalhes e modo automático em [integração Codex](references/codex-integration.md).

Outros projetos: copiar a pasta inteira para `.agents/skills/` e acrescentar
[assets/AGENTS.governance.md](assets/AGENTS.governance.md) às instruções existentes.
Instalação, atualização, desinstalação e caminhos suportados estão em
[references/codex-integration.md](references/codex-integration.md). Para uso global,
copiar esta pasta para `~/.agents/skills/software-engineering-governance` e integrar
[assets/AGENTS.global-governance.md](assets/AGENTS.global-governance.md) ao AGENTS
global existente, mediante autorização específica. Preservar instruções dos projetos.

## Conteúdo

```text
software-engineering-governance/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── agents/openai.yaml
├── references/
│   ├── risk-and-permissions.md
│   ├── quality-model.md
│   ├── standards.md
│   ├── automation.md
│   └── codex-integration.md
├── workflows/
│   ├── project-discovery.md
│   ├── requirements-analysis.md
│   ├── architecture-review.md
│   ├── implementation.md
│   ├── quality-assurance.md
│   ├── regression-validation.md
│   └── delivery-review.md
├── checklists/
│   ├── article-120.json
│   └── engineering.json
├── assets/
│   ├── AGENTS.governance.md
│   └── templates/
│       ├── requirements.md
│       ├── technical-design.md
│       ├── adr.md
│       ├── test-plan.md
│       ├── quality-report.md
│       ├── incident-report.md
│       └── release-report.md
├── scripts/
│   ├── governance.py
│   ├── codex_runtime.py
│   ├── release_gate.py
│   └── test_release_gate.py
├── tests/
│   ├── test_governance.py
│   ├── test_codex_runtime.py
│   └── fixtures/scenarios.json
└── validation/  especificação, relatórios e evidências executadas
```

Os dois catálogos usam JSON para leitura determinística com biblioteca padrão, em
vez de 11 YAMLs duplicados. Sete workflows implementam seis papéis lógicos, sem
dependência de multiagentes. Referências são carregadas por necessidade.

O catálogo do artigo contém 120 paráfrases com página/figura/número original. Métodos,
severidades, mapeamentos e regras de gate são adaptações explícitas desta skill.
O artigo é teórico e não demonstra redução empírica de retrabalho; não alegamos
conformidade/certificação ISO ou ausência absoluta de defeitos.

## Automação e testes

Python 3.10+, biblioteca padrão; Git para o runner estrito de release. Não há
dependências de aplicação a instalar para usar o núcleo. Ler o contrato antes de
executar comandos de projeto ou políticas de release:
[references/automation.md](references/automation.md).

```sh
python3 -m unittest discover -s tests -v
python3 scripts/test_release_gate.py
python3 scripts/governance.py --help
```

Executar a partir desta pasta. Governança gera plano e avaliação inicialmente
incompleta fora do projeto auditado; só runner real comprova execução de testes.
Hashes fornecem rastreabilidade local, não assinatura/autenticação de revisor.

Evidências e limites: [validation/report.md](validation/report.md).
