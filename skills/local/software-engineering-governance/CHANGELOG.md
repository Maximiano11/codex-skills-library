# Histórico

## 1.0.0 — 22/10/2026

- Bloco AGENTS global portátil e instruções de instalação pessoal, preservação e
  precedência para uso automático entre projetos, autorizado após o piloto local.
- Skill modular com sete workflows e políticas de risco/autorização.
- 120 critérios parafraseados do PDF e 16 controles complementares com origem explícita.
- Descoberta, risco, plano e assessment em Python padrão; templates e AGENTS de projeto.
- Runner de release reutilizado da production-readiness-auditor com suíte incluída.
- Forward-testing encontrou e motivou correção de duas aprovações indevidas:
  observação substituindo teste em release e erro JUnit fora de testcase ignorado.
- Assessment de release passa a exigir relatório estrito da mesma revisão, logs e JUnit.
- Descoberta e execução nativas explícita/automática comprovadas no runtime desktop
  0.163.0-alpha.11. Causa do bloqueio anterior reproduzida na CLI 0.133.0 do PATH;
  novo launcher seleciona o runtime correto sem trocar modelo ou configurações globais.
- Sete testes do resolver e verificações nativas com defeito conhecido; 65 testes
  automatizados do pacote aprovados. Tentativas anteriores preservadas como histórico.
- Piloto Atria iniciado em leitura e concluído na demanda real autorizada ATR-GATE-01:
  parser adaptado preservando Node flat, 33 testes e 13 critérios aprovados; comparação
  controlada de regressão antes/depois, sem publicar ou alterar pipeline.
