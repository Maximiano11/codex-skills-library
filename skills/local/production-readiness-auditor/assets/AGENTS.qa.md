<!-- production-readiness-auditor:start -->
## Qualidade e validação de software

- Use `production-readiness-auditor` para novas funcionalidades, formulários/APIs,
  mudanças de regras, bugs, refatorações com risco e auditorias de pré-produção.
- Descubra stack, contratos, scripts, testes e CI/CD antes de adicionar ferramentas.
  Preserve convenções e reutilize a infraestrutura existente.
- Toda funcionalidade nova requer validação proporcional ao risco. Toda correção de
  bug deve incluir regressão automatizada quando viável; documente a inviabilidade.
- Execute os testes afetados em mudanças relevantes. Mudanças críticas exigem
  revisão ampliada. Use validação incremental e suíte abrangente antes do release.
- Não declare testes aprovados sem executá-los. Identifique testes não executados,
  skips, falhas, limitações e evidências. Não oculte falhas para obter testes verdes.
- Corrija falhas sob seu controle e dentro do escopo autorizado antes de concluir.
  Não altere regras de negócio ambíguas nem invente limites sem confirmação.
- Use dados isolados e descartáveis. Não altere dados de clientes, publique,
  contrate serviços nem faça testes destrutivos contra produção.
- P0/P1 abertos bloqueiam release. P2 segue avaliação documentada da política.
  Testes obrigatórios pendentes impedem status APROVADO.
- Antes de alterar pipelines de produção, apresente mudanças concretas e obtenha
  aprovação. Um gate local não substitui proteção de branch e dependências do deploy.
- Entregue relatório com escopo, arquivos/fluxos, testes e resultados, severidades,
  correções, evidências, não executados, riscos e APROVADO/REPROVADO/NÃO VERIFICADO.
<!-- production-readiness-auditor:end -->
