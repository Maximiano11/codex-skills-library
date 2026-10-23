# Acessibilidade: verificar, medir e delimitar

Use a meta definida no projeto. Se ausente, proponha WCAG 2.2 AA como referência
técnica para web e declare o alcance exploratório; não atribua obrigação legal ou
certificação. Este checklist é parcial. Para conformance completa, é necessário
avaliar todos os critérios aplicáveis, páginas e processos do escopo.

## Evidência prática

Complete tarefas com teclado: ordem de foco, acionamento, saída de componentes,
abertura/fechamento de diálogos e retorno ao contexto. Inspecione nomes, papéis,
estados, rótulos e estrutura na árvore de acessibilidade.

Use leitor de tela se disponível e necessário ao escopo. Sem ele, marque essa
verificação como não executada; DOM acessível sozinho não prova a experiência
assistiva. Scanner automatizado existente, como axe, complementa os testes manuais;
zero alertas não significa ausência de barreiras.

Confira zoom, reflow, uso sem distinguir cores, movimento reduzido e alternativas
de entrada. Preserve semântica nativa quando adequada; não adicione ARIA redundante
nem substitua um controle funcional por um elemento genérico só para obter estilo.

## Critérios mensuráveis e fontes

- **Contraste textual, 1.4.3:** em AA, em geral 4,5:1; texto grande admite 3:1.
  A definição de grande é 18 pt, ou 14 pt em negrito. Considere exceções do critério,
  como logotipos, decoração e componentes inativos. Meça cores efetivas e fundo;
  não deduza razão exata olhando um screenshot.
  [W3C — Contrast Minimum](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html).
- **Contraste não textual, 1.4.11:** informações visuais necessárias para identificar
  controles/estados e partes relevantes de gráficos geralmente exigem 3:1 em
  relação às cores adjacentes. Verifique aplicabilidade e exceções; não exija a
  mesma razão para toda borda meramente decorativa.
  [W3C — Non-text Contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html).
- **Reflow, 1.4.10:** para conteúdo com leitura vertical, verifique apresentação
  equivalente a 320 CSS px de largura sem perder informação/funcionalidade nem
  exigir rolagem em duas dimensões, salvo partes cuja disposição bidimensional
  seja necessária. Uma tabela pode precisar de rolagem horizontal; isso não
  justifica overflow de toda a página.
  [W3C — Reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html).
- **Alvos, 2.5.8:** a referência AA é 24 × 24 CSS px, com exceções, incluindo
  espaçamento suficiente, alternativa equivalente, links inline, controles do
  navegador e apresentação essencial. Examine a geometria antes de acusar falha.
  Não apresente 44 × 44 como obrigação universal AA.
  [W3C — Target Size Minimum](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html).
- **Foco não encoberto, 2.4.11:** ao receber foco por teclado, o componente não deve
  ficar totalmente escondido por conteúdo criado pelo autor. Verifique overlays
  e barras fixas; visibilidade completa é uma meta mais forte que este mínimo.
  [W3C — Focus Not Obscured](https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html).

Identifique a condição avaliada, valor medido, método e referência em cada achado.
Se a ferramenta não permite medir com confiança, registre suspeita e a verificação
pendente. Para aplicativos nativos, consulte requisitos e ferramentas da plataforma;
não aplique unidades CSS diretamente a pontos ou unidades nativas.
