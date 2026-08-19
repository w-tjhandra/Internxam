import { useEffect, useState } from "react";
import { api, errDetail } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { toast } from "sonner";

export default function SettingsPage() {
  const [cfg, setCfg] = useState(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.get("/admin/config").then((r) => setCfg(r.data)).catch((e) => toast.error(errDetail(e)));
  }, []);

  const save = async () => {
    setSaving(true);
    try {
      const { data } = await api.put("/admin/config", {
        tkj_duration_minutes: Number(cfg.tkj_duration_minutes),
        disc_duration_minutes: Number(cfg.disc_duration_minutes),
        tkj_question_count: Number(cfg.tkj_question_count),
        violation_threshold: Number(cfg.violation_threshold),
        require_seb: cfg.require_seb,
        seb_browser_exam_key: cfg.seb_browser_exam_key || "",
      });
      setCfg(data);
      toast.success("Konfigurasi tersimpan");
    } catch (e) { toast.error(errDetail(e)); }
    setSaving(false);
  };

  if (!cfg) return <p className="text-zinc-400">Memuat...</p>;

  const NumField = ({ label, field, hint }) => (
    <div className="space-y-1.5">
      <Label>{label}</Label>
      <Input type="number" data-testid={`config-${field}`} value={cfg[field]}
        onChange={(e) => setCfg({ ...cfg, [field]: e.target.value })} />
      {hint && <p className="text-xs text-zinc-400">{hint}</p>}
    </div>
  );

  return (
    <div data-testid="settings-page" className="max-w-2xl">
      <h1 className="text-2xl font-semibold tracking-tight mb-6">Konfigurasi Ujian</h1>
      <div className="bg-white border border-zinc-200 p-6 shadow-sm space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <NumField label="Durasi TKJ (menit)" field="tkj_duration_minutes" />
          <NumField label="Durasi DISC (menit)" field="disc_duration_minutes" />
          <NumField label="Jumlah Soal TKJ" field="tkj_question_count" hint="Diambil acak dari bank soal" />
          <NumField label="Ambang Pelanggaran" field="violation_threshold" hint="Auto-submit setelah N pelanggaran" />
        </div>
        <div className="border-t border-zinc-200 pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Wajib Safe Exam Browser (SEB)</p>
              <p className="text-sm text-zinc-500">Jika aktif, backend memvalidasi header SEB. Nonaktifkan untuk mode soft-lock (uji coba).</p>
            </div>
            <Switch data-testid="config-require-seb" checked={cfg.require_seb}
              onCheckedChange={(v) => setCfg({ ...cfg, require_seb: v })} />
          </div>
          {cfg.require_seb && (
            <div className="space-y-1.5 mt-4">
              <Label>Browser Exam Key (BEK)</Label>
              <Input data-testid="config-seb-key" value={cfg.seb_browser_exam_key || ""}
                onChange={(e) => setCfg({ ...cfg, seb_browser_exam_key: e.target.value })}
                placeholder="Salin dari SEB Config Tool" className="font-mono" />
              <p className="text-xs text-zinc-400">Kosongkan untuk hanya memeriksa keberadaan header SEB tanpa validasi hash.</p>
            </div>
          )}
        </div>
        <Button onClick={save} disabled={saving} data-testid="save-config-btn" className="bg-zinc-900 text-white hover:bg-zinc-800">
          {saving ? "Menyimpan..." : "Simpan Konfigurasi"}
        </Button>
      </div>
    </div>
  );
}
