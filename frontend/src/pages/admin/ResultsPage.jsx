import { useEffect, useState } from "react";
import { api, errDetail } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { toast } from "sonner";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
} from "recharts";

function summarizeParticipant(detail) {
  const tkjScore = Number.isFinite(detail.tkj_score) ? detail.tkj_score : null;
  const tkjTotal = Number.isFinite(detail.tkj_total) ? detail.tkj_total : null;
  const tkjPercentage = tkjScore !== null && tkjTotal > 0
    ? Math.round((tkjScore / tkjTotal) * 100)
    : null;

  const scenarioIndicators = Object.values(detail.scenario_result?.indicators || {})
    .filter((indicator) => Number.isFinite(indicator.average) && indicator.answered > 0)
    .sort((first, second) => second.average - first.average);
  const scenarioAnswered = detail.scenario_result?.answered_scenarios || 0;
  const scenarioTotal = detail.scenario_result?.total_scenarios || 0;

  const workDisc = detail.work_disc_result;
  const discSummary = (workDisc?.summary || [])
    .filter((entry) => Number.isFinite(entry.score))
    .sort((first, second) => second.score - first.score);

  const evidence = [];
  if (tkjPercentage !== null) {
    evidence.push(`TKJ ${tkjScore}/${tkjTotal} (${tkjPercentage}%)`);
  }
  if (scenarioTotal > 0) {
    evidence.push(`skenario ${scenarioAnswered}/${scenarioTotal} terjawab`);
  }
  if (workDisc?.answered_items > 0) {
    evidence.push(`DISC ${workDisc.answered_items}/${workDisc.total_items} situasi terjawab`);
  }

  return {
    tkjScore,
    tkjTotal,
    tkjPercentage,
    scenarioIndicators,
    scenarioAnswered,
    scenarioTotal,
    discSummary,
    evidence,
    allComplete:
      tkjScore !== null &&
      scenarioTotal > 0 &&
      scenarioAnswered === scenarioTotal &&
      workDisc?.status === "complete",
  };
}

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

  const discDimensions = ["D", "I", "S", "C"];
  const discResult = detail?.disc_result;
  const hasDiscChart = ["most", "least", "change"].every((key) =>
    discResult?.[key] &&
    discDimensions.every((dimension) => Number.isFinite(discResult[key][dimension])));
  const discChart = hasDiscChart
    ? discDimensions.map((d) => ({
        dim: d,
        Most: discResult.most[d],
        Least: -discResult.least[d],
        Change: discResult.change[d],
      }))
    : [];
  const workDiscResult = detail?.work_disc_result;
  const workDiscChart = workDiscResult?.scores
      ? ["D", "I", "S", "C"].map((dimension) => ({
          dimension,
          score: workDiscResult.scores[dimension] || 0,
        }))
      : [];
  const overallSummary = detail ? summarizeParticipant(detail) : null;

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
              <th className="p-3">Status</th><th className="p-3">Skor TKJ</th><th className="p-3">Respons Skenario</th><th className="p-3">Status DISC</th>
              <th className="p-3">Pelanggaran</th><th className="p-3"></th>
            </tr>
          </thead>
          <tbody data-testid="results-table-body">
            {filtered.map((r) => (
              <tr key={r.id} className="border-b border-zinc-100 hover:bg-zinc-50">
                <td className="p-3 font-medium">{r.name}{r.auto_submitted && <span className="ml-2 text-[10px] bg-red-100 text-red-700 px-1.5 py-0.5">AUTO</span>}</td>
                <td className="p-3 text-zinc-500">{r.school} · {r.class_name}</td>
                <td className="p-3 font-mono">{r.token_code}</td>
                <td className="p-3">{r.stage === "done" ? "Selesai" : r.stage === "scenario" ? "Asesmen skenario" : r.stage === "work_disc" ? "Situasi kerja DISC" : r.stage === "disc" ? "DISC lama" : "Sedang TKJ"}</td>
                <td className="p-3 font-mono">{r.tkj_score !== null && r.tkj_score !== undefined ? `${r.tkj_score}/${r.tkj_total}` : "—"}</td>
                <td className="p-3 font-mono">{r.scenario_total ? `${r.scenario_answered}/${r.scenario_total}` : "—"}</td>
                <td className="p-3">
                  {r.work_disc_status === "complete" ? "Selesai" :
                    r.work_disc_status === "partial" ? `Parsial ${r.work_disc_answered}/${r.work_disc_total}` :
                      r.work_disc_status === "in_progress" ? "Sedang dikerjakan" :
                        r.work_disc_status === "skipped" ? "Nonaktif" : "—"}
                </td>
                <td className="p-3"><span className={r.violation_count > 0 ? "text-red-600 font-medium" : "text-zinc-400"}>{r.violation_count}</span></td>
                <td className="p-3"><Button size="sm" variant="ghost" data-testid={`detail-${r.token_code}`} onClick={() => openDetail(r.id)}>Detail</Button></td>
              </tr>
            ))}
            {filtered.length === 0 && <tr><td colSpan={9} className="p-8 text-center text-zinc-400">Belum ada hasil</td></tr>}
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
                  <p className="text-xs uppercase tracking-wider text-zinc-400">Respons Skenario</p>
                  <p className="text-2xl font-mono font-semibold">
                    {detail.scenario_total ? `${detail.scenario_answered}/${detail.scenario_total}` : "—"}
                  </p>
                </div>
                <div className="border border-zinc-200 p-4 text-center">
                  <p className="text-xs uppercase tracking-wider text-zinc-400">Pelanggaran</p>
                  <p className="text-2xl font-mono font-semibold text-red-600">{detail.violation_count}</p>
                </div>
              </div>
              <section className="mb-6 border border-indigo-100 bg-indigo-50/50 p-4" data-testid="participant-overall-summary">
                <h3 className="font-semibold text-slate-900">Ringkasan Keseluruhan</h3>
                {overallSummary.evidence.length > 0 ? (
                  <>
                    <p className="mt-2 text-sm leading-relaxed text-slate-700">
                      Berdasarkan data yang tersedia{overallSummary.allComplete ? " dari seluruh babak" : ""}:
                      {" "}{overallSummary.evidence.join("; ")}.
                    </p>
                    <div className="mt-4 grid grid-cols-1 gap-3 text-sm md:grid-cols-3">
                      <div className="bg-white/80 p-3">
                        <p className="font-medium">Kemampuan teknis</p>
                        <p className="mt-1 text-slate-600">
                          {overallSummary.tkjPercentage === null
                            ? "Hasil TKJ belum tersedia."
                            : `Skor ${overallSummary.tkjScore}/${overallSummary.tkjTotal} (${overallSummary.tkjPercentage}%) menggambarkan capaian pada soal teknis yang diujikan.`}
                        </p>
                      </div>
                      <div className="bg-white/80 p-3">
                        <p className="font-medium">Respons situasi kerja</p>
                        <p className="mt-1 text-slate-600">
                          {overallSummary.scenarioIndicators.length > 0
                            ? `Nilai rubrik relatif lebih tinggi pada ${overallSummary.scenarioIndicators[0].label} (${overallSummary.scenarioIndicators[0].average}/3). ${overallSummary.scenarioIndicators.length > 1
                              ? `Perlu pendalaman lebih lanjut pada ${overallSummary.scenarioIndicators[overallSummary.scenarioIndicators.length - 1].label} (${overallSummary.scenarioIndicators[overallSummary.scenarioIndicators.length - 1].average}/3).`
                              : "Data indikator lain belum cukup untuk dibandingkan."}`
                            : "Belum ada respons skenario yang cukup untuk diringkas."}
                          {overallSummary.scenarioTotal > overallSummary.scenarioAnswered
                            ? ` Baru ${overallSummary.scenarioAnswered} dari ${overallSummary.scenarioTotal} skenario terjawab.`
                            : ""}
                        </p>
                      </div>
                      <div className="bg-white/80 p-3">
                        <p className="font-medium">Kecenderungan perilaku kerja</p>
                        <p className="mt-1 text-slate-600">
                          {overallSummary.discSummary.length > 0
                            ? `Pilihan DISC paling banyak menunjukkan kecenderungan ${overallSummary.discSummary[0].label}${overallSummary.discSummary[1] ? `, diikuti ${overallSummary.discSummary[1].label}` : ""}. Gunakan ini sebagai bahan diskusi, bukan label tetap.`
                            : "Hasil DISC situasi kerja belum tersedia atau belum memiliki respons yang dapat diringkas."}
                          {workDiscResult?.status === "partial" && " Hasil parsial; baca dengan kehati-hatian."}
                        </p>
                      </div>
                    </div>
                  </>
                ) : (
                  <p className="mt-2 text-sm text-slate-600">
                    Belum ada hasil yang cukup untuk membuat ringkasan keseluruhan.
                  </p>
                )}
                <p className="mt-3 border-t border-indigo-100 pt-3 text-xs text-slate-500">
                  Ringkasan menggabungkan bukti dari tiap asesmen, bukan skor kecocokan atau keputusan penempatan otomatis. Pertimbangkan bersama minat peserta, percakapan, dan hasil praktik.
                </p>
              </section>
              {detail.scenario_result?.version && (
                <div className="mb-6" data-testid="scenario-result">
                  <h3 className="font-medium mb-1">Asesmen situasi PKL · {detail.scenario_result.version}</h3>
                  <p className="text-sm text-amber-800 bg-amber-50 border border-amber-200 p-3 mb-4">
                    {detail.scenario_result.disclaimer} Gunakan sebagai bahan diskusi, bukan diagnosis atau keputusan seleksi tunggal.
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-5">
                    {Object.entries(detail.scenario_result.indicators || {}).map(([key, indicator]) => (
                      <div key={key} className="border border-zinc-200 p-4">
                        <p className="font-medium">{indicator.label}</p>
                        <p className="text-xs text-zinc-500 mt-1">{indicator.description}</p>
                        <p className="text-sm mt-3">
                          Respons terjawab: {indicator.answered}/{indicator.total}
                          {" · "}Rata-rata rubrik: {indicator.average === null ? "Belum cukup respons" : `${indicator.average}/3`}
                        </p>
                      </div>
                    ))}
                  </div>
                  <h4 className="font-medium mb-2">Jawaban dan catatan rubrik</h4>
                  <div className="space-y-3">
                    {(detail.scenario_result.responses || []).map((response) => (
                      <div key={response.scenario_id} className="border-l-2 border-indigo-300 pl-4 py-1">
                        <p className="text-xs uppercase tracking-wider text-zinc-400">{response.indicator_label}</p>
                        <p className="text-sm mt-1">{response.selected_option}</p>
                        <p className="text-xs text-zinc-500 mt-1">
                          Rubrik {response.score}/3 · {response.rationale}
                        </p>
                      </div>
                    ))}
                    {!detail.scenario_result.responses?.length && (
                      <p className="text-sm text-zinc-400">Belum ada jawaban skenario yang tersimpan.</p>
                    )}
                  </div>
                </div>
              )}
              {detail.work_disc_status !== "not_started" && (
                <section className="mb-6 border border-zinc-200 p-4" data-testid="work-disc-result">
                  <div className="flex flex-wrap items-start justify-between gap-2">
                    <div>
                      <h3 className="font-medium">Ringkasan DISC · Situasi Kerja</h3>
                      {workDiscResult?.version && (
                        <p className="text-xs text-zinc-400 mt-1">{workDiscResult.version}</p>
                      )}
                    </div>
                    <span className="text-xs text-zinc-500">
                      {detail.work_disc_status === "complete" ? "Selesai" :
                        detail.work_disc_status === "partial" ? "Dikirim otomatis · hasil parsial" :
                          detail.work_disc_status === "in_progress" ? "Sedang dikerjakan" : "Babak dinonaktifkan"}
                    </span>
                  </div>
                  {workDiscResult ? (
                    <>
                      <p className="mt-3 text-sm text-amber-800 bg-amber-50 border border-amber-200 p-3">
                        {workDiscResult.disclaimer}
                      </p>
                      <p className="mt-3 text-xs text-zinc-500">
                        Terjawab {workDiscResult.answered_items}/{workDiscResult.total_items}
                        {workDiscResult.auto_submitted && " · Jawaban dikirim otomatis saat waktu habis"}
                      </p>
                      {workDiscChart.length > 0 && workDiscResult.answered_items > 0 ? (
                        <div className="mt-4 grid grid-cols-1 items-center gap-4 md:grid-cols-2">
                          <div className="h-64" data-testid="work-disc-radar-chart">
                            <ResponsiveContainer width="100%" height="100%">
                              <RadarChart data={workDiscChart}>
                                <PolarGrid />
                                <PolarAngleAxis dataKey="dimension" />
                                <PolarRadiusAxis domain={[0, 100]} tickCount={5} />
                                <Radar dataKey="score" name="Proporsi jawaban" stroke="#4f46e5" fill="#6366f1" fillOpacity={0.35} />
                                <Tooltip formatter={(value) => [`${value}%`, "Proporsi"]} />
                              </RadarChart>
                            </ResponsiveContainer>
                          </div>
                          <div className="space-y-3">
                            {(workDiscResult.summary || []).map((entry) => (
                              <div key={entry.dimension} className="border-l-2 border-indigo-300 pl-3">
                                <div className="flex items-baseline justify-between gap-2">
                                  <p className="font-medium">{entry.dimension} · {entry.label}</p>
                                  <p className="font-mono text-sm">{entry.score}%</p>
                                </div>
                                <p className="mt-1 text-xs text-zinc-500">{entry.description}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      ) : (
                        <p className="mt-4 text-sm text-zinc-400">
                          Belum ada jawaban yang cukup untuk menampilkan ringkasan diagram.
                        </p>
                      )}
                    </>
                  ) : (
                    <p className="mt-3 text-sm text-zinc-500">
                      {detail.work_disc_status === "in_progress"
                        ? "Peserta belum menyelesaikan babak ini; hasil belum tersedia."
                        : "Babak DISC dinonaktifkan untuk alur ujian ini."}
                    </p>
                  )}
                </section>
              )}
              {detail.disc_result?.dominant && (
                <div className="mb-4">
                  <h3 className="font-medium mb-1">Hasil DISC lama (historis; tidak digunakan pada asesmen baru)</h3>
                  <p className="text-sm text-zinc-500 mb-3">{detail.disc_result.interpretation}</p>
                  {hasDiscChart ? (
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
                  ) : (
                    <p className="text-sm text-zinc-400">Grafik tidak tersedia karena data hasil DISC historis tidak lengkap.</p>
                  )}
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
