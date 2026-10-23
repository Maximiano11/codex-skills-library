# Governance Core

O núcleo não depende do Codex. Adaptadores traduzem descoberta e instalação.
Intenção e autorização são preservadas: analisar, explicar, planejar ou auditar não
significa corrigir, publicar ou migrar. Um flag JSON não prova autorização humana.
Instruções da plataforma prevalecem; instruções específicas do projeto orientam a
implementação. Resolver conflitos com evidência, sem ignorar o pedido silenciosamente.

Risco baixo exige correção local reversível conhecida; desconhecido permanece médio.
Autenticação/autorização, dinheiro, dados sensíveis, migração, arquitetura relevante,
produção e incidentes elevam o rigor. A classificação determinística é triagem,
confirmada por inspeção técnica. Não executar todas as skills. Cada workflow permite
especialidades adicionais apenas por impacto demonstrado.

Reutilizar aceite, plano, evidências e verificações de governança/QA já disponíveis.
Documentação proporcional, sem ADR para toda edição. Código e documentação divergentes
são evidência de inconsistência; código observado não redefine sozinho a regra desejada.
Não ler .env/credenciais nem publicar conteúdo de logs brutos. Não alterar produção,
contratos públicos ou dados reais sem autorização aplicável. Sem deploy automático.

VALIDATED exige todos os critérios obrigatórios aplicáveis comprovados; pendência,
ambiente ausente, zero testes ou skip mantém PARTIALLY_VALIDATED; falha obrigatória ou
P0/P1 aberto leva a BLOCKED. Isso qualifica apenas o escopo configurado, não garante
segurança absoluta e não concede autorização operacional. Não repetir refinamentos
sem informação nova; após duas tentativas sem progresso, reavaliar e informar bloqueio.
