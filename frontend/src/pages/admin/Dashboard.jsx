import { useEffect, useState } from "react";
import { api } from "@/lib/api";

const Kpi = ({ label, value, sub, testid }) => (
  <div className="bg-white border border-zinc-200 p-5 shadow-sm" data-testid={testid}>
    <p className="text-xs uppercase tracking-widest text-zinc-400">{label}</p>
    <p className="text-3xl font-semibold font-mono mt-1">{value}</p>
    {sub && <p className="text-xs text-zinc-500 mt-1">{sub}</p>}
  </div>
);

export default function Dashboard() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    api.get("/admin/stats").then((r) => setStats(r.data)).catch(() => {});
  }, []);

  if (!stats) return <p className="text-zinc-400">Memuat statistik...</p>;

  return (
    <div data-testid="admin-dashboard">
      <h1 className="text-2xl font-semibold tracking-tight mb-6">Dashboard</h1>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <Kpi testid="kpi-tokens" label="Total Token" value={stats.tokens.total}
          sub={`${stats.tokens.unused} belum dipakai · ${stats.tokens.active} aktif`} />
        <Kpi testid="kpi-participants" label="Peserta" value={stats.participants} sub={`${stats.completed} selesai`} />
        <Kpi testid="kpi-avg" label="Rata-rata Skor TKJ" value={`${stats.avg_score_pct}%`} sub={`${stats.questions} soal di bank`} />
        <Kpi testid="kpi-violations" label="Total Pelanggaran" value={stats.violations} sub="tab-switch / fullscreen / kamera" />
      </div>
      <div className="bg-white border border-zinc-200 p-6 shadow-sm">
        <h2 className="font-medium mb-4">Status Token</h2>
        <div className="grid grid-cols-5 gap-4 text-center">
          {["unused", "active", "completed", "expired", "revoked"].map((s) => (
            <div key={s} className="border border-zinc-100 p-4">
              <p className="text-2xl font-mono font-semibold">{stats.tokens[s]}</p>
              <p className="text-xs uppercase tracking-wider text-zinc-400 mt-1">{s}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
