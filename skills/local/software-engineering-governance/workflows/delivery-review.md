# Entrega — responsáveis: documentação e release

Confrontar implementação com aceite, diff e documentação existente: README, ADRs,
API, modelo, regras, testes, operação, deploy/rollback e histórico conforme impacto.
Atualizar só o que mudou e está implementado; evitar versões paralelas.

| Gate | Condição |
| --- | --- |
| 1 Requisitos | Aceite suficiente e decisões críticas resolvidas. |
| 2 Arquitetura | Compatibilidade, riscos e aprovações estruturais tratados. |
| 3 Implementação | Aceite e contratos respeitados; diff revisado. |
| 4 Testes | Verificações obrigatórias executadas com resultados atuais. |
| 5 Segurança | Controles afetados avaliados; sem P0/P1 aberto. |
| 6 Documentação | Documentos afetados sincronizados, ou inaplicabilidade justificada. |
| 7 Entrega | Gates anteriores satisfeitos, riscos residuais e recuperação registrados. |

Todos os gates precisam de evidência ou justificativa revisada de inaplicabilidade;
os controles essenciais de requisitos/implementação/testes/revisão não podem ser
dispensados no helper. Um registro de revisão manual é evidência de avaliação,
nunca prova de teste executado. Pontuação qualitativa não modifica gates.

Precedência: falha bloqueante → REPROVADA; evidência obrigatória ausente → INCOMPLETA;
todos os obrigatórios comprovados → APROVADA **no escopo avaliado**. Registrar P2
aberto com decisão, responsável e motivo; P0/P1 aberto sempre bloqueia.

Para release Git usar o runner estrito incluído, ferramentas já disponíveis e
política revisada da revisão final limpa. Sem Git, aprovação incremental é possível
com hashes dos arquivos de escopo; release automatizado estrito permanece incompleto.
CI deve consumir exit code e publicar o mesmo SHA/artefato. Preparar proposta fora
do pipeline ativo; não ativar deploy/proteções sem autorização.

Entregar relatório objetivo com risco, arquivos/comportamentos, decisões, comandos,
resultados, skips/não executados, achados, evidências, documentos e riscos residuais.
Usar templates quando úteis. Aprovação de QA não autoriza publicação.
