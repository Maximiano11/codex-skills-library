# Avaliações reproduzíveis

Os testes determinísticos validam contratos do núcleo/instalador/runner. Execute
`python3 -B scripts/test.py --out /tmp/eos-tests-NOVO`; o runner exporta JUnit real.
`python3 -B scripts/eos.py evaluate` materializa os dez fixtures e verifica roteamento,
risco, modo e ausência de mutação pelo planner. Não executa modelo nem implementa
pedidos. scenarios.json contém entradas e arquivos; oracle.json é a rubrica determinística.

Avaliações com modelo são independentes e não se confundem com testes de roteamento:
materializar cada files em diretório temporário novo; entregar ao avaliador somente
request, fixture e as skills pertinentes. Não fornecer oracle, rubrica ou conclusões.
Capturar resposta, skills selecionadas, risco, aceite, alterações e evidências fora do
fixture. Comparar resultado observável e escopo com o pedido; respostas padronizadas
ou matching textual não provam comportamento. Conservar os casos originais para evitar
ajustar o critério depois do resultado. Não expor segredos ou dados de produção.

Cada especialidade tem exemplos e casos em skills/<nome>/evals/. Eles são entradas e
rubricas para validação futura, não resultados executados. O catálogo público não
obriga carregar esses casos no uso rotineiro. A rodada real desta entrega está em
`evaluations/model-run-2026-10-23/`; os dez casos foram executados por dois agentes,
cinco por agente. Não houve contexto novo por caso, grupo de controle ou experimento
estatístico de redução de bugs ou tokens. Esses limites constam na consolidação.

Revisão independente do security-auditor sobre o próprio framework usa código real e
fixtures locais. Relatórios histórico e rechecagem são separados; não apagar a evidência
do defeito ao corrigi-lo. Resultados de auditoria são atribuídos ao revisor, não
transformados pelo gate em uma certificação de veracidade.
