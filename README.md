# QuantPro Terminal

Plataforma independente de inteligência quantitativa para futuros, inicialmente **NQ/MNQ** e **GC/MGC**.

## Estado
- F0 Fundação: em implementação
- Research/Paper por padrão
- Live: bloqueado por padrão
- Custo inicial alvo: R$0

## Arquitetura
- apps/web — terminal Next.js/React
- services/api — FastAPI e contratos
- packages/quant_engine — features/modelos
- packages/data_engine — ingestão/normalização
- packages/decision_engine — LONG/SHORT/WAIT
- packages/risk_engine — veto e limites
- packages/ai_analyst — explicação baseada em evidências
- packages/backtest — validação causal
- packages/replay — replay point-in-time
- packages/paper_trading — execução simulada
- docs — decisões, arquitetura e continuidade

## Regra de confiança
Nenhuma porcentagem de confiança é tratada como probabilidade até existir calibração out-of-sample. WAIT é uma decisão válida e o Risk Engine possui veto independente.
