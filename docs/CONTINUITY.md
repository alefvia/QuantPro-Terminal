# QuantPro Terminal — Continuável

Data: 2026-09-19
Versão: 0.7
Branch: validation/f8-f10-2026-09-19

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
F1 Dados gratuitos — CONCLUÍDA (CI verde)
F2 Data/feature store — CONCLUÍDA (CI verde)
F3 Terminal — CONCLUÍDA (CI verde)
F4 Structure/Volume/Volatility — CONCLUÍDA (CI verde)
F5 Macro/Intermarket/Positioning/Event — CONCLUÍDA (CI verde)
F6 Regime/baseline — CONCLUÍDA (CI verde)
F7 Quant/ML foundation — CONCLUÍDA (CI verde)
F8 Backtest/walk-forward — CONCLUÍDA (CI verde)
F9 Replay/journal — CONCLUÍDA (CI verde)
F10 Decision + AI Analyst — CONCLUÍDA (CI verde)
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

## Evidência F1/F2
- Commit 33ce0ab: Python CI SUCCESS (install, Ruff, pytest).
- Web CI SUCCESS (Next.js build).
- Testes incluem anti-look-ahead point-in-time e round-trip Parquet.
- Próxima fase: F3 Terminal com dados/estado dos conectores.

## F3/F4 — 19/09/2026
Terminal profissional base para NQ/MNQ/GC/MGC implementado, com estados explícitos de feed, Decision/Risk e níveis. Market Engine implementa VWAP, ATR, realized volatility, range position, trend baseline, Volume Profile POC/VAH/VAL e session levels. Sem feed, UI permanece OFFLINE/WAIT e não inventa preços.

## Evidência F3/F4
- Python: SUCCESS (Ruff + pytest).
- Web: SUCCESS (Next.js production build).
- Próxima fase: F5 Macro/Intermarket/Positioning/Event.

## F5/F6/F7 — 19/09/2026
Implementados macro/intermarket, COT positioning, event risk, regime detector, feature vector, baseline quantitativo transparente, split temporal e ensemble com WAIT por desacordo. Probabilidade continua indisponível até calibração OOS.

## Evidência F5/F6/F7
- Python CI SUCCESS (Ruff + pytest).
- Web CI SUCCESS.
- Próximo bloco: backtest causal/walk-forward, replay e journal.

## F8/F9/F10 — 19/09/2026
Backtest com custos/slippage e métricas, walk-forward temporal, replay por available_at, decision log/journal, TradeThesis e AI Analyst explicável implementados. Evento/veto força WAIT; probabilidade continua não calibrada.

## Evidência F8/F9/F10
- Python CI SUCCESS: Ruff + pytest.
- Web CI SUCCESS.
- Próximo bloco: Risk Engine avançado + Paper Trading + validação paper.
