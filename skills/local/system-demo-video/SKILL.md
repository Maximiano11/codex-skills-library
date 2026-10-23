---
name: system-demo-video
description: Criar e aprimorar vídeos de apresentação de sistemas e SaaS com motion design cinematográfico, interfaces reais em camadas e narração sincronizada, seguindo a direção aprovada do Atria v3. Use para filmes de produto, demonstrações comerciais e vídeos de lançamento; não para tutoriais de navegação ou criação de landing pages.
---

# Vídeos cinematográficos de sistemas

Transforme funcionalidades verificadas em uma narrativa visual de produto. O padrão aprovado é o Atria v3: componentes reais animados individualmente, capítulos editoriais e continuidade entre cenas. Preserve as escolhas do usuário e adapte a linguagem à marca do sistema atual.

Leia [a direção e o storyboard de referência](references/atria-v3.md) no início de um vídeo novo ou de uma revisão estética. O [prompt reutilizável](references/prompt-outro-sistema.md) ajuda a iniciar trabalhos em outros projetos. Os arquivos locais do Atria são exemplos opcionais, não dependências para executar a skill.

## Descobrir o produto e preparar a produção

- Identifique nome, público, objetivo, funcionalidades prioritárias, duração e formatos a partir do pedido e do projeto. Quando não especificados, use como proposta inicial 60 s, 16:9, 1920×1080, 30 fps e português brasileiro. Adapte ao canal; não estique um roteiro para caber em uma duração arbitrária.
- Inspecione aplicação, identidade e componentes existentes antes de desenhar cenas: logos oficiais, cores, tipografia, estados, layout e dados. Confirme ferramentas de captura, render e áudio realmente disponíveis. Reaproveite a stack de produção audiovisual quando existir.
- Use ambiente de demonstração com dados sintéticos e fluxos isolados. Guarde autenticação fora dos assets e dos arquivos entregues. Não exiba informações de clientes em capturas.
- Percorra as funcionalidades que serão mostradas. Registre estados antes/depois de ações significativas, como mover um card, concluir uma subtarefa ou atribuir um responsável. Confirme o resultado persistido quando o roteiro o apresentar como ação real.
- Sem acesso à aplicação ou aos assets necessários, avance no roteiro e nas composições possíveis; identifique a lacuna e peça o insumo específico. Uma UI conceitual, se solicitada, deve ser identificada como conceito. Não entregue funcionalidades inventadas como demonstração do produto.

## Roteiro e direção

Construa uma sequência de benefício → ação observável → resultado. Escolha poucos fluxos que contem uma história. Uma duração curta não comporta uma visita a todos os menus.

Antes do render completo, monte uma tabela com tempo, fala, título curto, componentes, estado inicial/final, movimento e transição. Separe fala de texto em tela: o título reforça uma ideia, sem repetir um parágrafo inteiro da narração. Estime a fala pelo áudio real e ajuste a timeline à locução.

Para o padrão aprovado:

- Faixa lateral escura com logo, contexto/índice do capítulo e título de boa hierarquia; canvas claro para o produto. Cerca de 29%/71% é um ponto de partida em 16:9, não uma obrigação.
- Alterne essa composição com cenas mais abertas de indicadores, calendário ou visão geral. Mantenha uma intenção visual por cena.
- Componentes entram em sequência, se conectam e se reorganizam. O card destacado muda de lugar; outros elementos respondem; os detalhes se revelam por blocos. Uma imagem de página inteira deslizando não substitui essas ações.
- Perspectiva moderada, sombras discretas e movimentos suaves com desaceleração. Termine o movimento em enquadramento legível e reserve tempo de leitura.
- Transições preservam contexto: o objeto ou grupo da cena anterior prepara o próximo. Use cortes simples quando a continuidade não ajudar; não acrescente efeitos sem função.
- Use logo, fontes e cores do novo produto. A faixa escura e a composição são referências de linguagem; o verde do Atria não é uma paleta universal.

## Capturar e compor por camadas

Prefira capturar componentes diretamente do DOM em resolução suficiente, comumente DPR 2. Separe shells, cabeçalhos, cards, listas, responsáveis, comentários e estados de confirmação. Aguarde fontes e imagens antes de capturar. Use dimensões e proporções registradas para posicionar cada asset sem distorção.

Extraia SVGs reais para gráficos quando for viável, preservando dados, eixos e proporções. Anime o desenho dos caminhos com máscaras ou stroke progressivo. Recriação em código pode ser usada quando reproduz fielmente o design e os dados verificados; não troque a interface real por uma UI genérica para facilitar a animação.

Mantenha um manifesto de assets com origem, dimensões, estado representado e cena. Capturas de página inteira servem para orientação ou contexto breve; a demonstração principal usa elementos independentes. Não dependa de cursor, scroll ou zoom contínuo de uma gravação de tela para dar movimento ao filme.

Use composição programática determinística quando disponível, como React/Remotion ou equivalente. Separe conteúdo, configuração da marca, timeline e primitivas de movimento. Prefira tempos em frames e uma única fonte para duração/FPS. Prepare falhas explícitas de carregamento de assets/fontes; não renderize silenciosamente quadros incompletos.

## Áudio

- Quando ElevenLabs for pedido, use a conta e os meios autorizados disponíveis. Verifique voz, idioma, qualidade e direitos de uso da geração atual. Não presuma que o histórico de outra conta ou vídeo se aplica ao projeto novo.
- Gere por blocos narrativos para permitir ajustes; ouça pronúncia do nome do produto, pausas e cortes. Guarde texto e áudio correspondentes. Não acelere a voz de forma artificial para esconder um roteiro longo.
- Use trilha com direitos adequados e registre a fonte. Ajuste a música abaixo da fala, com ducking e fades suaves. Como referência inicial para web, aproximadamente −16 a −14 LUFS integrados e true peak até −1 dBTP; ajuste pela audição e pelo destino.
- Preserve voz, roteiro e mix aprovados em revisões apenas visuais. Reutilize o stream de áudio quando tecnicamente adequado, sem regenerar ou recomprimir sem necessidade.
- Ausência de uma licença é uma pendência identificada, não um motivo para inventar direitos ou comprar um plano. Não contrate serviços nem publique por iniciativa da skill; siga o pedido e as autorizações existentes, esclarecendo restrições concretas.

## Validar e entregar

Renderize primeiro quadros de momentos-chave e uma prévia leve. Inspecione as imagens efetivamente renderizadas e assista à prévia, inclusive trechos em movimento. Corrija legibilidade, sobreposição, recortes, velocidade, rigidez e continuidade antes do render final. Não declare qualidade visual apenas por ler o código.

No arquivo final, confira:

- Render completo, duração, FPS, resolução e áudio correspondentes à timeline; início, transições e último quadro sem falhas, congelamentos acidentais ou assets ausentes.
- Ações por componente e estados antes/depois consistentes com a aplicação. Animação editorial não implica que o aplicativo tenha esses mesmos efeitos em execução.
- Hierarquia e legibilidade no tamanho de exibição pretendido; se a versão móvel exigir outro enquadramento, recompose em vez de comprimir tudo.
- Sincronia da fala com a ação e reprodução sem clipping, cortes de sílabas ou música cobrindo a voz.
- Para web, H.264 em MP4, yuv420p e faststart são uma base compatível; áudio AAC. Verifique range e tags de cor no arquivo real, sem aplicar conversão cega que altere pretos e brancos.

Entregue MP4 final, poster, prévia e fontes editáveis com assets necessários, roteiro/timeline e instruções reais de render. Registre o que foi verificado e pendências concretas. Mantenha versões aprovadas separadas de revisões. A entrega principal é o vídeo pronto; não encerre apenas com um plano ou storyboard quando renderizar estiver ao alcance.

Integração em site ou publicação só entra no escopo quando solicitada. Nesse caso, use player acessível com reprodução voluntária, controles, poster e alternativa textual; valide o vídeo no destino real.
