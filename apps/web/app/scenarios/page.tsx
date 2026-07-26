import { Badge, PageHeader } from "@/components/ui";

const scenarios = [
  ["Rack B maintenance", "Maintenance", "h100-prod-01", "18 workloads", "Ready"],
  ["Q4 demand surge", "Demand +35%", "All clusters", "47 workloads", "Draft"],
  ["East region outage", "Node failure", "US East", "26 workloads", "Ready"],
  ["Add 16 H100 nodes", "Fleet expansion", "US Central", "31 workloads", "Complete"],
];
export default function ScenariosPage() {
  return <div className="page"><PageHeader eyebrow="What-if planning" title="Scenarios" description="Replay demand and infrastructure changes before they affect production." action="New scenario"/>
    <section className="scenarioGrid">{scenarios.map((s,i)=><article className="scenarioCard" key={s[0]}><div className={`scenarioIcon s${i}`}>{String(i+1).padStart(2,"0")}</div><Badge tone={s[4]==="Complete"?"success":s[4]==="Ready"?"blue":"neutral"}>{s[4]}</Badge><h2>{s[0]}</h2><p>{s[1]} · {s[2]}</p><div><span>Replay set</span><strong>{s[3]}</strong></div><button className="secondaryButton">{s[4]==="Complete"?"View report":"Open scenario"}</button></article>)}</section>
  </div>;
}
