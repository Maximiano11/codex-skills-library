# Capacidades e limitações Codex — pesquisa de 23/10/2026

Fontes oficiais consultadas antes da implementação. A tentativa de consumir os URLs
Markdown pela ferramenta web falhou por content-type; as páginas HTML foram abertas.

| Mecanismo | Capacidade confirmada | Uso neste produto |
| --- | --- | --- |
| AGENTS.md | Instrução global em CODEX_HOME e camadas locais; override tem precedência | Bloco preservando conteúdo existente; orientação por instruções |
| Agent Skills | SKILL.md com name/description, descoberta e invocação explícita/implícita | 13 skills e metadados; escolha contextual pelo agente |
| Configuração | Configuração por perfil e projeto, controles próprios da plataforma | Respeitada; config.toml não é alterado |
| Execução | CLI/app-server e ferramentas sob permissões do runtime | Probe de descoberta, sem iniciar turno de modelo |
| Subagentes | Delegação especializada, herança das permissões do pai | Opcional e condicionado à autorização; avaliações independentes nesta entrega |
| Hooks | Eventos de lifecycle e hooks de comando/MCP, com confiança aplicável | Não instalados; desenvolvimento/configuração futura se necessário |
| SDKs | Bibliotecas oficiais e app-server para integração programática | Não necessários ao núcleo; não adicionados como dependência |

As [instruções AGENTS](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
são carregadas em hierarquia; não substituem instruções superiores. Um override
global não vazio prevalece sobre AGENTS.md. Instruções específicas do projeto
podem refinar as globais. A leitura tem limite de contexto configurável.

[Skills](https://learn.chatgpt.com/docs/build-skills) usam descoberta progressiva e
seleção por contexto. A documentação atual apresenta .agents/skills no escopo pessoal;
o adaptador conserva o diretório skills no perfil CODEX_HOME deste ambiente, cuja
descoberta deve ser confirmada com probe. Não se instala cópia duplicada nos dois.

[Subagentes](https://learn.chatgpt.com/docs/agent-configuration/subagents) herdam
permissões e não ganham sandbox independente por uma instrução textual. Os papéis das
skills funcionam sem delegação; não dependem de chamadas imaginárias de agentes.

[Hooks](https://learn.chatgpt.com/docs/hooks) incluem UserPromptSubmit e eventos de
ferramentas/sessão. A documentação confirma mecanismos para contexto e bloqueio nos
eventos suportados, sujeitos à configuração, confiança e runtime. Não significa que
um pacote de skills intercepta toda mensagem em qualquer cliente. Este produto não
instala hook, listener ou middleware; ativação automática permanece orientada por
instrução/seleção. Garantia técnica mais forte exigiria implementar e testar um adapter
de lifecycle e seus limites no cliente alvo, com configuração autorizada.

[Codex SDK](https://learn.chatgpt.com/docs/codex-sdk) confirma bibliotecas TypeScript e
Python e o app-server para clientes próprios. Integrá-los exigiria dependências e
gestão de sessões/credenciais que não são necessárias para este framework local.

No ambiente observado, codex do PATH é 0.133.0; CODEX_CLI_PATH aponta para o runtime
do aplicativo, 0.163.0-alpha.11.1. São versões de executáveis CLI, não uma versão
independente da interface desktop. Preferir runtime explícito ou ambiental quando
testando a integração do desktop; não substituir modelo/configuração para contornar
incompatibilidade do executável errado. `scripts/probe_codex.py` permite confirmar
versão, flags relevantes e skills/list em cada executável sem turno de modelo.

O núcleo, ownership, runner e gates são capacidades desenvolvidas aqui. Não são APIs
nativas do Codex nem proteção remota de deploy. A confirmação de descoberta e os limites
dos testes reais ficam em validation.md e nos registros externos de instalação.
