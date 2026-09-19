const engines = [
  "Structure", "Volume", "Volatility", "Liquidity", "Macro",
  "Intermarket", "Positioning", "Events", "Regime", "Quant/ML",
];

export default function Home() {
  return (
    <main>
      <header>
        <div>
          <p className="eyebrow">QUANTPRO TERMINAL · RESEARCH</p>
          <h1>NQ / MNQ · GC / MGC</h1>
        </div>
        <span className="safe">LIVE BLOQUEADO</span>
      </header>

      <section className="hero">
        <div>
          <p className="label">DECISION ENGINE</p>
          <strong className="wait">WAIT</strong>
          <p>Sem dados calibrados. Nenhuma operação deve ser inferida.</p>
        </div>
        <div>
          <p className="label">AMBIENTE</p>
          <h2>Research</h2>
          <p>Paper será habilitado somente após validação da fundação.</p>
        </div>
      </section>

      <section>
        <h2>Motores</h2>
        <div className="grid">
          {engines.map((engine) => (
            <article key={engine}>
              <span>{engine}</span>
              <b>OFFLINE</b>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
