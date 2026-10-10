import { useEffect, useState } from "react";
import { api, errDetail } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner";

const badge = {
  unused: "bg-zinc-100 text-zinc-600",
  active: "bg-blue-100 text-blue-700",
  completed: "bg-emerald-100 text-emerald-700",
  expired: "bg-amber-100 text-amber-700",
  revoked: "bg-red-100 text-red-700",
};

export default function TokensPage() {
  const [tokens, setTokens] = useState([]);
  const [filter, setFilter] = useState("all");
  const [count, setCount] = useState(10);
  const [type, setType] = useState("single");
  const [maxUses, setMaxUses] = useState(1);
  const [loading, setLoading] = useState(false);

  const load = () => {
    api.get("/admin/tokens", { params: filter !== "all" ? { status: filter } : {} })
      .then((r) => setTokens(r.data)).catch((e) => toast.error(errDetail(e)));
  };
  useEffect(load, [filter]); // eslint-disable-line

  const generate = async () => {
    setLoading(true);
    try {
      const { data } = await api.post("/admin/tokens/generate", { count: Number(count), type, max_uses: Number(maxUses) });
      toast.success(`${data.tokens.length} token berhasil dibuat`);
      load();
    } catch (e) { toast.error(errDetail(e)); }
    setLoading(false);
  };

  const revoke = async (id) => {
    try {
      await api.post(`/admin/tokens/${id}/revoke`);
      toast.success("Token direvoke");
      load();
    } catch (e) { toast.error(errDetail(e)); }
  };

  const download = async (fmt) => {
    const res = await api.get("/admin/tokens/export", { params: { format: fmt }, responseType: "blob" });
    const url = URL.createObjectURL(res.data);
    const a = document.createElement("a");
    a.href = url;
    a.download = `tokens.${fmt}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div data-testid="tokens-page">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-semibold tracking-tight">Manajemen Token</h1>
        <div className="flex items-center gap-2">
          <Select value={type} onValueChange={setType}>
            <SelectTrigger className="w-28"><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="single">Single</SelectItem>
              <SelectItem value="group">Group</SelectItem>
            </SelectContent>
          </Select>
          {type === "group" && (
            <Input type="number" min={2} max={100} value={maxUses} onChange={(e) => setMaxUses(e.target.value)}
              className="w-16" title="Kapasitas (Max Uses)" />
          )}
          <Input type="number" min={1} max={500} value={count} onChange={(e) => setCount(e.target.value)}
            className="w-20" data-testid="token-count-input" title="Jumlah Token Dibuat" />
          <Button onClick={generate} disabled={loading} data-testid="generate-tokens-btn" className="bg-zinc-900 text-white hover:bg-zinc-800">
            {loading ? "Membuat..." : "Generate Token"}
          </Button>
          <Button variant="outline" data-testid="export-tokens-csv" onClick={() => download("csv")}>CSV</Button>
          <Button variant="outline" data-testid="export-tokens-xlsx" onClick={() => download("xlsx")}>Excel</Button>
        </div>
      </div>
      <div className="mb-4 w-48">
        <Select value={filter} onValueChange={setFilter}>
          <SelectTrigger data-testid="token-filter"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Semua status</SelectItem>
            {Object.keys(badge).map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}
          </SelectContent>
        </Select>
      </div>
      <div className="bg-white border border-zinc-200 shadow-sm overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-zinc-200 text-left text-xs uppercase tracking-wider text-zinc-400">
              <th className="p-3">Token</th><th className="p-3">Status</th><th className="p-3">Tipe</th><th className="p-3">Peserta</th><th className="p-3">Dibuat</th><th className="p-3">Aksi</th>
            </tr>
          </thead>
          <tbody data-testid="tokens-table-body">
            {tokens.map((t) => (
              <tr key={t.id} className="border-b border-zinc-100 hover:bg-zinc-50">
                <td className="p-3 font-mono font-medium tracking-widest">{t.code}</td>
                <td className="p-3"><span className={`px-2 py-0.5 text-xs font-medium ${badge[t.status]}`}>{t.status}</span></td>
                <td className="p-3 text-zinc-600">{t.type === "group" ? `Grup (${t.usage_count}/${t.max_uses})` : "Single"}</td>
                <td className="p-3 text-zinc-600">{t.type === "group" ? "Multi-user" : t.participant_name || "—"}</td>
                <td className="p-3 text-zinc-400">{t.created_at?.slice(0, 16).replace("T", " ")}</td>
                <td className="p-3">
                  {["unused", "active"].includes(t.status) && (
                    <Button size="sm" variant="ghost" className="text-red-600 hover:text-red-700 h-7"
                      data-testid={`revoke-${t.code}`} onClick={() => revoke(t.id)}>Revoke</Button>
                  )}
                </td>
              </tr>
            ))}
            {tokens.length === 0 && <tr><td colSpan={5} className="p-8 text-center text-zinc-400">Belum ada token</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}
