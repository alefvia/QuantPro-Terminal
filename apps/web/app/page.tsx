"use client";


import { useEffect, useState } from "react";


const RELAY = "https://quantpro-market-relay.onrender.com/terminal/state";
const instruments = [["NQ", "Nasdaq E-mini"], ["MNQ", "Nasdaq Micro"], ["GC", "Gold"], ["MGC", "Micro Gold"]] as const;
const desks = ["Order Flow", "Footprint", "CVD · Imbalance", "Liquidity", "DOM · Add/Pull", "Market Structure"];


type Quote = { price?: number; observed_at?: string };
type TerminalState = { markets?: Array<Quote & { symbol: string }> };


export default function Home() {
  const [data, setData] = useState<TerminalState>({});
  const [online, setOnline] = useState(false);


  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        const response = await fetch(RELAY, { cache: "no-store" });
        if (!response.ok) throw new Error("relay unavailable");
        const next = await response.json();
        if (active) { setData(next); setOnline(Boolean(next.markets?.some((quote: Quote & { symbol: string }) => quote.symbol === "MNQ" && quote.price != null))); }
      } catch { if (active) setOnline(false); }
    };
    load();
    const timer = window.setInterval(load, 5000);
    return () => { active = false; window.clearInterval(timer); };
  }, []);


  const mnq = data.markets?.find((quote) => quote.symbol === "MNQ");
  const price = mnq?.price ? mnq.price.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : "—";
  const updated = mnq?.observed_at ? new Date(mnq.observed_at).toLocaleTimeString("pt-BR") : "aguardando feed";


  return <main>
    <header><div><p className="eyebrow">QUANTPRO · INSTITUTIONAL RESEARCH WORKSTATION</p><h1>Trading Desk</h1><p className="sub">Pesquisa e leitura de mercado — sem execução de ordens</p></div><div className={online ? "status online" : "status"}>{online ? "● DADOS RITHMIC" : "● AGUARDANDO DADOS"}</div></header>
    <nav>{instruments.map(([s,n],i)=><button className={i===1 ? "active" : ""} key={s}><b>{s}</b><small>{n}</small><span>{s === "MNQ" ? price : "—"}</span></button>)}</nav>
    <section className="status"><span>MARKET DATA</span><span className={online ? "online" : ""}>{online ? "ONLINE" : "OFFLINE"}</span><span>Última atualização: {updated}</span></section>
    <section className="workspace"><div className="chart panel"><div className="sectionHead"><div><p className="label">MNQ · LIVE FEED</p><h2>{price}</h2><p className="reason">Preço recebido do Rithmic. Nenhuma ordem pode ser enviada por este painel.</p></div></div><div className="grid">{desks.map(x=><span key={x}>{x}</span>)}</div></div><aside className="panel"><p className="label">DECISION ENGINE</p><strong className="wait">WAIT</strong><p className="reason">Dados em modo leitura. Aguardando confirmação estrutural.</p></aside></section>
    <section><div className="sectionHead"><div><p className="label">ANALYTICS STACK</p><h2>Camadas institucionais</h2></div><span>Sem corretora · execução real bloqueada</span></div></section>
    <footer>Ambiente de pesquisa · Sem ordens de corretora · Execução em dinheiro real permanece bloqueada</footer>
  </main>;
}

