import { Badge, PageHeader } from "@/components/ui";

const strategies = [
  ["CP-SAT", "96.2%", "81.8%", "14", "5.0 s", 96],
  ["Topology aware", "92.3%", "79.4%", "18", "384 ms", 89],
  ["Best fit", "84.6%", "76.1%", "31", "216 ms", 74],
  ["First fit", "80.8%", "73.5%", "43", "118 ms", 65],
] as const;
export default function BenchmarksPage() {
  return <div className="page"><PageHeader eyebrow="Strategy lab" title="Benchmarks" description="Compare acceptance, capacity quality, and latency on repeatable workload suites." action="Run benchmark"/>
    <article className="panel benchmarkChart"><div className="panelHead"><div><span className="eyebrow">Enterprise mixed · 26 workloads</span><h2>Overall placement quality</h2></div><Badge tone="success">Last run · Jul 26</Badge></div>{strategies.map(s=><div className="barRow" key={s[0]}><strong>{s[0]}</strong><div><i style={{width:`${s[5]}%`}}/><span>{s[5]}</span></div></div>)}</article>
    <article className="panel"><div className="panelHead"><div><span className="eyebrow">Results</span><h2>Strategy comparison</h2></div></div><div className="tableWrap"><table><thead><tr><th>Strategy</th><th>Acceptance</th><th>Utilization</th><th>Fragmented GPUs</th><th>Runtime</th><th>Quality</th></tr></thead><tbody>{strategies.map((s,i)=><tr key={s[0]}><td><strong>{s[0]}</strong>{i===1&&<small>Interactive default</small>}</td><td>{s[1]}</td><td>{s[2]}</td><td>{s[3]}</td><td>{s[4]}</td><td><Badge tone={i<2?"success":"neutral"}>{s[5]} / 100</Badge></td></tr>)}</tbody></table></div></article>
  </div>;
}
