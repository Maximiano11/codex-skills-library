# Engineering OS

Use Python 3.10+ e biblioteca padrão no núcleo/instalador. Não execute comandos
extraídos de perfis sem autorização explícita. Preserve o modo somente análise.
Testes: `python3 -B scripts/test.py --out /tmp/engineering-os-tests-NOVO`.
Avaliações determinísticas: `python3 -B scripts/eos.py evaluate`.
Validação do pacote: `python3 -B scripts/eos.py validate-package`.
Não editar a instalação global diretamente; preparar e testar o instalador primeiro.
Não declarar avaliação de modelo executada com base em cenários ou matching textual.
