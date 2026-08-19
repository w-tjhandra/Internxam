import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { API, errDetail } from "@/lib/api";
import { getStreams, stopStreams } from "@/lib/mediaStore";
import { CameraPreview } from "@/components/exam/CameraPreview";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { CheckCircle, Warning } from "@phosphor-icons/react";

const fmt = (s) => `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;

export default function ExamRoom() {
  const nav = useNavigate();
  const [session] = useState(() => JSON.parse(localStorage.getItem("exam_session") || "null"));
  const [state, setState] = useState(null);
  const [stage, setStage] = useState(null);
  const [idx, setIdx] = useState(0);
  const [answers, setAnswers] = useState({});
  const [discIdx, setDiscIdx] = useState(0);
  const [discAnswers, setDiscAnswers] = useState({});
  const [remaining, setRemaining] = useState(0);
  const [saveStatus, setSaveStatus] = useState("");
  const [paused, setPaused] = useState(null);
  const [warning, setWarning] = useState(null);
  const [violations, setViolations] = useState(0);
  const [threshold, setThreshold] = useState(3);
  const startedRef = useRef(false);
  const streams = getStreams();

  const creds = session ? { participant_id: session.participant_id, token: session.token } : null;

  const finish = useCallback(() => {
    setStage("done");
    stopStreams();
    if (document.fullscreenElement) document.exitFullscreen().catch(() => {});
    localStorage.removeItem("exam_session");
    localStorage.removeItem("pending_answers");
  }, []);

  const loadSession = useCallback(async () => {
    try {
      const { data } = await axios.post(`${API}/exam/session`, creds);
      setState(data);
      setStage(data.stage);
      setRemaining(data.remaining_seconds || 0);
      setViolations(data.violation_count || 0);
      setThreshold(data.violation_threshold || 3);
      if (data.stage === "tkj") {
        setAnswers(data.answers || {});
        const qs = data.questions || [];
        const firstUnanswered = qs.findIndex((q) => !(q.id in (data.answers || {})));
        setIdx(firstUnanswered >= 0 ? firstUnanswered : 0);
      }
      if (data.stage === "disc") {
        setDiscAnswers(data.disc_answers || {});
        const answered = Object.keys(data.disc_answers || {}).length;
        setDiscIdx(Math.min(answered, (data.disc_items || []).length - 1));
      }
      if (data.stage === "done") finish();
    } catch (e) {
      setPaused({ type: "error", msg: errDetail(e) });
    }
  }, [finish]); // eslint-disable-line

  useEffect(() => {
    if (!session) { nav("/"); return; }
    loadSession();
  }, []); // eslint-disable-line

  // countdown
  useEffect(() => {
    if (stage !== "tkj" && stage !== "disc") return;
    const t = setInterval(() => {
      setRemaining((r) => {
        if (r <= 1) { loadSession(); return 0; }
        return r - 1;
      });
    }, 1000);
    return () => clearInterval(t);
  }, [stage, loadSession]);

  const reportViolation = useCallback(async (type, detail = "") => {
    if (!creds || startedRef.current === "done") return;
    try {
      const { data } = await axios.post(`${API}/exam/violation`, { ...creds, violation_type: type, detail });
      if (data.auto_submitted) {
        setWarning({ final: true, msg: "Batas pelanggaran tercapai. Ujian ditutup otomatis." });
        setTimeout(finish, 2500);
      } else if (data.count !== undefined) {
        setViolations(data.count);
        setWarning({ msg: `Peringatan ${data.count}/${threshold} — ${type === "tab-switch" ? "kamu terdeteksi meninggalkan halaman ujian" : "kamu keluar dari mode layar penuh"}. Pelanggaran berikutnya dapat menutup ujian.` });
      }
    } catch {}
  }, [creds, threshold, finish]); // eslint-disable-line

  // anti-cheat listeners
  useEffect(() => {
    if (stage !== "tkj" && stage !== "disc") return;
    const onVis = () => {
      if (document.hidden) reportViolation("tab-switch", "Pindah tab / minimize");
    };
    const onFs = () => {
      if (!document.fullscreenElement) {
        setPaused({ type: "fullscreen", msg: "Kamu keluar dari mode layar penuh. Ujian dijeda." });
        reportViolation("fullscreen-exit", "Keluar fullscreen");
      }
    };
    document.addEventListener("visibilitychange", onVis);
    document.addEventListener("fullscreenchange", onFs);
    return () => {
      document.removeEventListener("visibilitychange", onVis);
      document.removeEventListener("fullscreenchange", onFs);
    };
  }, [stage, reportViolation]);

  // camera watchdog
  useEffect(() => {
    if ((stage !== "tkj" && stage !== "disc") || !streams.camera) return;
    const track = streams.camera.getVideoTracks()[0];
    if (!track) return;
    const check = setInterval(() => {
      if (track.readyState === "ended" || !track.enabled) {
        setPaused((p) => p || { type: "camera", msg: "Kamera dimatikan. Ujian dijeda sampai kamera aktif kembali." });
        reportViolation("camera-off", "Kamera dimatikan");
      }
    }, 3000);
    return () => clearInterval(check);
  }, [stage, streams.camera, reportViolation]);

  // enter fullscreen on first interaction
  const enterFullscreen = async () => {
    try { await document.documentElement.requestFullscreen(); } catch {}
    setPaused(null);
    startedRef.current = true;
  };

  // offline queue flush
  useEffect(() => {
    const flush = async () => {
      const pending = JSON.parse(localStorage.getItem("pending_answers") || "[]");
      if (!pending.length) return;
      localStorage.setItem("pending_answers", "[]");
      for (const p of pending) {
        try { await axios.post(`${API}/exam/answer`, p); } catch {}
      }
      setSaveStatus("saved");
    };
    window.addEventListener("online", flush);
    return () => window.removeEventListener("online", flush);
  }, []);

  const answer = async (qid, displayIdx) => {
    setAnswers((a) => ({ ...a, [qid]: displayIdx }));
    setSaveStatus("saving");
    const payload = { ...creds, question_id: qid, selected_index: displayIdx };
    try {
      const { data } = await axios.post(`${API}/exam/answer`, payload);
      if (data.remaining_seconds !== undefined) setRemaining(data.remaining_seconds);
      if (data.stage === "disc") { loadSession(); return; }
      setSaveStatus("saved");
    } catch (e) {
      if (!navigator.onLine || !e.response) {
        const pending = JSON.parse(localStorage.getItem("pending_answers") || "[]");
        pending.push(payload);
        localStorage.setItem("pending_answers", JSON.stringify(pending));
        setSaveStatus("offline");
      } else setSaveStatus("error");
    }
  };

  const submitTkj = async () => {
    try {
      const { data } = await axios.post(`${API}/exam/tkj/submit`, creds);
      setState(data);
      setStage(data.stage);
      setRemaining(data.remaining_seconds || 0);
      setDiscAnswers(data.disc_answers || {});
      setDiscIdx(0);
      if (data.stage === "done") finish();
    } catch (e) { setPaused({ type: "error", msg: errDetail(e) }); }
  };

  const answerDisc = async (gi, most, least) => {
    setDiscAnswers((a) => ({ ...a, [gi]: { most, least } }));
    if (most === undefined || least === undefined || most === least) return;
    setSaveStatus("saving");
    try {
      const { data } = await axios.post(`${API}/exam/disc/answer`, { ...creds, group_index: gi, most, least });
      if (data.stage === "done") { finish(); return; }
      setSaveStatus("saved");
    } catch { setSaveStatus("error"); }
  };

  const submitDisc = async () => {
    try {
      await axios.post(`${API}/exam/disc/submit`, creds);
      finish();
    } catch (e) { setPaused({ type: "error", msg: errDetail(e) }); }
  };

  if (!session) return null;

  if (stage === "done") {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center px-6">
        <div className="text-center max-w-md" data-testid="thank-you-screen">
          <CheckCircle size={64} weight="fill" className="text-emerald-500 mx-auto mb-6" />
          <h1 className="text-4xl font-semibold tracking-tight mb-3">Terima kasih!</h1>
          <p className="text-zinc-500 mb-8">Jawaban kamu telah tersimpan. Sesi ujian telah berakhir dan token tidak dapat digunakan kembali. Hasil akan disampaikan oleh panitia.</p>
          <Button data-testid="back-home-btn" variant="outline" onClick={() => nav("/")}>Kembali ke Beranda</Button>
        </div>
      </div>
    );
  }

  if (!state || (stage !== "tkj" && stage !== "disc")) {
    return <div className="min-h-screen flex items-center justify-center text-zinc-400">Memuat sesi ujian...</div>;
  }

  const needsFullscreen = !document.fullscreenElement && !startedRef.current;

  const questions = state.questions || [];
  const q = questions[idx];
  const answeredCount = Object.keys(answers).length;
  const discItems = state.disc_items || [];
  const g = discItems[discIdx];
  const discDone = Object.entries(discAnswers).filter(([, v]) => v.most !== undefined && v.least !== undefined && v.most !== v.least).length;
  const progress = stage === "tkj"
    ? (questions.length ? (answeredCount / questions.length) * 100 : 0)
    : (discItems.length ? (discDone / discItems.length) * 100 : 0);

  return (
    <div className="min-h-screen bg-white">
      <Progress value={progress} className="h-2 rounded-none fixed top-0 left-0 right-0 z-40" data-testid="exam-progress-bar" />

      {(needsFullscreen || paused) && (
        <div className="fixed inset-0 z-50 bg-white/95 backdrop-blur flex items-center justify-center px-6" data-testid="exam-pause-overlay">
          <div className="text-center max-w-md">
            <Warning size={48} weight="fill" className="text-amber-500 mx-auto mb-4" />
            <h2 className="text-2xl font-semibold mb-2">{needsFullscreen && !paused ? "Masuk Mode Layar Penuh" : "Ujian Dijeda"}</h2>
            <p className="text-zinc-500 mb-6">{paused ? paused.msg : "Ujian hanya bisa dikerjakan dalam mode layar penuh."}</p>
            {paused?.type === "camera" ? (
              <p className="text-sm text-zinc-400">Aktifkan kembali kamera untuk melanjutkan, lalu muat ulang halaman jika perlu.</p>
            ) : (
              <Button data-testid="resume-fullscreen-btn" onClick={enterFullscreen} className="bg-zinc-900 text-white hover:bg-zinc-800">
                Lanjutkan Ujian (Fullscreen)
              </Button>
            )}
          </div>
        </div>
      )}

      {warning && !warning.final && (
        <div className="fixed inset-0 z-[60] bg-black/50 flex items-center justify-center px-6" data-testid="violation-warning-modal">
          <div className="bg-white border-2 border-red-500 p-8 max-w-md text-center">
            <Warning size={40} weight="fill" className="text-red-500 mx-auto mb-3" />
            <h3 className="text-xl font-semibold mb-2">Pelanggaran Terdeteksi</h3>
            <p className="text-zinc-600 mb-5">{warning.msg}</p>
            <Button data-testid="dismiss-warning-btn" onClick={() => { setWarning(null); if (!document.fullscreenElement) enterFullscreen(); }}
              className="bg-red-600 hover:bg-red-700 text-white">Saya Mengerti</Button>
          </div>
        </div>
      )}
      {warning?.final && (
        <div className="fixed inset-0 z-[60] bg-black/70 flex items-center justify-center px-6">
          <div className="bg-white p-8 max-w-md text-center">
            <Warning size={40} weight="fill" className="text-red-600 mx-auto mb-3" />
            <p className="font-medium">{warning.msg}</p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-12 gap-8 p-6 md:p-10 max-w-7xl mx-auto pt-10">
        <div className="col-span-full md:col-span-8 lg:col-span-9">
          {stage === "tkj" && q && (
            <div data-testid="tkj-question-area">
              <p className="text-xs uppercase tracking-widest text-zinc-400 mb-2">
                Tes TKJ · Soal {idx + 1} dari {questions.length} {q.category && `· ${q.category}`}
              </p>
              <h2 className="text-xl sm:text-2xl font-medium text-left leading-relaxed mb-8" data-testid="question-text">{q.text}</h2>
              <div className="space-y-3">
                {q.options.map((opt, oi) => (
                  <label key={oi} data-testid={`option-${oi}`}
                    className={`flex items-center gap-4 border p-4 cursor-pointer hover:bg-zinc-50 ${answers[q.id] === oi ? "border-[#0055FF] bg-blue-50/50" : "border-zinc-200"}`}>
                    <input type="radio" name={`q-${q.id}`} checked={answers[q.id] === oi}
                      onChange={() => answer(q.id, oi)} className="w-4 h-4 accent-[#0055FF]" />
                    <span className="text-base text-left">{String.fromCharCode(65 + oi)}. {opt}</span>
                  </label>
                ))}
              </div>
              <div className="flex justify-between mt-10">
                <Button variant="outline" data-testid="prev-question-btn" disabled={idx === 0} onClick={() => setIdx(idx - 1)}>← Sebelumnya</Button>
                {idx < questions.length - 1 ? (
                  <Button data-testid="next-question-btn" onClick={() => setIdx(idx + 1)} className="bg-zinc-900 text-white hover:bg-zinc-800">Berikutnya →</Button>
                ) : (
                  <Button data-testid="submit-tkj-btn" onClick={submitTkj} className="bg-[#0055FF] hover:bg-[#0044CC] text-white">
                    Selesai TKJ → Lanjut Psikotes
                  </Button>
                )}
              </div>
            </div>
          )}

          {stage === "disc" && g && (
            <div data-testid="disc-question-area">
              <p className="text-xs uppercase tracking-widest text-zinc-400 mb-2">Psikotes DISC · Grup {discIdx + 1} dari {discItems.length}</p>
              <h2 className="text-xl sm:text-2xl font-medium text-left leading-relaxed mb-2">Pilih satu pernyataan yang <span className="text-[#0055FF]">PALING</span> dan satu yang <span className="text-red-600">KURANG</span> menggambarkan dirimu.</h2>
              <p className="text-sm text-zinc-500 mb-8">Paling dan Kurang tidak boleh pada pernyataan yang sama.</p>
              <div className="border border-zinc-200">
                <div className="grid grid-cols-[1fr_80px_80px] bg-zinc-50 border-b border-zinc-200 text-xs font-medium uppercase tracking-wider text-zinc-500">
                  <div className="p-3">Pernyataan</div>
                  <div className="p-3 text-center text-[#0055FF]">Paling</div>
                  <div className="p-3 text-center text-red-600">Kurang</div>
                </div>
                {g.statements.map((s, si) => {
                  const cur = discAnswers[g.group_index] || {};
                  return (
                    <div key={si} className="grid grid-cols-[1fr_80px_80px] border-b border-zinc-100 last:border-0 hover:bg-zinc-50">
                      <div className="p-4 text-left">{s}</div>
                      <div className="flex items-center justify-center">
                        <input type="radio" data-testid={`disc-most-${si}`} name={`most-${g.group_index}`}
                          checked={cur.most === si}
                          onChange={() => answerDisc(g.group_index, si, cur.least)}
                          className="w-5 h-5 accent-[#0055FF] cursor-pointer" />
                      </div>
                      <div className="flex items-center justify-center">
                        <input type="radio" data-testid={`disc-least-${si}`} name={`least-${g.group_index}`}
                          checked={cur.least === si}
                          onChange={() => answerDisc(g.group_index, cur.most, si)}
                          className="w-5 h-5 accent-red-600 cursor-pointer" />
                      </div>
                    </div>
                  );
                })}
              </div>
              {discAnswers[g.group_index]?.most !== undefined && discAnswers[g.group_index]?.most === discAnswers[g.group_index]?.least && (
                <p className="text-sm text-red-600 mt-3">Paling dan Kurang tidak boleh sama.</p>
              )}
              <div className="flex justify-between mt-10">
                <Button variant="outline" data-testid="disc-prev-btn" disabled={discIdx === 0} onClick={() => setDiscIdx(discIdx - 1)}>← Sebelumnya</Button>
                {discIdx < discItems.length - 1 ? (
                  <Button data-testid="disc-next-btn" onClick={() => setDiscIdx(discIdx + 1)} className="bg-zinc-900 text-white hover:bg-zinc-800">Berikutnya →</Button>
                ) : (
                  <Button data-testid="submit-disc-btn" onClick={submitDisc} disabled={discDone < discItems.length}
                    className="bg-[#0055FF] hover:bg-[#0044CC] text-white disabled:opacity-40">
                    Selesaikan Ujian ({discDone}/{discItems.length})
                  </Button>
                )}
              </div>
            </div>
          )}
        </div>

        <div className="col-span-full md:col-span-4 lg:col-span-3 space-y-5">
          <div className="border border-zinc-200 p-5 text-center">
            <p className="text-xs uppercase tracking-widest text-zinc-400 mb-1">Sisa Waktu {stage === "tkj" ? "TKJ" : "DISC"}</p>
            <p data-testid="exam-timer" className={`font-mono text-4xl font-bold tracking-tighter ${remaining < 300 ? "text-red-600" : "text-zinc-900"}`}>{fmt(remaining)}</p>
          </div>
          <CameraPreview stream={streams.camera} />
          <div className="flex items-center justify-between text-sm">
            <span data-testid="autosave-indicator" className={saveStatus === "saved" ? "text-emerald-600" : saveStatus === "offline" ? "text-amber-600" : "text-zinc-400"}>
              {saveStatus === "saving" ? "Menyimpan..." : saveStatus === "saved" ? "Tersimpan ✓" : saveStatus === "offline" ? "Offline — antre" : saveStatus === "error" ? "Gagal simpan" : ""}
            </span>
            <span data-testid="violation-counter" className={violations > 0 ? "text-red-600 font-medium" : "text-zinc-400"}>
              Pelanggaran: {violations}/{threshold}
            </span>
          </div>
          {stage === "tkj" && (
            <div>
              <p className="text-xs uppercase tracking-widest text-zinc-400 mb-2">Navigasi Soal</p>
              <div className="grid grid-cols-5 gap-1.5" data-testid="question-nav-grid">
                {questions.map((qq, qi) => (
                  <button key={qq.id} data-testid={`nav-q-${qi}`} onClick={() => setIdx(qi)}
                    className={`w-full aspect-square text-sm font-mono border
                      ${qi === idx ? "ring-2 ring-[#0055FF] ring-offset-1" : ""}
                      ${qq.id in answers ? "bg-zinc-900 text-white border-zinc-900" : "bg-white text-zinc-600 border-zinc-200 hover:bg-zinc-50"}`}>
                    {qi + 1}
                  </button>
                ))}
              </div>
            </div>
          )}
          {stage === "disc" && (
            <div className="grid grid-cols-6 gap-1.5" data-testid="disc-nav-grid">
              {discItems.map((it, gi) => {
                const a = discAnswers[it.group_index];
                const done = a && a.most !== undefined && a.least !== undefined && a.most !== a.least;
                return (
                  <button key={gi} onClick={() => setDiscIdx(gi)}
                    className={`w-full aspect-square text-xs font-mono border
                      ${gi === discIdx ? "ring-2 ring-[#0055FF] ring-offset-1" : ""}
                      ${done ? "bg-zinc-900 text-white border-zinc-900" : "bg-white text-zinc-600 border-zinc-200"}`}>
                    {gi + 1}
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
