import { Badge, PageHeader, Progress, Stat } from "@/components/ui";
import { fleetRows } from "@/lib/demo-data";

export default function FleetPage() {
  return <div className="page"><PageHeader eyebrow="Infrastructure" title="GPU fleet" description="Inspect capacity, health, and fragmentation across every scheduling domain." action="Add capacity" href="/scenarios"/>
    <section className="statsGrid"><Stat label="Total GPUs" value="688" detail="632 currently healthy"/><Stat label="Active nodes" value="86" detail="Across 4 clusters"/><Stat label="Fully free nodes" value="12" detail="96 contiguous GPUs"/><Stat label="Maintenance" value="3" detail="Nodes in next 7 days"/></section>
    <article className="panel"><div className="panelHead"><div><span className="eyebrow">Inventory</span><h2>Clusters</h2></div><div className="filters"><button className="filter active">All clusters</button><button className="filter">Healthy</button><button className="filter">Attention</button></div></div>
      <div className="tableWrap"><table><thead><tr><th>Cluster</th><th>Region</th><th>Accelerator</th><th>Nodes</th><th>Utilization</th><th>Health</th></tr></thead><tbody>{fleetRows.map(r => { const pct = Math.round(r.used/r.capacity*100); return <tr key={r.cluster}><td><strong>{r.cluster}</strong><small>{r.capacity} GPUs total</small></td><td>{r.region}</td><td>{r.type}</td><td>{r.nodes}</td><td><div className="tableProgress"><Progress value={pct}/><span>{pct}%</span></div></td><td><Badge tone={r.health === "Healthy" ? "success" : "warn"}>{r.health}</Badge></td></tr>})}</tbody></table></div>
    </article>
    <section className="topology"><article className="panel"><div className="panelHead"><div><span className="eyebrow">Scheduling domains</span><h2>Topology map</h2></div><Badge tone="blue">h100-prod-01</Badge></div><div className="rackMap">{["Rack A · fd-a","Rack B · fd-b","Rack C · fd-c"].map((rack,i)=><div className="rack" key={rack}><strong>{rack}</strong><span>400G InfiniBand</span><div className="nodeGrid">{Array.from({length:8},(_,n)=><i key={n} className={(n+i)%5===0?"partial":(n+i)%7===0?"offline":""} title={`node-${n+1}`}/>)}</div></div>)}</div><div className="mapLegend"><span><i/>Available</span><span><i className="partial"/>Partial</span><span><i className="offline"/>Unavailable</span></div></article></section>
  </div>;
}
