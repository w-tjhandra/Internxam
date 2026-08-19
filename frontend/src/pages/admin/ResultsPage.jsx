import { useEffect, useState } from "react";
import { api, errDetail } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { toast } from "sonner";
import { BarChart, Bar, XAxis, YAxis, ReferenceLine, ResponsiveContainer, Tooltip } from "recharts";

export default function ResultsPage() {
  const [results, setResults] = useState([]);
  const [search, setSearch] = useState("");
  const [detail, setDetail] = useState(null);

  useEffect(() => {
    api.get("/admin/results").then((r) => setResults(r.data)).catch((e) => toast.error(errDetail(e)));
  }, []);

  const openDetail = async (id) => {
    const { data } = await api.get(`/admin/results/${id}`);
    setDetail(data);
  };

  const download = async (fmt) => {
    const res = await api.get("/admin/results/export", { params: { format: fmt }, responseType: "blob" });
    const url = URL.createObjectURL(res.data);
    const a = document.createElement("a");
    a.href = url;
    a.download = `hasil_ujian.${fmt}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const filtered = results.filter((r) =>
    [r.name, r.school, r.class_name, r.token_code].join(" ").toLowerCase().includes(search.toLowerCase()));

  const discChart = detail?.disc_result
    ? ["D", "I", "S", "C"].map((d) => ({
        dim: d,
        Most: detail.disc_result.most[d],
        Least: -detail.disc_result.least[d],
        Change: detail.disc_result.change[d],
      }))
    : [];

  return (
    <div data-testid="results-page">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-semibold tracking-tight">Hasil & Analitik</h1>
        <div className="flex gap-2">
          <Button variant="outline" data-testid="export-results-csv" onClick={() => download("csv")}>Export CSV</Button>
          <Button variant="outline" data-testid="export-results-xlsx" onClick={() => download("xlsx")}>Export Excel</Button>
        </div>
      </div>
      <Input placeholder="Cari nama / sekolah / token..." value={search} onChange={(e) => setSearch(e.target.value)}
        className="mb-4 max-w-sm" data-testid="results-search" />
      <div className="bg-white border border-zinc-200 shadow-sm overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-zinc-200 text-left text-xs uppercase tracking-wider text-zinc-400">
              <th className="p-3">Nama</th><th className="p-3">Sekolah / Kelas</th><th className="p-3">Token</th>
              <th className="p-3">Status</th><th className="p-3">Skor TKJ</th><th className="p-3">DISC</th>
              <th className="p-3">Pelanggaran</th><th className="p-3"></th>
            </tr>
          </thead>
          <tbody data-testid="results-table-body">
            {filtered.map((r) => (
              <tr key={r.id} className="border-b border-zinc-100 hover:bg-zinc-50">
                <td className="p-3 font-medium">{r.name}{r.auto_submitted && <span className="ml-2 text-[10px] bg-red-100 text-red-700 px-1.5 py-0.5">AUTO</span>}</td>
                <td className="p-3 text-zinc-500">{r.school} · {r.class_name}</td>
                <td className="p-3 font-mono">{r.token_code}</td>
                <td className="p-3">{r.stage === "done" ? "Selesai" : r.stage === "disc" ? "Sedang DISC" : "Sedang TKJ"}</td>
                <td className="p-3 font-mono">{r.tkj_score !== null && r.tkj_score !== undefined ? `${r.tkj_score}/${r.tkj_total}` : "—"}</td>
                <td className="p-3 font-mono font-semibold">{r.disc_dominant || "—"}</td>
                <td className="p-3"><span className={r.violation_count > 0 ? "text-red-600 font-medium" : "text-zinc-400"}>{r.violation_count}</span></td>
                <td className="p-3"><Button size="sm" variant="ghost" data-testid={`detail-${r.token_code}`} onClick={() => openDetail(r.id)}>Detail</Button></td>
              </tr>
            ))}
            {filtered.length === 0 && <tr><td colSpan={8} className="p-8 text-center text-zinc-400">Belum ada hasil</td></tr>}
          </tbody>
        </table>
      </div>

      <Dialog open={!!detail} onOpenChange={(v) => !v && setDetail(null)}>
        <DialogContent className="max-w-3xl max-h-[85vh] overflow-y-auto" data-testid="result-detail-dialog">
          {detail && (
            <>
              <DialogHeader>
                <DialogTitle>{detail.name} — {detail.school} ({detail.class_name})</DialogTitle>
              </DialogHeader>
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="border border-zinc-200 p-4 text-center">
                  <p className="text-xs uppercase tracking-wider text-zinc-400">Skor TKJ</p>
                  <p className="text-2xl font-mono font-semibold">{detail.tkj_score ?? "—"}/{detail.tkj_total ?? "—"}</p>
                </div>
                <div className="border border-zinc-200 p-4 text-center">
                  <p className="text-xs uppercase tracking-wider text-zinc-400">Profil Dominan</p>
                  <p className="text-2xl font-mono font-semibold">{detail.disc_dominant || "—"}</p>
                </div>
                <div className="border border-zinc-200 p-4 text-center">
                  <p className="text-xs uppercase tracking-wider text-zinc-400">Pelanggaran</p>
                  <p className="text-2xl font-mono font-semibold text-red-600">{detail.violation_count}</p>
                </div>
              </div>
              {detail.disc_result && (
                <div className="mb-4">
                  <h3 className="font-medium mb-1">Grafik DISC (Most / Least / Change)</h3>
                  <p className="text-sm text-zinc-500 mb-3">{detail.disc_result.interpretation}</p>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={discChart}>
                        <XAxis dataKey="dim" />
                        <YAxis />
                        <Tooltip />
                        <ReferenceLine y={0} stroke="#e4e4e7" />
                        <Bar dataKey="Most" fill="#0055FF" />
                        <Bar dataKey="Least" fill="#EF4444" />
                        <Bar dataKey="Change" fill="#18181B" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}
              <div>
                <h3 className="font-medium mb-2">Log Pelanggaran ({detail.violations.length})</h3>
                {detail.violations.length === 0 ? (
                  <p className="text-sm text-zinc-400">Tidak ada pelanggaran. 👏</p>
                ) : (
                  <table className="w-full text-sm border border-zinc-200">
                    <thead>
                      <tr className="border-b border-zinc-200 text-left text-xs uppercase tracking-wider text-zinc-400">
                        <th className="p-2">Waktu</th><th className="p-2">Jenis</th><th className="p-2">Tahap</th><th className="p-2">Detail</th>
                      </tr>
                    </thead>
                    <tbody>
                      {detail.violations.map((v) => (
                        <tr key={v.id} className="border-b border-zinc-100">
                          <td className="p-2 font-mono text-xs">{v.timestamp?.slice(0, 19).replace("T", " ")}</td>
                          <td className="p-2"><span className="bg-red-100 text-red-700 px-1.5 py-0.5 text-xs">{v.violation_type}</span></td>
                          <td className="p-2 uppercase text-xs">{v.stage}</td>
                          <td className="p-2 text-zinc-500">{v.detail}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
