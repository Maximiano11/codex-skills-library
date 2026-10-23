# Matrizes de auditoria

Use apenas itens aplicáveis; registre justificativa para os demais. Localize a fonte
da regra no domínio, esquema, contrato, código ou requisito aprovado. Limites ausentes
são decisões pendentes, não licença para inventar restrições.

## Formulários

Para cada campo, registre nome, tipo, obrigatoriedade, regra condicional, limites,
normalização, contrato do backend e cenários. Cubra:

- Obrigatórios omitidos, null, vazio e só espaços; tamanho mínimo/máximo e vizinhos.
- Tipos incorretos, máscara versus valor persistido, Unicode, caracteres especiais,
  normalização e sanitização apropriada ao contexto de uso.
- Email, telefone conforme formato do produto, CPF/CNPJ ou outros documentos apenas
  quando existentes, com dígitos verificadores quando exigidos pelo domínio.
- Negativos, zero, extremos, precisão decimal e limites de datas, datas impossíveis,
  fusos e horário de verão quando relevantes.
- Entradas excessivas e payloads grandes; não confundir limite técnico de segurança
  com regra de negócio. Propor limites ausentes e registrar a decisão.
- Arquivos: tamanho, extensão, conteúdo/MIME, permissão de acesso e armazenamento;
  erros, cancelamento e limpeza de upload incompleto.
- Campos condicionais, dependências, mensagens específicas, foco no erro, associação
  acessível de rótulos e mensagens.
- Loading/disabled, reenvio, clique duplo, timeout, rede lenta/desconectada e retomada.
- Validação equivalente no backend por requisições diretas que contornem o frontend.

## Fluxos e integridade

Mapeie caminhos principal e alternativos, estados vazios e exceções. Valide CRUD,
paginação, ordenação, filtros, busca sem resultados, exclusão com confirmação,
permissões por perfil, expiração de sessão, consistência entre telas, atualização de
cache após mutação e persistência após recarga.

Simule erros de rede e servidor sem corromper dados. Verifique concorrência,
idempotência/duplicidade, transações, rollback, restrições e efeitos externos. Testes
com mocks não substituem integração real frontend/backend/banco para fluxos críticos.
Migrações exigem ensaio com dados sintéticos representativos e estratégia de recuperação.

Asserções devem verificar valores e efeitos: gravação única, valores normalizados,
negação de acesso sem exposição, atualização visível e persistida, rollback completo.
Para isolamento entre tenants, teste também leitura, atualização, exclusão e listagem
usando IDs pertencentes a outra organização e confirme que nada foi alterado.

## Segurança

Inspecione autenticação, autorização no servidor, separação de usuários/organizações,
validação de payloads, exposição de dados e mensagens de erro, tokens/cookies/sessões,
configurações, injeção, uploads, dependências e segredos. Use scanners existentes,
interprete alcance e falsos positivos e registre indisponibilidade do scanner como
não executado. Nunca imprima valores de segredos encontrados.

Avalie rate limiting em operações sensíveis, recuperação de conta, CSRF, CORS,
redirecionamentos e XSS conforme a arquitetura. Não faça varreduras destrutivas,
exfiltração nem testes em contas ou endpoints fora do escopo autorizado.

## UX, acessibilidade e compatibilidade

Teste teclado, foco, semântica, rótulos, erros anunciados e contraste. Combine scanner
existente com inspeção manual; scanner aprovado não comprova acessibilidade completa.
Verifique responsividade e navegadores suportados pelo projeto, zoom e conteúdo longo.
Documente a matriz suportada ausente, sem escolher suporte arbitrário.

## Seleção por risco

Selecione unitários para regras puras e fronteiras, integração para persistência e
transações, API para contratos e acesso, E2E para jornadas reais, regressão para bugs
e acessibilidade para telas alteradas. Registre comando, ambiente, resultado e
artefato de cada camada. Marque camadas não aplicáveis com motivo verificável.

Para bug: antes da correção, execute uma reprodução com falha observável; depois,
execute a mesma asserção e regressões relacionadas. Não use apenas snapshots ou
seletores de presença quando a obrigação é comprovar comportamento.
