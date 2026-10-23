# Checklist contextual de UI e UX

Marque executado, falhou, não executado ou não aplicável com justificativa. Não
transforme todos os itens em obrigações universais. Compare primeiro com o produto,
seus usuários, requisitos e referências aprovadas.

## Matriz de cobertura

Registre por cenário: jornada/tarefa, rota/tela, perfil de teste, dados, estado,
viewport, navegador/plataforma, tema, idioma, critério esperado, evidência e resultado.
Se não existir matriz de suporte, escolha e declare uma amostra exploratória:
viewport estreito, intermediário e amplo, mais larguras próximas dos breakpoints
observados. Isso não permite afirmar cobertura de todos os dispositivos/navegadores.

Para componentes compartilhados, identifique consumidores que variam em conteúdo,
densidade ou contexto. Use amostra orientada ao risco; expanda quando achar falhas.

## UI: composição e consistência

- A prioridade visual corresponde à tarefa? A ação principal compete com ações
  secundárias ou destrutivas? O contexto e o estado atual são distinguíveis?
- Compare tokens, tipografia, alinhamento, ritmo de espaçamento, bordas, ícones,
  tamanhos de controles e densidade com o sistema existente.
- Verifique cortes em títulos, rótulos e valores importantes; quebras ruins; ícones
  ilegíveis; imagens/fontes faltando; dimensões que mudam quando conteúdo carrega.
- Examine regiões sticky/fixed, menus, popovers e diálogos em relação ao conteúdo
  e ao foco. Observe a área utilizável quando há banners, barras e teclado virtual.
- Conteúdo longo, textos traduzidos, poucos/muitos registros e ausência de conteúdo
  devem continuar compreensíveis. Não use ocultação para mascarar overflow.
- Se existem temas, valide estados e componentes nos temas afetados; não crie um
  tema novo como condição de aprovação.

## UX: tarefas e decisões

Defina o objetivo e o resultado esperado antes da interação. Registre passos e
obstáculos observados, sem inventar comportamento de usuários.

- Navegação: localização atual, retorno, rotas diretas, continuidade ao recarregar
  e preservação de estado quando fizer parte do contrato.
- Ações: nomes compreensíveis, resultado previsível, indicação de processamento,
  cancelamento e possibilidade de recuperação.
- Formulários: instruções antes do erro, campos condicionais compreensíveis, erro
  associado ao campo, entrada preservada após falha e confirmação inteligível.
- Loading: evite silêncio, falsa conclusão ou ações duplicadas. Teste a transição
  até o resultado, não só um spinner estático.
- Erros: texto que descreva o problema e como prosseguir, preservando informações
  seguras; tente corrigir/repetir e confirme que a interface se recupera.
- Estados vazios: diferencie primeiro uso, sem resultados, falta de permissão e
  indisponibilidade. A próxima ação deve fazer sentido para o estado real.
- Operações irreversíveis: avalie prevenção, confirmação ou reversibilidade conforme
  risco e contrato; nunca execute destruição em dados reais para testar a UX.

## Sistemas internos e dashboards

Valide leitura e comparação de dados, cabeçalhos, unidades, precisão, filtros,
ordenação, paginação, seleção e ações em lote conforme os requisitos.
Tabelas densas não são automaticamente um defeito; confirme legibilidade e tarefas.
Gráficos precisam distinguir séries e comunicar dados sem depender só da cor.
Confira se ocultação responsiva remove informação/ação essencial sem alternativa.

## Responsividade e modalidades de entrada

Teste reflow, zoom, orientação suportada, toque e teclado. Compare o mesmo estado
nos tamanhos selecionados, incluindo componentes abertos e mensagens de erro.
No mobile, emulação de viewport não comprova teclado virtual, safe areas ou
comportamento no dispositivo: registre esses limites ou valide em ambiente apropriado.

Movimento deve permitir uso contínuo e respeitar preferências do usuário. Identifique
saltos de layout, lentidão ou travamento perceptível; meça antes de atribuir causa
ou afirmar cumprimento de métricas de desempenho.

## Referências complementares

As [Web Interface Guidelines](https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md)
podem apoiar inspeção de semântica, foco, feedback, navegação, conteúdo e movimento.
Se usar a skill `web-design-guidelines` em uma revisão concreta, siga seu mecanismo
de consultar as diretrizes atualizadas e registre arquivo/linha dos achados de código.
Suas preferências editoriais, bibliotecas sugeridas e regras de estilo não substituem
contratos do produto, requisitos de acessibilidade ou convenções do idioma.
