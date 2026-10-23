# Núcleo independente de plataforma

O pacote engineering_os expõe orchestrator.plan/discover, gates.collect/verify/verdict,
validation.validate_package/evaluate e util.fingerprint. Entradas JSON de schema 1,
ContractError para violações; sem dependências de SDK, Codex, Git, rede ou framework web.
O CLI é scripts/eos.py e carrega o adaptador apenas nas operações específicas.
