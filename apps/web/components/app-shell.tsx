"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Icon } from "./icons";

const navigation = [
  ["Overview", "/", "overview"],
  ["Fleet", "/fleet", "fleet"],
  ["Workloads", "/workloads", "workloads"],
  ["Placement", "/placement", "placement"],
  ["Scenarios", "/scenarios", "scenarios"],
  ["Benchmarks", "/benchmarks", "benchmarks"],
] as const;

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  return <div className="shell">
    <aside className="sidebar">
      <Link href="/" className="brand"><span className="brandMark">H</span><span>Helios</span></Link>
      <nav>
        <p className="navLabel">Workspace</p>
        {navigation.map(([label, href, icon]) => {
          const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
          return <Link className={`navItem ${active ? "active" : ""}`} href={href} key={href}><Icon name={icon}/><span>{label}</span></Link>;
        })}
      </nav>
      <div className="sideFoot">
        <div className="healthDot"/>
        <div><strong>API healthy</strong><span>Last sync 18s ago</span></div>
      </div>
    </aside>
    <div className="workspace">
      <header className="topbar">
        <div className="search"><Icon name="search" size={17}/><span>Search fleet, workload, or run…</span><kbd>⌘ K</kbd></div>
        <div className="topActions"><button className="iconButton" aria-label="Notifications"><Icon name="bell"/></button><span className="divider"/><div className="avatar">AC</div><div className="user"><strong>Atharva</strong><span>Platform admin</span></div></div>
      </header>
      <main>{children}</main>
    </div>
  </div>;
}
