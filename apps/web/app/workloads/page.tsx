import { Badge, PageHeader, Stat } from "@/components/ui";
import { workloads } from "@/lib/demo-data";

export default function WorkloadsPage() {
  return <div className="page"><PageHeader eyebrow="Demand" title="Workloads" description="Manage placement requirements, constraints, priority, and reservation windows." action="New workload"/>
    <section className="statsGrid"><Stat label="Active" value="31" detail="426 GPUs allocated"/><Stat label="Queued" value="7" detail="72 GPUs requested"/><Stat label="Starting soon" value="4" detail="Within the next 24h"/><Stat label="Placement risk" value="3" detail="Strict topology workloads"/></section>
    <article className="panel"><div className="panelHead"><div><span className="eyebrow">Workload queue</span><h2>All workloads</h2></div><div className="filters"><button className="filter active">All</button><button className="filter">Running</button><button className="filter">Queued</button></div></div><div className="tableWrap"><table><thead><tr><th>Workload</th><th>GPU shape</th><th>Priority</th><th>End date</th><th>Status</th></tr></thead><tbody>{workloads.map(w=><tr key={w.name}><td><strong>{w.name}</strong><small>{w.tenant}</small></td><td>{w.shape}</td><td><Badge tone={w.priority==="P0"?"warn":"neutral"}>{w.priority}</Badge></td><td>{w.end}</td><td><Badge tone={w.status==="Running"?"success":"blue"}>{w.status}</Badge></td></tr>)}</tbody></table></div></article>
  </div>;
}
