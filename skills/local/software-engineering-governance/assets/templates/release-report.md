# Revisão de release

Registrar demanda, revisão final/artefato, ambiente alvo, risco e escopo da avaliação.

## Gates e evidências
Consolidar sete gates e runner real; listar comandos, casos, falhas/skips, revisão,
logs/JUnit e hashes. Separar verificações locais das externas não realizadas.

## Riscos e recuperação
Registrar achados abertos/decisões P2, rollback, backup/restauração pertinentes,
monitoramento e limitações. P0/P1 aberto bloqueia release.

## Configuração externa e autorização
Conferir checks obrigatórios, proteção de branch e mesmo SHA no deploy quando houver
acesso autorizado. Ausência de evidência mantém pendência. Aprovação técnica não
autoriza publicação; referenciar autorização humana específica antes da operação.

## Resultado
Declarar APROVADA/REPROVADA/INCOMPLETA para o escopo realmente comprovado.
