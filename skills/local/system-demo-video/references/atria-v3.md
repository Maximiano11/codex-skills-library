# Referência aprovada: Atria v3

Aprovada pelo usuário em 20/10/2026 após duas versões rejeitadas. Referência de linguagem: vídeo EmpresarizaHUB em https://www.empresarizahub.com.br/assista. Não reutilizar imagens, áudio ou identidade da referência externa.

## Como consultar

Se disponíveis, abra o filme e quadros do Atria para avaliar composição e movimento:

- Filme original local: `/Users/jeversonsolomon/Documents/Github/GPJ/output/atria-showcase-60s/atria-showcase-60s-v3.mp4`.
- Storyboard visual local: `/Users/jeversonsolomon/Documents/Github/GPJ/output/atria-showcase-60s/storyboard-visual-v3.jpg`.
- Player público de referência: https://atriatasks.vercel.app/#apresentacao.
- Implementação opcional: `/Users/jeversonsolomon/Documents/Github/GPJ/output/atria-showcase-60s/src/v3/motion.tsx` e `scripts/render-v3.mjs`.

A skill continua utilizável sem esses caminhos. Caso não estejam disponíveis, siga as características documentadas abaixo e peça acesso à referência somente se a comparação exata for necessária. Não afirme ter assistido ao filme sem fazê-lo.

## O que fez diferença

A versão v1 parecia uma montagem de prints estáticos sobrepostos; v2 usava uma demonstração de navegação gravada. Ambas foram rejeitadas. A versão v3 foi aprovada por transformar a UI em material de motion design: componentes isolados em camadas, reordenação e revelação por elemento, com estados reais e mudanças de composição.

Em 1920×1080, a faixa lateral ocupava 560 px, com logo no alto, índice discreto, contexto e headline embaixo. O campo claro acomodava componentes em escala legível. Indicadores e calendário abriam a composição. Elementos assentavam frontalmente após a entrada em perspectiva.

Capturas de DOM em DPR 2 preservaram o design do produto. Cabeçalhos, shells e cards foram separados; SVGs de gráficos mantiveram os dados originais. Card principal em trânsito ganhava elevação discreta; os demais refluíam, e cabeçalhos/contagens refletiam o estado confirmado. Detalhes, responsáveis, subtarefas e comentário tinham entradas próprias. O filme não dependia de cursor ou scroll.

A identidade era Sora, verde #72f216, verde profundo #1f590e, preto #1e1c20 e gelo #f7f6f6. Esses valores pertencem ao Atria: substitua pelos do sistema atual.

## Estrutura de 60 s usada no Atria

| Tempo | Papel na narrativa | Tratamento visual |
| --- | --- | --- |
| 0–6 s | Promessa e apresentação | Marca oficial e tipografia cinética; produto começa a se formar ao fundo. |
| 6–15 s | Visão geral | Faixa lateral; linhas reais de prazos entram individualmente; responsável aparece; conjunto prepara o quadro. |
| 15–25 s | Fluxo principal | Colunas, cabeçalhos e cards separados. Card atravessa etapas, demais cards refluem e contagens mudam. Detalhes abrem em blocos. |
| 25–35 s | Colaboração | Subtarefas reveladas em sequência, responsável e status atualizados, contagem consistente e comentário real da demonstração. |
| 35–45 s | Indicadores | KPIs isolados; composição abre; caminhos do SVG desenhados progressivamente sem mudar valores. |
| 45–54 s | Integração do trabalho | Planejamento, demanda e responsáveis se organizam; faixa sai; calendário ocupa o espaço com destaque na data relevante. |
| 54–60 s | Assinatura | Logo e mensagem final, respiro e encerramento com áudio bem finalizado. |

Para outro sistema, substitua os fluxos por ações relevantes ao público. Um CRM pode acompanhar uma oportunidade; um ERP, um pedido; uma plataforma educacional, uma jornada de aprendizagem. Não force Kanban e calendário quando não existirem.

## Pontos de partida para movimento

Valores ilustrativos, não um preset obrigatório:

- Entradas escalonadas a cada 3–9 frames em 30 fps, com deslocamentos locais de 24–90 px.
- Springs amortecidas: damping perto de 25, stiffness perto de 115, mass perto de 0,9. Evitar quique ornamental.
- Progressão suave: clamp de t e easing `t*t*(3-2*t)`; opacity e deslocamento podem ter durações diferentes.
- Card atravessa a coluna em cerca de 2 s, enquanto reordenação e atualização de contagem são sincronizadas com sua chegada.
- Perspectiva inicial pequena, perto de 4° em X e −9° em Y, assentando para 0°. Não inclinar texto durante todo o tempo de leitura.
- Cenas mantêm momentos de repouso. Não animar cada elemento continuamente nem usar movimento aleatório.

## Entrega de referência

60 s, 30 fps, 1.800 frames, Full HD, MP4 H.264 yuv420p Rec.709, AAC estéreo 48 kHz; poster e preview separados. O mix foi preservado nas revisões visuais, com cerca de −15 LUFS e −1,4 dBTP.

A narração desse exemplo foi gerada no ElevenLabs com a voz Lucas, em português brasileiro. A conta de origem estava no plano Free e a licença comercial ficou pendente. O exemplo não fornece licença para copiar áudio para outros trabalhos: gere ou obtenha áudio com direitos adequados ao projeto novo e registre sua origem.
