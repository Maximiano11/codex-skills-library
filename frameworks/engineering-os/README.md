# Engineering OS

Framework local de engenharia para agentes. Python 3.10+, biblioteca padrão, sem
serviço, credenciais, SDK ou infraestrutura em nuvem obrigatórios.

O CLI faz triagem explicável, inventaria contexto, coleta evidências e instala
skills com controle de propriedade. O agente continua responsável por interpretar
a linguagem e investigar o código; instruções não interceptam todas as mensagens.

```sh
python3 -B scripts/eos.py validate-package
python3 -B scripts/eos.py plan --change examples/css-change.json --project .
python3 -B scripts/eos.py evaluate
python3 -B scripts/test.py --out /tmp/engineering-os-tests-NOVO
python3 -B scripts/eos.py install --dry-run
python3 -B scripts/eos.py install
python3 -B scripts/eos.py doctor
```

Leia [instalação](docs/installation.md), [uso](docs/usage.md),
[arquitetura](docs/architecture.md), [capacidades Codex](docs/codex-capabilities.md)
e [validação](docs/validation.md). Os caminhos dos exemplos partem desta pasta.
Nenhum deploy, migration ou hook é executado na instalação.
