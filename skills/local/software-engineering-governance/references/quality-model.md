# Modelo de qualidade e proveniência

## Fonte local analisada integralmente

Garcia, Felipe Molina; Altoé, Gustavo Fernandes; Teodoro, Karina Angélica; Facci,
Marcio Antonio. **Criação de um checklist de validação de software baseado no modelo
ISO/IEC 25010**. Revista e-Fatec, v. 15, n. 1, novembro de 2025. PDF fornecido pelo
usuário, 14 páginas. SHA-256:
`4ab43e69d2ec638b5af2d518f0b4a983ab017c8f607018678451d2cfa4e49de3`.

Leitura: texto das páginas 1–14 extraído com pdfplumber; figuras 1–6 das páginas
7–12 renderizadas e inspecionadas visualmente. As perguntas estão em imagens e
não aparecem na extração textual comum. Catalogação manual em paráfrases, preservando
número e localização, sem alegar transcrição literal nem OCR perfeito.

| Página/figura | Números | Bloco efetivamente impresso |
| --- | --- | --- |
| 7 / 1 | 1–20 | Funcionalidade |
| 8 / 2 | 21–40 | Confiabilidade |
| 9 / 3 | 41–60 | Usabilidade |
| 10 / 4 | 61–80 | Eficiência |
| 11 / 5 | 81–100 | Manutenibilidade |
| 12 / 6 | 101–120 | Portabilidade |

O texto do artigo enumera oito características; as figuras possuem seis blocos.
Interoperabilidade (5–6) e Segurança Funcional (7–8) estão em Funcionalidade;
Resiliência a Ataques (35–36) em Confiabilidade; Coexistência (105–106) em
Portabilidade. Preservar essa organização em `source.original_group` e
`original_subheading`; não atribuí-la como taxonomia normativa ISO.

O artigo é um instrumento **teórico**: p. 13 afirma necessidade de validação
posterior em estudos de caso e dependência do julgamento dos avaliadores. Não
há demonstração empírica de redução de defeitos/retrabalho no PDF. Esses resultados
precisam de medição no piloto; não inventar baseline, participantes ou percentuais.

## Quatro origens distintas

1. `article_paraphrase`: os 120 títulos/descrições adaptam perguntas identificadas
   pelas seis figuras. Página/figura/número permitem voltar ao original.
2. Norma: só declarar requisito normativo específico quando houver acesso legítimo
   ao texto/edição/cláusula que o comprova. Não há texto integral licenciado das
   normas anexado. Catálogos oficiais confirmam finalidade/edição, não conformidade.
3. `engineering_practice`: testes de regressão, ADR, revisão de ameaças e heurísticas
   de projeto são práticas complementares; não atribuir automaticamente à ISO.
4. `skill_rule`: score de risco, estados, gates e regra de evidências são decisões
   desta implementação. Severidade, métodos e seleção incremental dos 120 itens
   também são adaptações da skill, não conclusões normativas do artigo.

## Mapeamento 2011 → 2023

O catálogo oficial confirma nove características no modelo de produto 2023.
O mapeamento abaixo é uma interpretação operacional em nível de característica;
não é equivalência integral de subcaracterísticas nem certificação.

| 2011 usada como referência do artigo | Roteamento 2023 nesta skill |
| --- | --- |
| Adequação funcional | `functional_suitability` |
| Eficiência de desempenho | `performance_efficiency` |
| Compatibilidade | `compatibility` |
| Usabilidade | `interaction_capability` — rever interação/inclusividade no contexto |
| Confiabilidade | `reliability` |
| Segurança da informação | `security` |
| Manutenibilidade | `maintainability` |
| Portabilidade | `flexibility` — não pressupor equivalência exata |
| Sem bloco específico no artigo | `safety` — avaliar dano e operação segura separadamente |

Cada item contém listas `iso_2011_mapping`, `iso_2023_mapping` e
`mapping_authority: skill_interpretation_not_normative`. Escalabilidade (75–76)
também é roteada para flexibilidade. Safety não se confunde com segurança da
informação: `GOV-SAFE` é complemento próprio; avaliar restrições operacionais,
identificação de perigo, falha segura, avisos e integração segura conforme o produto.
Para uso normativo formal, revisar a edição licenciada, incluindo diferenças de
subcaracterísticas e o modelo de qualidade em uso separado.

## Operacionalizar um critério

Definir: regra/fonte → contexto e aplicabilidade → cenário → asserção/limiar
pré-definido → ferramenta/método → evidência da execução → resultado. Uma pergunta
ampla pode exigir vários testes; várias perguntas podem compartilhar a mesma
evidência, desde que ela realmente comprove cada asserção. Contagem não é cobertura.

Estados são distintos da escala qualitativa. N/A precisa de motivo e revisão;
`not_verified`/`blocked` não são sucesso. O helper não faz média para aprovar.

## Rubrica qualitativa própria (exemplo adaptável)

Definir rubrica específica e registrar **antes** da observação. Para maturidade do
processo: 1 = prática ausente observada; 2 = prática ad hoc com lacunas demonstradas;
3 = procedimento definido com execução parcial comprovada; 4 = procedimento executado
consistentemente no escopo e sem lacunas relevantes observadas; 5 = nível 4 mais
monitoramento de resultados e melhoria demonstrada no período definido. Sem evidência,
deixar pontuação ausente, não atribuir 1 automaticamente. Pontuação não converte
teste falho em aprovação. A ISO 25023 não fornece um limiar universal para este score.

Fontes oficiais e limites: [standards.md](standards.md).
