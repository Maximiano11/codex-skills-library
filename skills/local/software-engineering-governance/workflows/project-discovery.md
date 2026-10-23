# Descoberta — responsável: engenharia/arquitetura

Confirmar diretório, instruções ancestrais/locais, escopo e estado Git sem desfazer
trabalho existente. Ler somente módulos e dependências relevantes; evitar varreduras
de `node_modules`, artefatos, `.env` e credenciais. O helper `discover` inventaria
caminhos e scripts, não comprova arquitetura, cobertura ou segurança.

Investigar manifestos/lockfiles, entrypoints, módulos, contratos, esquema de dados,
validação, autenticação/autorização, integrações, tratamento de erros, testes,
documentação e CI/CD. Diferenciar dependência declarada de disponível/executada.
Inspecionar scripts antes de executá-los; não iniciar serviços ou migrações
automaticamente. Registrar ferramentas ausentes e caminhos que sustentam conclusões.

Entregar diagnóstico com: contexto; arquitetura observada; dependências relevantes;
convenções; riscos; lacunas documentais; lacunas de testes; recomendações proporcionais.
Informação não localizada é 'não identificada', não prova de inexistência.

Saída alimenta requisitos e matriz de impacto: arquivo/módulo → contrato/fluxo →
consumidores → verificações. Reutilizar diagnóstico recente quando ainda válido.
