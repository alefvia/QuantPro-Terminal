"use client";

import { useEffect, useMemo, useState } from "react";

const RELAY = "https://quantpro-market-relay.onrender.com";
const frames = ["1m", "5m", "15m"] as const;
type Frame = (typeof frames)[number];
type Candle = { time: number; open: number; high: number; low: number; close: number; volume: number };
type Level = { level: number; price: number; size: number };
type Book = { bids: Level[]; asks: Level[] };
type State = { markets?: { symbol: string; price?: number; last_event?: { observed_at?: string } }[]; mnq?: { cvd?: number; trade_count?: number; event_count?: number } };

function fmt(value?: number) { return value == null ? "—" : value.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }

function CandleChart({ candles }: { candles: Candle[] }) {
  const model = useMemo(() => {
    if (!candles.length) return null;
    const visible = candles.slice(-72);
    const rawHigh = Math.max(...visible.map((c) => c.high));
    const rawLow = Math.min(...visible.map((c) => c.low));
    const extra = Math.max((rawHigh - rawLow) * 0.08, 1);
    const high = rawHigh + extra, low = rawLow - extra;
    const range = Math.max(high - low, 0.25);
    const width = 960, height = 430, left = 18, right = 76, top = 18, bottom = 58, volumeHeight = 72;
    const plotHeight = height - top - bottom - volumeHeight;
    const step = (width - left - right) / visible.length;
    const y = (price: number) => top + ((high - price) / range) * plotHeight;
    const volumeMax = Math.max(...visible.map((c) => c.volume), 1);
    const volumeY = top + plotHeight + 8;
    return { width, height, left, right, top, step, y, high, low, visible, volumeMax, volumeY, volumeHeight };
  }, [candles]);
  if (!model) return <div className="placeholder"><strong>AGUARDANDO HISTÓRICO REAL</strong><p>O gráfico aparece quando as velas chegam ao relay.</p></div>;
  const ticks = Array.from({ length: 6 }, (_, index) => model.high - (model.high - model.low) * index / 5);
  const timeText = (stamp: number) => new Date(stamp * 1000).toLocaleString("pt-BR", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit", timeZone: "America/Chicago" });
  return <svg className="candleChart" viewBox={"0 0 " + model.width + " " + model.height} role="img" aria-label="Gráfico de velas reais do MNQ">
    <rect x="0" y="0" width={model.width} height={model.height} fill="#070c12" />
    {ticks.map((price) => <g key={price}><line x1={model.left} x2={model.width - model.right} y1={model.y(price)} y2={model.y(price)} stroke="#1b2835" strokeWidth="1"/><text x={model.width - model.right + 10} y={model.y(price) + 4} fill="#8494a9" fontSize="11">{fmt(price)}</text></g>)}
    {model.visible.map((candle, index) => { const x = model.left + index * model.step + model.step / 2; const up = candle.close >= candle.open; const color = up ? "#35c596" : "#ef5f73"; const bodyTop = model.y(Math.max(candle.open, candle.close)); const body = Math.max(2, Math.abs(model.y(candle.open) - model.y(candle.close))); const volume = candle.volume / model.volumeMax * model.volumeHeight; return <g key={candle.time}><rect x={x - model.step * .34} y={model.volumeY + model.volumeHeight - volume} width={Math.max(2, model.step * .68)} height={volume} fill={color} opacity=".42"/><line x1={x} x2={x} y1={model.y(candle.high)} y2={model.y(candle.low)} stroke={color} strokeWidth="1.5"/><rect x={x - model.step * .34} y={bodyTop} width={Math.max(2, model.step * .68)} height={body} fill={color}/>{index % 12 === 0 && <g><line x1={x} x2={x} y1={model.top} y2={model.volumeY + model.volumeHeight} stroke="#13202c" strokeWidth="1"/><text x={x} y={model.height - 17} textAnchor="middle" fill="#718196" fontSize="10">{timeText(candle.time)}</text></g>}</g>; })}
    <line x1={model.left} x2={model.width - model.right} y1={model.volumeY} y2={model.volumeY} stroke="#293848" strokeWidth="1"/><text x={model.left} y={model.volumeY + 15} fill="#718196" fontSize="10">VOLUME</text>
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
      const [stateRes, chartRes, bookRes] = await Promise.all([fetch(RELAY + "/terminal/state", { cache: "no-store" }), fetch(RELAY + "/terminal/chart?symbol=MNQ&timeframe=" + frame, { cache: "no-store" }), fetch(RELAY + "/terminal/book?symbol=MNQ", { cache: "no-store" })]);
      if (!stateRes.ok || !chartRes.ok || !bookRes.ok) throw new Error("relay unavailable");
      const next = await stateRes.json(), chart = await chartRes.json(), depth = await bookRes.json();
      if (active) { setState(next); setCandles(chart.candles ?? []); setBook(depth.book ?? { bids: [], asks: [] }); setOnline(Boolean(next.markets?.find((m: {symbol:string}) => m.symbol === "MNQ")?.price)); }
    } catch { if (active) setOnline(false); } };
    load(); const timer = window.setInterval(load, 5000); return () => { active = false; window.clearInterval(timer); };
  }, [frame]);
  const mnq = state.markets?.find((market) => market.symbol === "MNQ");
  const updated = mnq?.last_event?.observed_at ? new Date(mnq.last_event.observed_at).toLocaleTimeString("pt-BR", { timeZone: "America/Chicago" }) : "histórico CME";
  const rows = Math.max(book.asks.length, book.bids.length, 5);
  return <main><header><div><p className="eyebrow">QUANTPRO · MARKET INTELLIGENCE WORKSTATION</p><h1>MNQ Market Structure</h1><p className="sub">Rithmic Test · análise somente · execução bloqueada</p></div><div className={online ? "badge" : "danger"}>{online ? "● DADOS RITHMIC" : "● HISTÓRICO CME"}</div></header><nav>{[["NQ", "Nasdaq E-mini"], ["MNQ", "Nasdaq Micro"], ["GC", "Gold"], ["MGC", "Micro Gold"]].map(([symbol, name]) => <button className={symbol === "MNQ" ? "active" : ""} key={symbol}><b>{symbol}</b><small>{name}</small><span>{symbol === "MNQ" ? fmt(mnq?.price) : "—"}</span></button>)}</nav><section className="status"><div><span>MARKET DATA</span><b className={online ? "ready" : "red"}>{online ? "ONLINE" : "HISTÓRICO"}</b></div><div><span>TIMEFRAME</span><b>{frame}</b></div><div><span>ÚLTIMO EVENTO</span><b>{updated}</b></div><div><span>EXECUÇÃO</span><b className="red">DISABLED</b></div></section><section className="workspace"><div className="chart panel"><div className="sectionHead"><div><p className="label">MNQ · VELAS CME REAIS + RITHMIC AO VIVO</p><h2>{fmt(mnq?.price)}</h2></div><div className="timeframes">{frames.map((item) => <button className={frame === item ? "active" : ""} onClick={() => setFrame(item)} key={item}>{item}</button>)}</div></div><CandleChart candles={candles}/><div className="metricGrid"><div><span>CVD</span><b>{state.mnq?.cvd ?? "—"}</b></div><div><span>TRADES</span><b>{state.mnq?.trade_count ?? "—"}</b></div><div><span>EVENTOS</span><b>{state.mnq?.event_count ?? "—"}</b></div><div><span>FONTE</span><b>CME + RITHMIC</b></div></div></div><aside className="panel"><p className="label">DOM · ORDER BOOK</p><div className="bookHead"><span>BID SIZE</span><span>PRICE</span><span>ASK SIZE</span></div>{Array.from({ length: rows }, (_, i) => <div className="bookRow" key={i}><b className="bid">{book.bids[i]?.size ?? ""}</b><span>{fmt(book.asks[i]?.price ?? book.bids[i]?.price)}</span><b className="ask">{book.asks[i]?.size ?? ""}</b></div>)}<div className="divider"/><p className="label">DECISION ENGINE</p><strong className="wait">WAIT</strong><p className="reason">Leitura em modo pesquisa. Nenhuma ordem pode ser enviada.</p></aside></section><footer>Dados reais de mercado · histórico CME importado · tempo real Rithmic quando conectado</footer></main>;
}
