# Requisitos — responsável: requisitos

Extrair problema, objetivo, atores/perfis/organizações, regras, requisitos funcionais
e não funcionais, dependências, restrições e erros. Distinguir fonte observada,
hipótese e decisão pendente. Não definir formatos, limites ou SLAs por preferência.

Transformar cada requisito em aceite verificável: precondição/entrada/ação →
resultado e efeitos persistidos ou proibidos. Vincular requisito → critério de
qualidade → teste/asserção → evidência. Considerar vazio, limite, duplicado,
concorrência, falha externa e acesso direto à API conforme impacto.

Para formulário, verificar regra no servidor e no cliente quando ambos existem;
feedback compreensível, acessibilidade, persistência/edição e dados inválidos.
Para API, definir identidade, autorização por recurso/tenant, contrato e erro.

Ambiguidade que muda comportamento impede implementação dependente até esclarecimento;
continuar descoberta e trabalho independente. Gate 1 exige aceite suficiente e
ausência de decisão crítica em aberto. Usar template de requisitos somente para
complexidade que o justifique; mudança simples pode ter aceite no próprio relatório.
