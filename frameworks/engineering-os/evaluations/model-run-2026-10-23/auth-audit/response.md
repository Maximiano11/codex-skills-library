# Auditoria
Modo: auditoria somente leitura. Risco: alto por autenticação/autorização e isolamento entre organizações. Workflow: security-review. Skills selecionadas: prompt-engineer, engineering-os, security-auditor e quality-engineer. Nenhum arquivo alterado no fixture.

## Achados com evidência
1. **P1 — leitura entre organizações (`auth.py:2`).** A função considera role e owner_id, mas nunca compara organização. Admin de org-a acessa registro de org-b; membro de org-a com id igual ao owner_id de org-b também acessa. CONTRATO exige negar ambos. Impacto demonstrado: can_read concede autorização indevida entre organizações. Vazamento por API real não foi avaliado, pois não há rota no fixture. Mitigação proposta: negar organização diferente antes da regra de admin/proprietário; não aplicada.
2. **P2 — sessão ausente lança exceção (`auth.py:2`).** user=None resulta em TypeError ao ler user["role"], em vez de negar como pede CONTRACT.md. Impacto demonstrado: função falha; eventual HTTP 500 depende de tratamento externo não presente. Mitigação proposta: negar usuário ausente antes de ler campos; não aplicada.

## Aceite e execução
Fonte: pedido e CONTRACT.md. Verificações: sessão ausente nega; organizações diferentes negam inclusive admin/owner coincidente; mesma organização permite admin e membro proprietário e nega membro não proprietário. Somente dados sintéticos, sem correção.

Comando real: `python3 -B - <<'PY'`, no fixture/auth-audit, importando can_read e executando seis dicionários sintéticos. Registro: `{'org_id':'org-b','owner_id':22}`. Usuários: None; admin id=1/org-a; membro id=22/org-a; admin id=1/org-b; membro id=22/org-b; membro id=33/org-b. O script capturou exceções e comparou observado com booleano esperado.
```
unauthenticated: expected=False; observed="TypeError: 'NoneType' object is not subscriptable"; contract=VIOLATED
admin_cross_org: expected=False; observed=True; contract=VIOLATED
member_cross_org_matching_owner: expected=False; observed=True; contract=VIOLATED
admin_same_org: expected=True; observed=True; contract=satisfied
member_same_org_own: expected=True; observed=True; contract=satisfied
member_same_org_other: expected=False; observed=False; contract=satisfied
Cases executed: 6; contract violations: 3
```
Exit 0 do coletor significa término da coleta; não significa conformidade. Hashes iniciais/finais iguais em baseline-agent.json/verified-files-agent.json.

Estado: auditoria concluída com evidência local; comportamento auditado BLOCKED/REPROVADO por P1 aberto e três violações. Sessão/token em HTTP, dependências e sistemas externos não foram verificados, ausentes do contexto. Sem correção aplicada nem pergunta essencial pendente à auditoria.
