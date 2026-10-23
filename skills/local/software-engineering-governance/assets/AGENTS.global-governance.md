<!-- software-engineering-governance:global:start -->
## Governança automática de engenharia nos projetos

- Use automaticamente `software-engineering-governance` em tarefas de desenvolvimento,
  bugs, refatorações, requisitos, arquitetura, segurança e preparação de releases em
  projetos de software, sem exigir chamada explícita ou aprovação para selecionar a skill.
- Leia o `SKILL.md` da skill antes de aplicar seu workflow. Use a versão indicada pelas
  instruções específicas do projeto; na ausência dessa indicação, use a instalação global
  em `~/.agents/skills/software-engineering-governance/SKILL.md`. Resolva scripts e
  referências a partir da pasta da skill selecionada, nunca do diretório do projeto.
- Preserve instruções existentes, stack, arquitetura e regras de negócio. Descubra o
  contexto afetado, classifique o risco, defina aceite e valide com evidências reais,
  dimensionando o processo à mudança. Não aplique a conversas ou artefatos sem desenvolvimento.
- Reutilize a validação de `production-readiness-auditor` e `ui-ux-visual-auditor` quando
  aplicável, compartilhando testes e achados sem duplicação. Não declare sucesso sem
  execução; registre pendências e conclua APROVADA/REPROVADA/INCOMPLETA no escopo verificado.
- Respeite autorizações específicas já concedidas. O uso automático não autoriza publicação,
  produção, dados reais, operações destrutivas, mudanças sensíveis ou configuração global
  adicional. AGENTS.md orienta o agente; bloqueios técnicos de deploy dependem da infraestrutura.
<!-- software-engineering-governance:global:end -->
