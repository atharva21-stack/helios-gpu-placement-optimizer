export const fleetRows = [
  { cluster: "h100-prod-01", region: "US Central", type: "H100 80GB", nodes: 32, capacity: 256, used: 198, health: "Healthy" },
  { cluster: "h100-prod-02", region: "US East", type: "H100 80GB", nodes: 24, capacity: 192, used: 151, health: "Healthy" },
  { cluster: "a100-research", region: "US Central", type: "A100 80GB", nodes: 18, capacity: 144, used: 82, health: "Degraded" },
  { cluster: "l40s-inference", region: "EU West", type: "L40S 48GB", nodes: 12, capacity: 96, used: 63, health: "Healthy" },
];

export const workloads = [
  { name: "Llama 70B Production", tenant: "Finance AI", shape: "16 × H100", priority: "P0", status: "Running", end: "Aug 31" },
  { name: "Vision encoder tuning", tenant: "Research", shape: "8 × A100", priority: "P2", status: "Queued", end: "Aug 04" },
  { name: "Realtime embeddings", tenant: "Search", shape: "12 × L40S", priority: "P1", status: "Running", end: "Continuous" },
  { name: "Agent eval suite", tenant: "Platform", shape: "4 × H100", priority: "P2", status: "Pending", end: "Jul 29" },
  { name: "Fraud model training", tenant: "Risk", shape: "32 × H100", priority: "P0", status: "Running", end: "Aug 12" },
];

export const runs = [
  { id: "run_8f21", strategy: "Topology aware", accepted: "24 / 26", utilization: "79.4%", fragmented: 18, runtime: "384 ms", status: "Complete" },
  { id: "run_8f20", strategy: "Best fit", accepted: "22 / 26", utilization: "76.1%", fragmented: 31, runtime: "216 ms", status: "Complete" },
  { id: "run_8f19", strategy: "CP-SAT", accepted: "25 / 26", utilization: "81.8%", fragmented: 14, runtime: "5.0 s", status: "Complete" },
];
