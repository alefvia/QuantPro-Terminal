"use client";

import { useEffect, useMemo, useState } from "react";

const RELAY = "https://quantpro-market-relay.onrender.com";
const frames = ["1m", "5m", "15m"] as const;
type Frame = (typeof frames)[number];
type Candle = { time: number; open: number; high: number; low: number; close: number; volume: number; buy_volume: number; sell_volume: number };
type Level = { level: number; price: number; size: number };
type Book = { bids: Level[]; asks: Level[] };
type State = { markets?: { symbol: string; price?: number; last_event?: { observed_at?: string } }[]; mnq?: { cvd?: number; trade_count?: number; event_count?: number; book?: Book } };

function fmt(value?: number) { return value == null ? "—" : value.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }

function CandleChart({ candles }: { candles: Candle[] }) {
  const model = useMemo(() => {
    if (!candles.length) return null;
    const display = candles.slice(-72);
    const high = Math.max(...display.map((c) => c.high));
    const low = Math.min(...display.map((c) => c.low));
    const range = Math.max(high - low, 0.25);
    const width = 960, height = 350, pad = 20, step = (width - pad * 2) / display.length;
    const y = (price: number) => pad + ((high - price) / range) * (height - pad * 2);
    return { width, height, pad, step, y };
  }, [candles]);
  if (!model) return <div className="placeholder"><strong>AGUARDANDO TRADES RITHMIC</strong><p>As velas aparecem quando os negócios reais chegam ao relay.</p></div>;
  return <svg className="candleChart" viewBox={`0 0 ${model.width} ${model.height}`} role="img" aria-label="Candles reais do MNQ">
    {[0.2, 0.4, 0.6, 0.8].map((line) => <line key={line} x1="0" x2={model.width} y1={model.height * line} y2={model.height * line} stroke="#1b2835" strokeWidth="1" />)}
    {display.map((candle, index) => { const x = model.pad + index * model.step + model.step / 2; const up = candle.close >= candle.open; const color = up ? "#38c99b" : "#ff6e82"; const top = model.y(Math.max(candle.open, candle.close)); const body = Math.max(2, Math.abs(model.y(candle.open) - model.y(candle.close))); return <g key={candle.time}><line x1={x} x2={x} y1={model.y(candle.high)} y2={model.y(candle.low)} stroke={color} strokeWidth="1.5"/><rect x={x - Math.max(1.5, model.step * .28)} y={top} width={Math.max(3, model.step * .56)} height={body} fill={color}/></g>; })}
  </svg>;
}

export default function Home() {
  const [frame, setFrame] = useState<Frame>("1m");
  const [state, setState] = useState<State>({});
  const [candles, setCandles] = useState<Candle[]>([]);
  const [book, setBook] = useState<Book>({ bids: [], asks: [] });
  const [online, setOnline] = useState(false);
  useEffect(() => {
    let active = true;
    const load = async () => { try {
      const [stateRes, chartRes, bookRes] = await Promise.all([fetch(`${RELAY}/terminal/state`, { cache: "no-store" }), fetch(`${RELAY}/terminal/chart?symbol=MNQ&timeframe=${frame}`, { cache: "no-store" }), fetch(`${RELAY}/terminal/book?symbol=MNQ`, { cache: "no-store" })]);
      if (!stateRes.ok || !chartRes.ok || !bookRes.ok) throw new Error("relay unavailable");
      const next = await stateRes.json(), chart = await chartRes.json(), depth = await bookRes.json();
      if (active) { setState(next); setCandles(chart.candles ?? []); setBook(depth.book ?? { bids: [], asks: [] }); setOnline(Boolean(next.markets?.find((m: {symbol:string}) => m.symbol === "MNQ")?.price)); }
    } catch { if (active) setOnline(false); } };
    load(); const timer = window.setInterval(load, 5000); return () => { active = false; window.clearInterval(timer); };
  }, [frame]);
  const mnq = state.markets?.find((market) => market.symbol === "MNQ");
  const updated = mnq?.last_event?.observed_at ? new Date(mnq.last_event.observed_at).toLocaleTimeString("pt-BR") : "aguardando feed";
  const rows = Math.max(book.asks.length, book.bids.length, 5);
  return <main>
    <header><div><p className="eyebrow">QUANTPRO · MARKET INTELLIGENCE WORKSTATION</p><h1>MNQ Market Structure</h1><p className="sub">Rithmic Test · análise somente · execução bloqueada</p></div><div className={online ? "badge" : "danger"}>{online ? "● DADOS RITHMIC" : "● AGUARDANDO DADOS"}</div></header>
    <nav>{[["NQ", "Nasdaq E-mini"], ["MNQ", "Nasdaq Micro"], ["GC", "Gold"], ["MGC", "Micro Gold"]].map(([symbol, name]) => <button className={symbol === "MNQ" ? "active" : ""} key={symbol}><b>{symbol}</b><small>{name}</small><span>{symbol === "MNQ" ? fmt(mnq?.price) : "—"}</span></button>)}</nav>
    <section className="status"><div><span>MARKET DATA</span><b className={online ? "ready" : "red"}>{online ? "ONLINE" : "OFFLINE"}</b></div><div><span>TIMEFRAME</span><b>{frame}</b></div><div><span>ÚLTIMO EVENTO</span><b>{updated}</b></div><div><span>EXECUÇÃO</span><b className="red">DISABLED</b></div></section>
    <section className="workspace"><div className="chart panel"><div className="sectionHead"><div><p className="label">MNQ · HISTÓRICO CME + RITHMIC AO VIVO</p><h2>{fmt(mnq?.price)}</h2></div><div className="timeframes">{frames.map((item) => <button className={frame === item ? "active" : ""} onClick={() => setFrame(item)} key={item}>{item}</button>)}</div></div><CandleChart candles={candles}/><div className="metricGrid"><div><span>CVD</span><b>{state.mnq?.cvd ?? "—"}</b></div><div><span>TRADES</span><b>{state.mnq?.trade_count ?? "—"}</b></div><div><span>EVENTOS</span><b>{state.mnq?.event_count ?? "—"}</b></div><div><span>FONTE</span><b>CME + RITHMIC</b></div></div></div>
    <aside className="panel"><p className="label">DOM · ORDER BOOK</p><div className="bookHead"><span>BID SIZE</span><span>PRICE</span><span>ASK SIZE</span></div>{Array.from({ length: rows }, (_, i) => <div className="bookRow" key={i}><b className="bid">{book.bids[i]?.size ?? ""}</b><span>{fmt(book.asks[i]?.price ?? book.bids[i]?.price)}</span><b className="ask">{book.asks[i]?.size ?? ""}</b></div>)}<div className="divider"/><p className="label">DECISION ENGINE</p><strong className="wait">WAIT</strong><p className="reason">Leitura em modo pesquisa. Nenhuma ordem pode ser enviada.</p></aside></section>
    <footer>Dados reais de mercado · memória de sessão atual · persistência histórica e footprint entram na próxima camada</footer>
  </main>;
}
