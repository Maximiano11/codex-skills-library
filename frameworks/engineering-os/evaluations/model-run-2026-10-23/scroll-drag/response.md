# Resposta
Corrigido o início indevido de drag pela área de texto. Apenas o handle aceita início do ponteiro primário; o texto mantém touch-action:auto e não recebe preventDefault. Mantidos captura de ponteiro e handlers de teclado; adicionada limpeza em pointercancel/lostpointercapture e liberação ao terminar.

Modo: implementação de correção. Risco médio: interação entre eventos de ponteiro, scroll e acessibilidade por teclado, sem dados ou serviço externo. Workflow: bug-investigation.
Skills selecionadas: Engineering OS e prompt-engineer (instruções em engineering-os/skills/); implementation-standards, quality-engineer e code-reviewer. Instruções locais AGENTS.md lidas. Stack preservada, dados sintéticos, sem pacotes instalados, produção ou publicação. Especialidades reutilizadas sem auditar superfícies não afetadas. product-ux para investigar gesto, handle, área rolável, captura e teclado.

## Aceite ligado ao pedido e contexto
- “texto deve permitir scroll normal no toque/roda”: impedir drag iniciado pelo texto, manter gesto nativo sem preventDefault global e verificar scroll da lista. Roda verificada; toque permanece pendente.
- “arrastar começa somente pelo handle”: mesmo arrasto pela região de texto deve manter ordem, pelo handle deve reordenar.
- “drag deve continuar funcionando”: handle continua capturando ponteiro e alterando posição ao soltar.
- “preserve reordenação por teclado”: ArrowDown/ArrowUp movem o item e mantêm foco em seu botão.
- Contexto de pointer capture: limpar estado em finalização/cancelamento para não deixar drag preso.

## Evidências e comandos reais
Servidor:
    python3 -B -m http.server 8876 --bind 127.0.0.1
CUA no navegador real, URL http://127.0.0.1:8876/scroll-drag/:
1. Antes da correção, drag([190,63],[190,190]) sobre o texto alterou ordem [1,2,3,...] para [2,1,3,...]. Causa observada no handler pointerdown delegado: preventDefault e captura eram aplicados a qualquer row.
2. Depois, o mesmo drag sobre texto manteve [1,2,3,4,5,6,7,8] e scrollTop=0. CSS computado: texto touch-action='auto', handle='none'.
3. scroll([200,130],'down',1) mudou scrollTop de 0 para 368; ordem permaneceu [1,2,3,4,5,6,7,8]. Screenshot scroll.png inspecionada.
4. Após rolar ao topo, drag([62,63],[190,190]) pelo handle moveu item 1, com ordem [2,1,3,4,5,6,7,8]. Screenshot handle.png inspecionada.
5. Press ArrowDown no botão Mover item 1: ordem [2,3,1,4,5,6,7,8], foco Mover item 1.
6. Press ArrowUp no mesmo botão: ordem [2,1,3,4,5,6,7,8], foco Mover item 1. Screenshot keyboard.png inspecionada.
Screenshots exibem seleção de texto remanescente do teste de arrasto de texto; isso é comportamento nativo de seleção, não indicação de reordenação indevida.

## Revisão e limites
Diff revisado: CSS, conteúdo e handler keydown originais preservados; preventDefault restrito ao handle; alvo de drop confinado à lista; liberação e limpeza revisadas no código.
Sem achados funcionais obrigatórios nos cenários executados. Após reinserção por ponteiro, o foco observado foi o documento; a navegação/reordenação de teclado solicitada foi exercitada separadamente e manteve foco no item.
Toque real ou emulado não foi executado: a API CUA documentada utilizada expõe drag/scroll/teclado, sem gesto de touchscreen. Não se equipara leitura de touch-action ou eventos de mouse a comprovação do scroll no toque.
pointercancel, perda de captura e múltiplos ponteiros foram revisados, mas não disparados no navegador. Não há runner de testes de UI no fixture; não foram instalados pacotes.
Perguntas pendentes ao ambiente de avaliação: disponibilizar gesto de toque ou aparelho para executar pan pelo texto e drag pelo handle. Nenhuma pergunta foi enviada ao usuário real.

Estado: PARTIALLY_VALIDATED, porque toque é critério explícito não exercitado. Implementação realizada e comportamento de roda/mouse/teclado validado; não constitui aprovação de release.
Arquivos alterados no fixture: index.html.

