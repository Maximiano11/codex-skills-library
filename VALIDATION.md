# Validação da preparação open source — 23/10/2026

- Distribuição separa material original MIT, terceiros com MIT/Apache-2.0 verificáveis
  e referências sem redistribuição. Licenças/copyrights originais preservados.
- Não contém cópia dos diretórios de plugins restritos ou sem licença confirmada.
- Não inclui credenciais, configurações pessoais, caches ou logs de sessão.
- Os entrypoints das skills preservadas não foram reescritos; foram adicionadas licenças.
- O Engineering OS é validado pelo próprio catálogo e suíte de 62 testes na cópia preparada.
- Histórico Git novo é preparado localmente; publicação/substituição do histórico anterior
  depende de autorização explícita. Remover arquivos de HEAD não remove versões anteriores.

## Instalador seletivo da biblioteca — 23/10/2026

- `python3 -B -m unittest discover -s tests -v`: 20 testes passaram em macOS,
  com perfis temporários, sem instalação no perfil global real.
- Cobertura: cópia integral das 36 skills, seleção, hashes, bits executáveis,
  idempotência, preservação de AGENTS/configuração/skills alheias, conflitos de lote,
  fontes e destinos com links, travessia de paths, precedência de perfil explícito,
  proteção de skills `.system` e destino criado por outro processo antes da cópia.
- Menu interativo e cancelamento conferidos em terminal; listagem e links locais
  do README conferidos. Prévia no perfil real recusou conflito sem escrever.
- Escopo VALIDATED: comportamento do instalador nos cenários acima. Não comprova
  descoberta das skills por todos os clientes ou operação em Windows/Linux.
- Não há atualização, remoção, rollback transacional ou isolamento contra alterações
  concorrentes. Falhas de IO podem deixar cópias novas parciais, conforme o README.
- Testes do runtime Engineering OS não repetidos: nenhum arquivo do framework foi
  alterado; esta validação cobre o novo instalador independente.

## Atualização e desinstalação gerenciadas — 23/10/2026

- `python3 -B -m unittest discover -s tests -v`: **43 testes passaram** em macOS,
  incluindo as 20 regressões do instalador e 23 cenários do ciclo de vida.
- Atualização aplica conteúdo novo e remoções do catálogo; backup conserva bytes,
  estrutura e permissões anteriores. Desinstalação move os originais para backup.
- Verificados: estado de propriedade, adoção explícita somente de cópias idênticas,
  preservação de arquivos/configurações alheios, conflitos de lote, edições locais,
  arquivos extras/ausentes, permissões, fontes adulteradas, links, estado alheio,
  lock, prévias sem escrita e idempotência sem backup redundante.
- Simuladas falhas antes da movimentação, depois do backup e ao salvar o estado:
  originais recuperáveis, journal pendente e bloqueio de operações subsequentes.
- Comandos CLI `update` e `uninstall --all` executados em perfil temporário;
  ajuda dos comandos e links locais do README conferidos.
- Escopo incremental **VALIDATED**: instalador e preservação nos cenários executados.
  Nenhuma instalação global real foi atualizada ou desinstalada.
- Esta seção substitui o limite anterior de ausência de update/uninstall. Continua
  sem rollback automático, mesclagem de adaptações ou transação de lote. Lock é
  cooperativo; ACLs, atributos estendidos, falha de energia e Windows/Linux não
  foram validados. Recuperação manual está descrita no README.
- Runtime Engineering OS não alterado; sua suíte não foi repetida nesta mudança.
