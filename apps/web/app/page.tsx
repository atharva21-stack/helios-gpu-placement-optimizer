import Link from "next/link";
import { Icon } from "@/components/icons";
import { Badge, PageHeader, Progress, Stat } from "@/components/ui";
import { fleetRows, runs, workloads } from "@/lib/demo-data";

export default function Overview() {
  return <div className="page">
    <PageHeader eyebrow="Fleet control" title="Good morning, Atharva" description="Here’s how your GPU fleet is placed across regions and workloads." />
    <section className="statsGrid">
      <Stat label="Fleet utilization" value="78.2%" detail="494 of 632 healthy GPUs" trend="+3.1%" accent />
      <Stat label="Available GPUs" value="138" detail="Across 4 active clusters" />
      <Stat label="Fragmented GPUs" value="18" detail="2.8% of healthy capacity" trend="−6" />
      <Stat label="Queued workloads" value="7" detail="3 have strict topology needs" />
    </section>
    <section className="overviewGrid">
      <article className="panel utilizationPanel">
        <div className="panelHead"><div><span className="eyebrow">Capacity trend</span><h2>GPU utilization</h2></div><select defaultValue="7"><option value="7">Last 7 days</option><option value="30">Last 30 days</option></select></div>
        <div className="chartLegend"><span><i className="legendFill"/>Allocated</span><span><i className="legendLine"/>Effective capacity</span></div>
        <div className="chart">
          <div className="chartGrid"><span>100%</span><span>75%</span><span>50%</span><span>25%</span></div>
          <svg viewBox="0 0 720 230" preserveAspectRatio="none" aria-label="GPU utilization over seven days">
            <defs><linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#7259e8" stopOpacity=".35"/><stop offset="1" stopColor="#7259e8" stopOpacity=".02"/></linearGradient></defs>
            <path className="area" d="M0 168 C80 145 94 150 155 121 S240 104 305 119 S391 74 455 84 S540 56 610 66 S680 42 720 48 L720 230 L0 230Z"/>
            <path className="chartLine" d="M0 168 C80 145 94 150 155 121 S240 104 305 119 S391 74 455 84 S540 56 610 66 S680 42 720 48"/>
            <path className="capacityLine" d="M0 72 C130 69 190 77 300 64 S510 74 720 56"/>
          </svg>
          <div className="axis"><span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span><span>Sat</span><span>Sun</span></div>
        </div>
      </article>
      <article className="panel capacityPanel">
        <div className="panelHead"><div><span className="eyebrow">Fleet health</span><h2>Capacity by class</h2></div><Link href="/fleet">View fleet <Icon name="arrow" size={14}/></Link></div>
        {[["H100 80GB", 83, "349 / 448"], ["A100 80GB", 57, "82 / 144"], ["L40S 48GB", 66, "63 / 96"]].map(([name, pct, value]) => <div className="capacityRow" key={name}><div><strong>{name}</strong><span>{value} GPUs allocated</span></div><b>{pct}%</b><Progress value={Number(pct)}/></div>)}
        <div className="capacityFoot"><span className="pulse"/><span>608 of 632 GPUs healthy</span><Badge tone="success">96.2%</Badge></div>
      </article>
    </section>
    <section className="dataGrid">
      <article className="panel">
        <div className="panelHead"><div><span className="eyebrow">Live demand</span><h2>Priority workloads</h2></div><Link href="/workloads">View all <Icon name="arrow" size={14}/></Link></div>
        <div className="tableWrap"><table><thead><tr><th>Workload</th><th>Shape</th><th>Priority</th><th>Status</th></tr></thead><tbody>{workloads.slice(0,4).map(w => <tr key={w.name}><td><strong>{w.name}</strong><small>{w.tenant}</small></td><td>{w.shape}</td><td><Badge tone={w.priority === "P0" ? "warn" : "neutral"}>{w.priority}</Badge></td><td><Badge tone={w.status === "Running" ? "success" : "blue"}>{w.status}</Badge></td></tr>)}</tbody></table></div>
      </article>
      <article className="panel runPanel">
        <div className="panelHead"><div><span className="eyebrow">Latest optimization</span><h2>Placement run</h2></div><Badge tone="success">Complete</Badge></div>
        <div className="runScore"><div className="ring"><strong>92</strong><span>score</span></div><div><strong>{runs[0].id}</strong><span>Topology-aware heuristic</span><p>24 of 26 workloads placed</p></div></div>
        <div className="runMetrics"><span><strong>79.4%</strong>Utilization</span><span><strong>18</strong>Fragmented</span><span><strong>384ms</strong>Runtime</span></div>
        <Link className="secondaryButton" href="/placement">Inspect placement <Icon name="arrow" size={15}/></Link>
      </article>
    </section>
  </div>;
}
