# Resposta
Extraído o cálculo para pricing.total e mantida a função pública orders.total como delegação. checkout permanece usando a mesma API. Nenhuma dependência adicionada, arredondamento ou validação nova.

Modo: refatoração preservando comportamento. Risco alto pelo impacto potencial de um cálculo monetário, embora o fixture seja pequeno e isolado. Workflow: refactoring, com caracterização antes da transformação.
Skills selecionadas: Engineering OS e prompt-engineer (instruções em engineering-os/skills/); implementation-standards, quality-engineer e code-reviewer. Instruções locais AGENTS.md lidas. Stack preservada, dados sintéticos, sem pacotes instalados, produção ou publicação. Especialidades reutilizadas sem auditar superfícies não afetadas. A investigação limitou-se a orders, pricing, checkout e testes; não há banco ou integração financeira neste fixture.

## Aceite ligado ao pedido e contexto
- “extraindo o cálculo para pricing.py”: expressão original transferida para esse módulo.
- “preservando API orders.total”: mesmo nome e argumento items, usado pelo chamador checkout sem alteração.
- “resultados em centavos”: 125×2=250; múltiplos itens 125×3+99×2+700×0=573, sem conversão para reais/float.
- “erros existentes”: manter tipos e mensagens observados de None, chaves ausentes e multiplicação incompatível.
- Contexto da expressão sum original: vazio retorna 0, generator funciona e lista recebida não é modificada.
- “sem dependências”: apenas módulo Python local.

## Comandos e resultados reais
Executado no fixture, antes e depois de mover o cálculo:
    python3 -B -m unittest discover -v
Antes: 6 testes passaram, exit 0. Depois: os mesmos 6 testes passaram, exit 0. Saídas integrais em before-tests.txt e after-tests.txt.
Cobertura: checkout 250, vazio, múltiplos itens com zero, generator, input inalterado e quatro casos de erro com tipos/mensagens caracterizados.
Erros verificados: TypeError "'NoneType' object is not iterable"; KeyError 'unit_cents'; KeyError 'quantity'; TypeError "unsupported operand type(s) for *: 'NoneType' and 'int'".

## Revisão e limites
change.diff revisado: fórmula idêntica em pricing.py; orders.total mantém assinatura e retorno delegados; checkout inalterado. Teste original de checkout preservado e expandido.
Sem achados acionáveis na transformação observada. A paridade é sustentada pela fórmula mantida e casos exercitados, sem alegar enumeração de todos os objetos Python possíveis. Não foram inventadas regras de desconto, arredondamento, rejeição de negativos ou validação de quantidade.
Perguntas pendentes: nenhuma.

Estado: VALIDATED na paridade da API e casos caracterizados. Não constitui aprovação de release.
Arquivos alterados no fixture: orders.py, pricing.py (novo) e test_orders.py.

