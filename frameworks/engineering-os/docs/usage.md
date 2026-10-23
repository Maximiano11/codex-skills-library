# Uso do framework

No Codex, use `$engineering-os` ou a seleção orientada pelo AGENTS instalado. Começar
por prompt-engineer, confirmar intenção/modo e só então implementar dentro do escopo.
Skills são responsabilidades lógicas; não exigem processos/modelos separados.

O CLI pode ser usado por outra ferramenta sem Codex:

```sh
python3 -B scripts/eos.py discover --project /projeto
python3 -B scripts/eos.py plan --change examples/css-change.json --project /projeto --out /tmp/plano-NOVO.json
python3 -B scripts/eos.py fingerprint --project /projeto
```

`discover` inventaria manifestos e scripts declarados sem executá-los; isso não comprova
arquitetura ou disponibilidade. O agente ainda lê instruções ancestrais e código.
`plan` aceita `request`, `mode` (implement/analyze/plan/explain/audit), `workflow`,
`traits`, `scope` (local/module/system/unknown), `reversible`, `acceptance` e `ambiguities`.
Campos desconhecidos são recusados. O pedido é preservado; critérios são fornecidos
pelo operador após investigação e não inventados pelo CLI. `implementation_ready`
significa apenas que os campos mínimos foram fornecidos sem ambiguidades declaradas.

Para mudanças complexas, use a síntese proporcional da skill; para correções triviais,
basta o aceite e verificação relevante. Não criar documentação para satisfazer formato.
Explicação, análise, planejamento e auditoria preservam o modo; seleção de workflow não
concede permissão para etapas de código, deploy ou migration.

## Verificações e estados

Começar pelo perfil existente do projeto. `examples/profile.json` mostra o contrato,
mas não impõe ferramentas ou política. Revisar argv, destino, efeitos e dados antes
de executar; o framework não fornece sandbox e herda o ambiente do processo.

```sh
python3 -B scripts/eos.py run --project /projeto --profile /perfil.json --out /fora-do-projeto/evidencia-NOVA --allow-exec
python3 -B scripts/eos.py gate --project /projeto --profile /perfil.json --evidence /fora-do-projeto/evidencia-NOVA
```

O output precisa ser novo e externo ao código para não autoalterar o fingerprint.
Comandos são arrays argv, sem shell implícito; shells explícitos ainda executam código
e exigem revisão. O flag autoriza o processo a executá-los, não prova aprovação humana
para efeitos externos. `run` nunca é chamado automaticamente pelo instalador.

Kinds disponíveis: command (resultado do processo para lint/build/etc.), junit
(relatório real de runner, obrigatório para purpose tests) e review (atestação atribuída).
Se a stack não exportar JUnit, usar adapter testado do relatório nativo; enquanto ele
não existir, registrar pendência, sem converter exit 0 em teste aprovado. O runner
`scripts/test.py` exporta resultados reais de unittest para os testes deste framework.

`review` exige atestações externas via `--attestations`, com reviewer, source_sha256,
result passed/failed, criteria/evidence não vazios e findings com severity/open. O hash
vem de fingerprint. Não há aprovação automática de revisão: o autor da atestação
responde por sua veracidade. Evidência ausente ou de outra fonte permanece pendente.

VALIDATED: critérios obrigatórios configurados passaram, incluindo aceite/revisão.
PARTIALLY_VALIDATED: cobertura obrigatória ausente, indisponível, zero testes, skip ou
evidência desatualizada. BLOCKED: critério obrigatório falhou ou há P0/P1 aberto.
Códigos de saída: 0 sucesso/VALIDATED; 1 falha/BLOCKED; 2 PARTIALLY_VALIDATED;
3 erro de contrato/IO. Automação deve tratar 1, 2 e 3 como não aprovados.

Perfis podem omitir checks não aplicáveis, mas a decisão e sua justificativa precisam
constar na avaliação de escopo. Isso não autoriza omitir um critério obrigatório real
para obter verde. O núcleo não pode descobrir a política verdadeira de todo projeto.

O gate confere fingerprint de bytes, modos e identidades de links, perfil e relatório
JUnit. Exclui .git, dependências/venvs/bytecode e nomes de segredos descritos no output;
não é atestação de todo arquivo implantado. Logs brutos de stdout/stderr não são
exibidos ou guardados, apenas hashes/tamanhos. Artefatos escritos pelos próprios
comandos continuam sob responsabilidade de quem os configurou.

Em POSIX, cada comando tem grupo próprio encerrado ao fim/timeout para limpar filhos
herdados; processos que se destacam podem escapar. Em Windows, limpeza é best effort
e não foi testada nesta entrega. Comandos não confiáveis precisam de isolamento externo.
