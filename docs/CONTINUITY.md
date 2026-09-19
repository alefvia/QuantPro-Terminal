# QuantPro Terminal — Continuável

Data: 2026-09-19
Versão: 0.4
Branch: data/f1-f2-2026-09-19

## Decisões canônicas
- Projeto independente da ALEFVIA.
- Mercados iniciais: NQ/MNQ e GC/MGC.
- Custo inicial alvo: R$0.
- IA interpreta evidências; não inventa dados/sinais.
- WAIT é decisão de primeira classe.
- Risk Engine possui veto.
- MBO/Level 3 preparado, mas desativado inicialmente.
- Research -> OOS/walk-forward -> Paper -> somente depois avaliar Live.

## Fases
F0 Fundação — CONCLUÍDA (CI Python + Web verde)
F1 Dados gratuitos — IMPLEMENTADA; validação CI pendente
F2 Data/feature store — IMPLEMENTADA; validação CI pendente
F3 Terminal — PENDENTE
F4 Structure/Volume/Volatility — PENDENTE
F5 Macro/Intermarket/Positioning/Event — PENDENTE
F6 Regime/baseline — PENDENTE
F7 Backtest causal — PENDENTE
F8 Replay/journal — PENDENTE
F9 Decision + AI Analyst — PENDENTE
F10 Risk + Paper — PENDENTE
F11 Walk-forward/paper ao vivo — PENDENTE
F12 Level 2 — PENDENTE
F13 MBO A/B — PENDENTE
F14 Live — BLOQUEADO

## Evidência F0
- CI GitHub Actions: Python SUCCESS (install, Ruff, pytest).
- CI GitHub Actions: Web SUCCESS (npm install, Next.js build).
- API Research com Live desabilitado.
- Risk Engine com veto e WAIT.
- Frontend-base criado.

## Próximo checkpoint
Iniciar F1: fontes gratuitas, catálogo de dados, conectores macro/COT e primeira persistência reproduzível.


## F1/F2 — 19/09/2026
Implementados catálogo macro/intermarket, cliente FRED, adapter CFTC, validação de qualidade, esquema temporal canônico, Parquet atômico, manifests SHA-256, filtro point-in-time e testes. Dados de futuros NQ/GC em tempo real não são simulados: exigem feed legal específico. FRED requer chave do usuário e permanece fora do repositório.
