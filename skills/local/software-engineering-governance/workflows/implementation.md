# Implementação — responsável: engenharia

Trabalhar apenas no escopo aceito. Revisar diff e convenções antes de editar;
preservar alterações de terceiros. Implementar a solução mais simples que satisfaça
o aceite. Validar tipos/entradas, erros e contratos no limite de confiança.
Considerar consistência, concorrência, compatibilidade e não exposição de dados.

Para bug, reproduzir em ambiente descartável; acrescentar regressão que falhe antes
e passe depois quando viável. Não exigir teste novo para texto/layout reversível sem
risco comportamental: inspeção real apropriada pode ser suficiente.

Inspecionar efeitos dos comandos; usar ferramentas existentes, sem instalação
redundante. Não executar migrations, seeds ou serviços que apontem para dados reais.
Atualizar documentos existentes somente quando o comportamento/instrução registrado
mudar. Gate 3: aceite implementado, contratos preservados e diff sem escopo indevido;
compilação sozinha não valida o comportamento.
