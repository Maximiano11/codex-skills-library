# Arquitetura — responsável: arquitetura

Mapear componentes, responsabilidades, dependências, contratos e fluxos de dados
atingidos. Avaliar coesão/acoplamento, consistência/transações, concorrência,
segurança, observabilidade, escalabilidade necessária e custo operacional.
Preservar decisões válidas. Usar SOLID/DRY/KISS/YAGNI como heurísticas; não impor
abstrações, microserviços, filas ou dependências sem necessidade demonstrada.

Para decisão relevante, procurar ADR existente. Registrar contexto, problema,
alternativas, decisão proposta, justificativa, consequências, riscos e reversão.
Descrever stakeholders e preocupações relevantes, sem alegar conformidade 42010.

Mudança significativa: preparar design/diff revisável e testes seguros; obter
autorização específica antes de executar a transformação. Não confundir corrigir
um bug autorizado com licença para reestruturar o sistema. Gate 2: solução
compatível e riscos/contratos tratados; aprovação pendente mantém o gate incompleto.
