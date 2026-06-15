# Decisões — Tech Challenge Fase 2

Pontos que precisam de alinhamento do time antes de fechar a implementação do AG.

---

## Decisão 1 — Recall mínimo aceitável

O modelo atual usa threshold `0.40` para garantir recall ≥ 0.80, mas isso gera **82k falsos positivos**, o que representa um custo operacional alto para o SUS. Abaixar o piso reduz FP significativamente.

| Opção | Recall mínimo | FP estimado | FN estimado |
|---|---|---|---|
| 🔴 Manter atual | 0.80 | ~82.000 | ~2.600 |
| 🟡 Intermediário | 0.70 | ~50.000 | ~4.500 |
| 🟢 Mais tolerante | 0.65 | ~40.000 | ~5.500 |

---

## Decisão 2 — Quantos FN a mais são toleráveis?

Hoje temos **2.627 FN** (prematuros não identificados pelo modelo). FN é mais caro que FP — um prematuro não identificado representa risco de vida e custo de UTI neonatal de emergência.

Qual é o limite que o time aceita aumentar para viabilizar a redução de FP?

- Nenhum — FN é inegociável, não pode crescer
- Até 500 a mais (~3.100 total)
- Até 1.000 a mais (~3.600 total)

---

## Decisão 3 — Objetivo do AG na Fase 2

Dois caminhos são válidos e defensáveis no relatório:

**Opção A — AG tenta melhorar o modelo**
Usamos F1 como fitness (penaliza mais FP que F2). O AG busca hiperparâmetros que melhorem a curva precision-recall. Resultado esperado: melhoria marginal (~0.01–0.02 de AUC-PR).

**Opção B — AG confirma o teto do modelo**
Mantemos a fitness similar à Fase 1. O AG chega a resultados próximos do RandomizedSearch, demonstrando experimentalmente que o espaço de hiperparâmetros já estava esgotado. A conclusão é que a próxima alavanca real é a qualidade dos dados — o que é um resultado científico válido e defensável.

---

## Decisão 4 — Os dados foram atualizados?

O notebook está rodando com shape `(562.520 linhas, 26 colunas)` — diferente do original da Fase 1 que tinha `(552.344 linhas, 29 colunas)`. Isso afeta a comparação com o baseline.

- ✅ Sim — dados foram atualizados intencionalmente (ex: inclusão do ano 2022)
- ❌ Não — provavelmente é um erro no caminho dos arquivos ou no preprocessing

> Se a resposta for sim, o baseline da Fase 1 precisa ser recomputado com os novos dados para a comparação ser justa.

---

## Decisão 5 — Implementar threshold estratificado por perfil de risco?

Em vez de um único threshold para todos os 140k pacientes, aplicamos limiares diferentes por perfil clínico. O notebook 04 (SHAP) já identificou as features mais importantes — o trabalho de definição dos perfis está em grande parte feito.

**Como funciona:**

| Perfil | Threshold | Efeito |
|---|---|---|
| Alto risco (pré-natal tardio, histórico de perda fetal, primípara jovem/idosa) | 0.35–0.38 | Captura quase tudo → FN mínimo |
| Baixo risco | 0.55–0.60 | Rejeita FP óbvios → reduz custo |

**Resultado esperado:** redução de ~20–30% nos FP com crescimento mínimo de FN, sem treinar nenhum modelo novo.

**Importante:** essa decisão é independente das outras — pode ser aplicada com qualquer combinação de hiperparâmetros que o AG encontrar. Se o AG não melhorar muito o modelo base, o threshold estratificado pode ser o resultado mais concreto e impactante da Fase 2.

- ✅ Sim — implementamos no Bloco 6 como parte da avaliação final
- ❌ Não — mantemos threshold único por simplicidade
- 🤔 Talvez — avaliamos depois de ver os resultados do AG
