# Codex Skills Library

Coleção open source de skills e do Engineering OS, com licença MIT para nossas
contribuições originais e preservação das licenças de terceiros.

- **36 skills redistribuíveis incluídas**, com seus scripts, referências e assets.
- **43 skills adicionais catalogadas como referências externas**, sem copiar materiais
  cuja licença proíba redistribuição ou cuja licença aberta não tenha sido confirmada.
- **79 entradas no catálogo**: as skills disponíveis na instalação de origem continuam mapeadas.
- **Engineering OS completo**: núcleo Python, 13 skills, 9 workflows, instalador, gates e testes.

Veja [CATALOG.md](CATALOG.md), [manifest.json](manifest.json) e
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) para escopo e atribuições.
As referências a plugins não incluem suas ferramentas MCP, contas ou runtimes nativos.

## Engineering OS

```sh
python3 -B frameworks/engineering-os/scripts/eos.py validate-package
python3 -B frameworks/engineering-os/scripts/eos.py install --dry-run
python3 -B frameworks/engineering-os/scripts/eos.py install
python3 -B frameworks/engineering-os/scripts/eos.py doctor
```

Skills individuais podem ser instaladas a partir das pastas do catálogo. Preserve
configurações existentes; ferramentas e integrações nativas exigem disponibilidade
e permissões próprias. Referências de caminhos locais históricos podem precisar de adaptação.

## Licenças

[MIT](LICENSE) para Engineering OS e contribuições originais listadas no manifesto.
As skills de Leonxlnx/taste-skill mantêm MIT e sua atribuição. As skills Apache-2.0
mantêm seus arquivos de licença. Nenhum material restrito é relicenciado como MIT.
Disponibilidade local ou visibilidade pública de um repositório não concede direitos
adicionais sobre materiais de terceiros. Use os canais oficiais dos plugins referenciados.

## Privacidade e verificação

Não inclui credenciais, configurações pessoais, caches ou logs brutos de sessão.
O Engineering OS tem testes próprios e evidências sintéticas; as integrações externas
não são declaradas validadas por estarem no catálogo. AGENTS e skills orientam agentes,
sem interceptação técnica garantida de toda mensagem.
