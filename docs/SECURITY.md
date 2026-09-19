# Security baseline

- Live trading is disabled by default.
- No broker credential is stored in the repository.
- Secrets must be supplied through environment variables/secret stores.
- Research, Paper and Live are separate operating modes.
- Data quality failure forces a risk veto.
- Event-risk blocks can force WAIT.
- Live enablement requires a future explicit approval and a separate implementation checkpoint.
