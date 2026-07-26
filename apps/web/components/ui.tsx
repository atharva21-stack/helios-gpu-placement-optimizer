import Link from "next/link";
import { Icon } from "./icons";

export function PageHeader({ eyebrow, title, description, action = "New placement", href = "/placement" }: { eyebrow: string; title: string; description: string; action?: string; href?: string }) {
  return <div className="pageHeader"><div><span className="eyebrow">{eyebrow}</span><h1>{title}</h1><p>{description}</p></div><Link href={href} className="primaryButton"><Icon name="plus" size={16}/>{action}</Link></div>;
}

export function Badge({ children, tone = "neutral" }: { children: React.ReactNode; tone?: "success" | "warn" | "blue" | "neutral" }) {
  return <span className={`badge ${tone}`}>{children}</span>;
}

export function Stat({ label, value, detail, trend, accent }: { label: string; value: string; detail: string; trend?: string; accent?: boolean }) {
  return <article className={`statCard ${accent ? "accent" : ""}`}><div className="statTop"><span>{label}</span>{trend && <Badge tone="success">{trend}</Badge>}</div><strong>{value}</strong><p>{detail}</p></article>;
}

export function Progress({ value }: { value: number }) {
  return <div className="progress"><span style={{ width: `${value}%` }}/></div>;
}

export function EmptyHint({ title, body }: { title: string; body: string }) {
  return <div className="emptyHint"><div className="emptyIcon"><Icon name="placement"/></div><h3>{title}</h3><p>{body}</p></div>;
}
