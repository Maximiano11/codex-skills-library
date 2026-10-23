# Arquitetura e evolução

Engineering OS separa decisão assistida por agente de mecanismos determinísticos.
Não usa uma biblioteca de orquestração externa ou um serviço central. O núcleo Python
3.10+ depende apenas da biblioteca padrão e funciona sem Git, SDK, credencial ou rede.

| Camada | Implementação | Responsabilidade |
| --- | --- | --- |
| Governance Core | policies/governance.md, contratos de core/ | Intenção, escopo, risco, autorização, evidência e conflitos |
| Prompt Engine | skills/prompt-engineer/ | Interpretação semântica e especificação proporcional pelo agente |
| Orchestrator | core/engineering_os/orchestrator.py, skill engineering-os | Triagem explicável e seleção; confirmação técnica pelo agente |
| Especialidades | skills/ | Onze competências delimitadas, com exemplos e casos de avaliação |
| QA Engine | core/engineering_os/gates.py | Execução explícita, parsing de testes e estados de validação |
| Knowledge | templates/, docs/, technical-documentation | Decisões e contratos nas fontes existentes do projeto |
| Adaptador Codex | adapters/codex/ | Propriedade de arquivos, instalação e instruções persistentes |

O agente faz interpretação que regras locais não garantem. `plan` conserva o pedido,
produz modo, risco, razões, superfícies, workflow, skills, aceite fornecido e etapas.
Não inventa uma especificação de negócio a partir de palavras-chave. Sem aceite ou
com ambiguidade crítica declarada, `implementation_ready` permanece falso. Seu valor
é triagem, nunca autorização humana nem prova de ausência de ambiguidades.

Os workflows JSON são grafos acíclicos em ordem de execução, com ativação, skills,
dependências, aprovação, interrupção e saídas. O modo de análise substitui etapas de
modificação por inspeção e entrega. A classificação conservadora é revisável por
contexto técnico; pode haver falso positivo ou perda de significado em linguagem
arbitrária, negação ou pedidos compostos. O operador deve confirmar o plano.

Novas especialidades são pastas Agent Skills. Novos workflows são JSON com o mesmo
contrato; `workflow` no objeto JSON de mudança seleciona seu id sem alterar o núcleo.
O núcleo não importa o adaptador Codex; o CLI seleciona esse adaptador explicitamente.
Adaptadores futuros podem traduzir instalação e instruções para outra plataforma.

## Decisões e riscos

- Sem dependência de SDK: a entrega não precisa iniciar turnos de modelo. SDK ou hooks
  podem ser adicionados a um adaptador separado quando houver necessidade comprovada.
- Propriedade por arquivo e backups privados: evita apagar diretórios com notas locais.
  Atualização recusa drift, downgrade e versão maior sem opção explícita.
- `prompt-engineer` preexistente é emprestada sem substituição. Sua versão pode diferir
  do pacote e precisa ser revisada pelo operador; o instalador não declara equivalência
  semântica. Diagnóstico identifica empréstimo e mudança de bytes conhecida.
- Rollback transacional cobre exceções no processo. Não há garantia ACID contra falta
  de energia, processo morto durante escrita, filesystem hostil ou escritor concorrente
  malicioso. Journal/backup permite recuperação manual; não há recuperação automática
  de transação interrompida. O lock evita dois instaladores cooperativos concorrentes.
- Hashes detectam drift acidental; quem escreve estado/evidência pode forjá-los. Não há
  assinatura, certificação de revisão humana ou sandbox no framework.
- O produto não altera pipelines, branch protection ou deploy. Um gate local só bloqueia
  um pipeline se ele for explicitamente integrado e sua política for configurada.

## Fases entregáveis

1. Fundação: núcleo, CLI, adaptador, prompt-engineer, orquestrador e instalador; primeiro
   ciclo passou em 24 testes antes das especialidades.
2. Engenharia: arquitetura, implementação, UX, dados e workflows de desenvolvimento.
3. Qualidade: QA, segurança, revisão, gates e avaliações determinísticas/modelo separadas.
4. Operação: release, confiabilidade, desempenho, documentação e workflows operacionais.
5. Consolidação: testes integrados, revisão independente, correções e documentação.

O histórico de execução e limitações efetivas está em validation.md. A existência desta
lista não substitui os testes. O número VERSION identifica o pacote local; nenhum
release foi publicado. Esta distribuição do Engineering OS está licenciada sob MIT; consulte LICENSE.
