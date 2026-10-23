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
