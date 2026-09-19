const instruments = [
  { symbol: "NQ", name: "Nasdaq-100 E-mini" },
  { symbol: "MNQ", name: "Nasdaq-100 Micro" },
  { symbol: "GC", name: "Gold" },
  { symbol: "MGC", name: "Micro Gold" },
];
const engines = ["Structure","VWAP","Volume Profile","ATR / Volatility","Macro","Intermarket","Positioning","Events","Regime","Quant / ML"];
const levels = ["VWAP","POC","VAH","VAL","Prev. High","Prev. Low","Overnight High","Overnight Low","Opening Range"];

export default function Home() {
  return <main>
    <header><div><p className="eyebrow">QUANTPRO · PROFESSIONAL RESEARCH TERMINAL</p><h1>Market Intelligence</h1></div><div className="badges"><span className="badge">RESEARCH</span><span className="danger">LIVE BLOQUEADO</span></div></header>
    <nav>{instruments.map(x=><button key={x.symbol}><b>{x.symbol}</b><small>{x.name}</small></button>)}</nav>
    <section className="terminal">
      <div className="chart">
        <div className="sectionHead"><div><p className="label">NQ · MARKET STRUCTURE</p><h2>Feed de futuros aguardando conexão</h2></div><span className="offline">OFFLINE</span></div>
        <div className="placeholder"><div className="bars"/><p>Nenhum preço é fabricado. O gráfico será ativado quando houver um feed permitido.</p></div>
        <div className="levels">{levels.map(x=><div key={x}><span>{x}</span><b>—</b></div>)}</div>
      </div>
      <aside>
        <p className="label">DECISION ENGINE</p><strong className="wait">WAIT</strong>
        <p>Sem dados de mercado suficientes para decisão.</p>
        <hr/><p className="label">RISK ENGINE</p><b>VETO ATIVO</b><p>Data quality gate impede operação sem dados.</p>
        <hr/><p className="label">PROBABILIDADE</p><b>INDISPONÍVEL</b><p>Somente após calibração out-of-sample.</p>
      </aside>
    </section>
    <section><div className="sectionHead"><h2>Motores</h2><span className="muted">F3/F4</span></div><div className="grid">{engines.map((x,i)=><article key={x}><span>{x}</span><b className={i<4?"ready":"pending"}>{i<4?"READY":"PENDING"}</b></article>)}</div></section>
  </main>
}
