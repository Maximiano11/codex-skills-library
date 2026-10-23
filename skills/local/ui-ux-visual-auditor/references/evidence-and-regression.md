# Evidência visual e regressão

## Capturar e inspecionar

Para cada evidência, registre ID, rota/tela, revisão, ambiente, navegador/plataforma,
viewport, escala/DPR quando disponível, tema/idioma, perfil sintético, estado e passos.
Não inclua tokens em URLs nem credenciais em logs. Prefira dados de teste para que
as imagens originais não contenham informações de clientes.

Capture contexto e detalhe: o screenshot inteiro ajuda a entender posição; o recorte
ajuda a localizar o defeito. Abra as imagens usando a ferramenta visual disponível.
Um caminho de arquivo ou log "screenshot saved" não prova que a imagem foi examinada.
Para comportamento temporal, combine sequência de capturas, trace/vídeo disponível
e assertions; uma imagem estática não prova o que aconteceu antes ou depois.

Screenshot não substitui medição de contraste, navegação por teclado, semântica,
validação de formulário ou persistência. Console/rede ajudam a investigar, mas
não atribua todo erro registrado à mudança sem reproduzir e relacionar a causa.

## Comparação confiável

Reutilize infraestrutura existente. Para uma nova regressão web automatizada,
considere o runner e reporter já disponíveis antes de instalar ferramentas.
Automatize primeiro cenários críticos, componentes muito reutilizados e defeitos
com reprodução estável. Use assertions sobre resultados observáveis, não apenas
presença de seletores.

Em screenshot tests:

1. Use dados, locale, fuso, tema, navegador, viewport e fontes controlados.
2. Aguarde o estado esperado e os recursos relevantes, evitando sleeps arbitrários.
3. Controle relógio/animações somente quando não forem o objeto do teste. Teste
   separadamente movimento, loading e transições quando fizerem parte do escopo.
4. Compare baseline e resultado sob condições equivalentes. Inspecione ambos e o
   diff; diferenças de pixels não explicam impacto sozinhas.
5. Revise mudanças intencionais antes de atualizar baseline. Sem baseline aprovada,
   a primeira captura é candidata, não prova de ausência de regressão.

Não aumente tolerâncias para esconder defeitos nem use máscaras sobre regiões cuja
correção precisa ser validada. Limite máscaras a conteúdo não determinístico
justificado, mantendo assertions do comportamento. Não aprove em lote snapshots
alterados. Registre flakiness e investigue; retry verde não elimina a causa.

## Após uma correção autorizada

Mantenha evidência do estado anterior. Reexecute o mesmo cenário, confira o depois
no navegador e teste variações afetadas de tamanho/tema/conteúdo. Para alteração de
token ou componente compartilhado, amplie a amostra para consumidores relevantes.
Não repita a suíte inteira se testes direcionados resolvem o risco.

Se a interface atual mudou após as capturas, refaça as evidências afetadas ou marque
o resultado como referente à revisão antiga. Não declare o HEAD novo validado por
imagens antigas. Guarde originais e identifique recortes/anotações como derivados;
não edite pixels para apresentar um defeito como resolvido.

## Integração com auditoria de produção

Entregue findings com IDs estáveis, severidade, estado e reteste; a auditoria geral
consolida os bloqueadores sem duplicá-los. Um screenshot não é um relatório JUnit.
Quando o gate geral exigir JUnit, use o reporter real do runner, preservando falhas
e skips. Itens visuais/manuais pendentes obrigatórios impedem revisão completa.

Não crie um segundo gate concorrente. Integre verificações na infraestrutura real
quando solicitado e autorizado; mudanças em pipelines de produção exigem revisão
concreta e a aprovação aplicável.
