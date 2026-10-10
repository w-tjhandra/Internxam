import { useCallback, useEffect, useRef, useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { API, errDetail } from "@/lib/api";
import { getStreams, stopStreams } from "@/lib/mediaStore";
import { CameraPreview } from "@/components/exam/CameraPreview";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { CheckCircle, Warning } from "@phosphor-icons/react";
import * as faceapi from "@vladmandic/face-api";
import ScenarioAssessment from "@/features/exam/components/ScenarioAssessment";
import WorkDiscAssessment from "@/features/exam/components/WorkDiscAssessment";

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
  const [scenarioIdx, setScenarioIdx] = useState(0);
  const [scenarioAnswers, setScenarioAnswers] = useState({});
  const [workDiscIdx, setWorkDiscIdx] = useState(0);
  const [workDiscAnswers, setWorkDiscAnswers] = useState({});
  const [remaining, setRemaining] = useState(0);
  const [saveStatus, setSaveStatus] = useState("");
  const [paused, setPaused] = useState(null);
  const [warning, setWarning] = useState(null);
  const [violations, setViolations] = useState(0);
  const [threshold, setThreshold] = useState(3);
  const startedRef = useRef(false);
  const streams = getStreams();

  const creds = useMemo(() => session ? { participant_id: session.participant_id, token: session.token } : null, [session]);

  const finish = useCallback(() => {
    setStage("done");
    stopStreams();
    if (document.fullscreenElement) document.exitFullscreen().catch(() => {});
    localStorage.removeItem("exam_session");
    localStorage.removeItem("pending_answers");
    localStorage.removeItem("pending_scenario_answers");
    localStorage.removeItem("pending_work_disc_answers");
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
      if (data.stage === "scenario") {
        const savedAnswers = data.scenario_answers || {};
        setScenarioAnswers(savedAnswers);
        const items = data.scenario_items || [];
        const firstUnanswered = items.findIndex((item) => !(item.id in savedAnswers));
        setScenarioIdx(firstUnanswered >= 0 ? firstUnanswered : 0);
      }
      if (data.stage === "work_disc") {
        const savedAnswers = data.work_disc_answers || {};
        setWorkDiscAnswers(savedAnswers);
        const items = data.work_disc_items || [];
        const firstUnanswered = items.findIndex((item) => !(item.id in savedAnswers));
        setWorkDiscIdx(firstUnanswered >= 0 ? firstUnanswered : 0);
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
    if (stage !== "tkj" && stage !== "disc" && stage !== "scenario" && stage !== "work_disc") return;
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
        let msgDetail = "terdapat pelanggaran keamanan";
        if (type === "tab-switch") msgDetail = "kamu terdeteksi meninggalkan halaman ujian";
        else if (type === "fullscreen-exit") msgDetail = "kamu keluar dari mode layar penuh";
        else if (type === "camera-off") msgDetail = "kamera dimatikan";
        else if (type === "face-missing") msgDetail = "wajah tidak terdeteksi di kamera";
        else if (type === "multiple-faces") msgDetail = "terdeteksi orang lain di kamera";
        else if (type === "face-mismatch") msgDetail = "wajah tidak cocok dengan peserta asli";
        setWarning({ msg: `Peringatan ${data.count}/${threshold} — ${msgDetail}. Pelanggaran berikutnya dapat menutup ujian.` });
      }
    } catch {}
  }, [creds, threshold, finish]); // eslint-disable-line

  // anti-cheat listeners
  useEffect(() => {
    if (stage !== "tkj" && stage !== "disc" && stage !== "scenario" && stage !== "work_disc") return;
    const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

    const onVis = () => {
      if (document.hidden) reportViolation("tab-switch", "Pindah tab / minimize");
    };
    const onBlur = () => {
      reportViolation("tab-switch", "Jendela browser kehilangan fokus / tertumpuk");
    };
    const onFs = () => {
      if (!isMobile && !document.fullscreenElement) {
        setPaused({ type: "fullscreen", msg: "Kamu keluar dari mode layar penuh. Ujian dijeda." });
        reportViolation("fullscreen-exit", "Keluar fullscreen");
      }
    };

    const awayCheck = setInterval(() => {
      if (document.hidden || !document.hasFocus()) {
        reportViolation("tab-switch", "Berada di luar ujian / membuka aplikasi lain (penalti berlanjut)");
      } else if (!isMobile && !document.fullscreenElement) {
        reportViolation("fullscreen-exit", "Layar tidak penuh (penalti berlanjut)");
      }
    }, 2000);

    document.addEventListener("visibilitychange", onVis);
    window.addEventListener("blur", onBlur);
    if (!isMobile) document.addEventListener("fullscreenchange", onFs);
    return () => {
      clearInterval(awayCheck);
      document.removeEventListener("visibilitychange", onVis);
      window.removeEventListener("blur", onBlur);
      if (!isMobile) document.removeEventListener("fullscreenchange", onFs);
    };
  }, [stage, reportViolation]);

  // camera & face watchdog
  useEffect(() => {
    if ((stage !== "tkj" && stage !== "disc" && stage !== "scenario" && stage !== "work_disc") || !streams.camera) return;
    const track = streams.camera.getVideoTracks()[0];
    if (!track) return;

    const baselineStr = localStorage.getItem("baseline_face");
    const baselineDesc = baselineStr ? new Float32Array(JSON.parse(baselineStr)) : null;
    const faceAnomalyGraceMs = 12000;
    let faceAnomalyStartedAt = null;
    let reportedFaceAnomaly = false;
    let checkingFace = false;

    const check = setInterval(async () => {
      if (checkingFace) return;
      if (track.readyState === "ended" || !track.enabled) {
        setPaused((p) => p || { type: "camera", msg: "Kamera dimatikan. Ujian dijeda sampai kamera aktif kembali." });
        reportViolation("camera-off", "Kamera dimatikan");
        return;
      }

      const videoEl = document.getElementById("face-video-preview");
      if (!videoEl) return;
      if (videoEl.paused) videoEl.play().catch(() => {});
      if (videoEl.readyState < 2) return;

      if (baselineDesc) {
        checkingFace = true;
        try {
          const opts = new faceapi.SsdMobilenetv1Options({ minConfidence: 0.2 });
          const faces = await faceapi.detectAllFaces(videoEl, opts).withFaceLandmarks().withFaceDescriptors();
          let anomaly = null;
          if (faces.length === 0) {
            anomaly = ["face-missing", "Wajah tidak terdeteksi di depan kamera"];
          } else if (faces.length > 1) {
            anomaly = ["multiple-faces", "Terdeteksi lebih dari satu orang di kamera"];
          } else {
            const dist = faceapi.euclideanDistance(faces[0].descriptor, baselineDesc);
            if (dist > 0.65) {
              anomaly = ["face-mismatch", "Wajah tidak cocok dengan peserta asli"];
            }
          }

          if (anomaly) {
            if (faceAnomalyStartedAt === null) {
              faceAnomalyStartedAt = Date.now();
            } else if (
              !reportedFaceAnomaly
              && Date.now() - faceAnomalyStartedAt >= faceAnomalyGraceMs
            ) {
              reportViolation(...anomaly);
              reportedFaceAnomaly = true;
            }
          } else {
            faceAnomalyStartedAt = null;
            reportedFaceAnomaly = false;
          }
        } catch {
          faceAnomalyStartedAt = null;
          reportedFaceAnomaly = false;
        } finally {
          checkingFace = false;
        }
      }
    }, 2000);

    return () => {
      clearInterval(check);
    };
  }, [stage, streams.camera, reportViolation]);

  // enter fullscreen on first interaction
  const enterFullscreen = async () => {
    try { await document.documentElement.requestFullscreen(); } catch {}
    setPaused(null);
    startedRef.current = true;
  };

  // offline queue flush
  useEffect(() => {
    const flushQueue = async (storageKey, endpoint) => {
      const pending = JSON.parse(localStorage.getItem(storageKey) || "[]");
      if (!pending.length) return;
      const remainingItems = [];
      for (const payload of pending) {
        try { await axios.post(`${API}${endpoint}`, payload); }
        catch { remainingItems.push(payload); }
      }
      localStorage.setItem(storageKey, JSON.stringify(remainingItems));
      setSaveStatus(remainingItems.length ? "error" : "saved");
    };
    const flush = async () => {
      await flushQueue("pending_answers", "/exam/answer");
      await flushQueue("pending_scenario_answers", "/exam/scenario/answer");
      await flushQueue("pending_work_disc_answers", "/exam/work-disc/answer");
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
      if (data.stage !== "tkj") { loadSession(); return; }
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
      setScenarioAnswers(data.scenario_answers || {});
      setScenarioIdx(0);
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

  const answerScenario = async (scenarioId, selectedIndex) => {
    setScenarioAnswers((current) => ({ ...current, [scenarioId]: selectedIndex }));
    setSaveStatus("saving");
    const payload = { ...creds, scenario_id: scenarioId, selected_index: selectedIndex };
    try {
      const { data } = await axios.post(`${API}/exam/scenario/answer`, payload);
      if (data.remaining_seconds !== undefined) setRemaining(data.remaining_seconds);
      if (data.stage === "done") { finish(); return; }
      if (data.stage !== "scenario") { loadSession(); return; }
      setSaveStatus("saved");
    } catch (e) {
      if (!navigator.onLine || !e.response) {
        const pending = JSON.parse(localStorage.getItem("pending_scenario_answers") || "[]");
        localStorage.setItem("pending_scenario_answers", JSON.stringify([
          ...pending.filter((item) => item.scenario_id !== scenarioId),
          payload,
        ]));
        setSaveStatus("offline");
      } else {
        setSaveStatus("error");
      }
    }
  };

  const submitScenario = async () => {
    try {
      const { data } = await axios.post(`${API}/exam/scenario/submit`, creds);
      setState(data);
      setStage(data.stage);
      setRemaining(data.remaining_seconds || 0);
      if (data.stage === "work_disc") {
        const savedAnswers = data.work_disc_answers || {};
        const items = data.work_disc_items || [];
        setWorkDiscAnswers(savedAnswers);
        const firstUnanswered = items.findIndex((item) => !(item.id in savedAnswers));
        setWorkDiscIdx(firstUnanswered >= 0 ? firstUnanswered : 0);
      }
      if (data.stage === "done") finish();
    } catch (e) {
      setPaused({ type: "error", msg: errDetail(e) });
    }
  };

  const answerWorkDisc = async (itemId, selectedIndex) => {
    setWorkDiscAnswers((current) => ({ ...current, [itemId]: selectedIndex }));
    setSaveStatus("saving");
    const payload = { ...creds, item_id: itemId, selected_index: selectedIndex };
    try {
      const { data } = await axios.post(`${API}/exam/work-disc/answer`, payload);
      if (data.remaining_seconds !== undefined) setRemaining(data.remaining_seconds);
      if (data.stage === "done") { finish(); return; }
      setSaveStatus("saved");
    } catch (e) {
      if (!navigator.onLine || !e.response) {
        const pending = JSON.parse(localStorage.getItem("pending_work_disc_answers") || "[]");
        localStorage.setItem("pending_work_disc_answers", JSON.stringify([
          ...pending.filter((answer) => answer.item_id !== itemId),
          payload,
        ]));
        setSaveStatus("offline");
      } else {
        setSaveStatus("error");
      }
    }
  };

  const submitWorkDisc = async () => {
    try {
      const pending = JSON.parse(localStorage.getItem("pending_work_disc_answers") || "[]");
      if (pending.length && !navigator.onLine) {
        throw new Error("Koneksi internet diperlukan untuk menyimpan jawaban yang masih tertunda.");
      }
      for (const payload of pending) {
        const { data } = await axios.post(`${API}/exam/work-disc/answer`, payload);
        if (data.stage === "done") { finish(); return; }
      }
      localStorage.removeItem("pending_work_disc_answers");
      await axios.post(`${API}/exam/work-disc/submit`, creds);
      finish();
    } catch (e) {
      setPaused({ type: "error", msg: errDetail(e) });
    }
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

  if (!state || (stage !== "tkj" && stage !== "disc" && stage !== "scenario" && stage !== "work_disc")) {
    return <div className="min-h-screen flex items-center justify-center text-zinc-400">Memuat sesi ujian...</div>;
  }

  const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
  const needsFullscreen = !isMobile && !document.fullscreenElement && !startedRef.current;
  const needsMobileStart = isMobile && !startedRef.current;
  const showOverlay = needsFullscreen || needsMobileStart || paused;

  const questions = state.questions || [];
  const q = questions[idx];
  const answeredCount = Object.keys(answers).length;
  const discItems = state.disc_items || [];
  const g = discItems[discIdx];
  const discDone = Object.entries(discAnswers).filter(([, v]) => v.most !== undefined && v.least !== undefined && v.most !== v.least).length;
  const scenarioItems = state.scenario_items || [];
  const scenario = scenarioItems[scenarioIdx];
  const scenarioDone = Object.keys(scenarioAnswers).length;
  const workDiscItems = state.work_disc_items || [];
  const workDiscAnsweredCount = workDiscItems.filter((item) => Number.isInteger(workDiscAnswers[item.id])).length;
  const progress = stage === "tkj"
    ? (questions.length ? (answeredCount / questions.length) * 100 : 0)
    : stage === "scenario"
      ? (scenarioItems.length ? (scenarioDone / scenarioItems.length) * 100 : 0)
      : stage === "work_disc"
        ? (workDiscItems.length ? (workDiscAnsweredCount / workDiscItems.length) * 100 : 0)
        : (discItems.length ? (discDone / discItems.length) * 100 : 0);

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-slate-50 to-blue-50 font-sans selection:bg-blue-100">
      {/* Anti-Cheat Watermark Overlay */}
      {state && (
        <div className="pointer-events-none fixed inset-0 z-[100] overflow-hidden opacity-[0.04] flex flex-wrap justify-center items-center gap-x-24 gap-y-32 select-none">
          {Array.from({ length: 40 }).map((_, i) => (
            <div key={i} className="text-4xl font-black tracking-widest text-slate-900 transform -rotate-45 whitespace-nowrap">
              {state.name?.toUpperCase()} · {session.token.toUpperCase()}
            </div>
          ))}
        </div>
      )}

      <Progress value={progress} className="h-2 rounded-none fixed top-0 left-0 right-0 z-40" data-testid="exam-progress-bar" />

      {showOverlay && (
        <div className="fixed inset-0 z-50 bg-white/95 backdrop-blur flex items-center justify-center px-6" data-testid="exam-pause-overlay">
          <div className="text-center max-w-md">
            <Warning size={48} weight="fill" className="text-amber-500 mx-auto mb-4" />
            <h2 className="text-2xl font-semibold mb-2">{(needsFullscreen || needsMobileStart) && !paused ? "Mulai Ujian" : "Ujian Dijeda"}</h2>
            <p className="text-zinc-500 mb-6">{paused ? paused.msg : (isMobile ? "Ketuk tombol di bawah untuk masuk ke ujian." : "Ujian hanya bisa dikerjakan dalam mode layar penuh.")}</p>
            {paused?.type === "camera" ? (
              <p className="text-sm text-zinc-400">Aktifkan kembali kamera untuk melanjutkan, lalu muat ulang halaman jika perlu.</p>
            ) : (
              <Button data-testid="resume-fullscreen-btn" onClick={enterFullscreen} className="bg-zinc-900 text-white hover:bg-zinc-800">
                {isMobile ? "Mulai Ujian Sekarang" : "Lanjutkan Ujian (Fullscreen)"}
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
            <div data-testid="tkj-question-area" className="bg-white/60 backdrop-blur-xl border border-white/50 shadow-xl rounded-3xl p-8 md:p-10 transition-all">
              <p className="text-xs uppercase tracking-widest text-indigo-500 font-semibold mb-3">
                Tes TKJ · Soal {idx + 1} dari {questions.length} {q.category && `· ${q.category}`}
              </p>
              <h2 className="text-xl sm:text-2xl font-medium text-slate-800 leading-relaxed mb-8" data-testid="question-text">{q.text}</h2>
              <div className="space-y-4">
                {q.options.map((opt, oi) => (
                  <label key={oi} data-testid={`option-${oi}`}
                    className={`flex items-center gap-4 border-2 p-5 rounded-2xl cursor-pointer transition-all duration-300 transform hover:scale-[1.01] shadow-sm ${answers[q.id] === oi ? "border-indigo-500 bg-indigo-50/80 shadow-md" : "border-white/60 bg-white/40 hover:bg-white hover:border-indigo-200 hover:shadow-md"}`}>
                    <input type="radio" name={`q-${q.id}`} checked={answers[q.id] === oi}
                      onChange={() => answer(q.id, oi)} className="w-5 h-5 accent-indigo-600" />
                    <span className="text-base text-left">{String.fromCharCode(65 + oi)}. {opt}</span>
                  </label>
                ))}
              </div>
              <div className="flex justify-between mt-10">
                <Button variant="outline" data-testid="prev-question-btn" disabled={idx === 0} onClick={() => setIdx(idx - 1)} className="rounded-full px-6 transition-transform hover:-translate-x-1">← Sebelumnya</Button>
                {idx < questions.length - 1 ? (
                  <Button data-testid="next-question-btn" onClick={() => setIdx(idx + 1)} className="bg-slate-900 text-white rounded-full px-6 shadow-lg transition-transform hover:translate-x-1 hover:bg-slate-800 hover:shadow-xl">Berikutnya →</Button>
                ) : (
                  <Button data-testid="submit-tkj-btn" onClick={submitTkj} className="bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700 text-white rounded-full px-6 shadow-lg shadow-indigo-200 transition-all hover:scale-105">
                    Selesai TKJ → Lanjut Asesmen Skenario
                  </Button>
                )}
              </div>
            </div>
          )}

          {stage === "scenario" && (
            <ScenarioAssessment
              scenario={scenario}
              scenarioIdx={scenarioIdx}
              scenarioCount={scenarioItems.length}
              selectedIndex={scenarioAnswers[scenario?.id]}
              answeredCount={scenarioDone}
              saveStatus={saveStatus}
              onAnswer={answerScenario}
              onPrevious={() => setScenarioIdx(scenarioIdx - 1)}
              onNext={() => setScenarioIdx(scenarioIdx + 1)}
              onSubmit={submitScenario}
            />
          )}

          {stage === "work_disc" && (
            <WorkDiscAssessment
              items={workDiscItems}
              itemIndex={workDiscIdx}
              answers={workDiscAnswers}
              saveStatus={saveStatus}
              onAnswer={answerWorkDisc}
              onPrevious={() => setWorkDiscIdx((current) => current - 1)}
              onNext={() => setWorkDiscIdx((current) => current + 1)}
              onSubmit={submitWorkDisc}
            />
          )}

          {stage === "disc" && g && (
            <div data-testid="disc-question-area" className="bg-white/60 backdrop-blur-xl border border-white/50 shadow-xl rounded-3xl p-8 md:p-10 transition-all">
              <p className="text-xs uppercase tracking-widest text-indigo-500 font-semibold mb-2">Psikotes DISC · Grup {discIdx + 1} dari {discItems.length}</p>
              <h2 className="text-xl sm:text-2xl font-medium text-slate-800 leading-relaxed mb-2">Pilih satu pernyataan yang <span className="text-indigo-600 font-bold">PALING</span> dan satu yang <span className="text-red-500 font-bold">KURANG</span> menggambarkan dirimu.</h2>
              <p className="text-sm text-slate-500 mb-8">Paling dan Kurang tidak boleh pada pernyataan yang sama.</p>
              <div className="border border-white/50 bg-white/40 rounded-2xl overflow-hidden shadow-sm">
                <div className="grid grid-cols-[1fr_80px_80px] bg-white/60 border-b border-white/50 text-xs font-semibold uppercase tracking-wider text-slate-500">
                  <div className="p-4">Pernyataan</div>
                  <div className="p-4 text-center text-indigo-600">Paling</div>
                  <div className="p-4 text-center text-red-500">Kurang</div>
                </div>
                {g.statements.map((s, si) => {
                  const cur = discAnswers[g.group_index] || {};
                  return (
                    <div key={si} className="grid grid-cols-[1fr_80px_80px] border-b border-white/30 last:border-0 hover:bg-white/80 transition-colors">
                      <div className="p-5 text-left text-sm md:text-base text-slate-700">{s}</div>
                      <div className="flex items-center justify-center">
                        <input type="radio" data-testid={`disc-most-${si}`} name={`most-${g.group_index}`}
                          checked={cur.most === si}
                          onChange={() => answerDisc(g.group_index, si, cur.least)}
                          className="w-6 h-6 accent-indigo-600 cursor-pointer transform hover:scale-110 transition-transform" />
                      </div>
                      <div className="flex items-center justify-center">
                        <input type="radio" data-testid={`disc-least-${si}`} name={`least-${g.group_index}`}
                          checked={cur.least === si}
                          onChange={() => answerDisc(g.group_index, cur.most, si)}
                          className="w-6 h-6 accent-red-500 cursor-pointer transform hover:scale-110 transition-transform" />
                      </div>
                    </div>
                  );
                })}
              </div>
              {discAnswers[g.group_index]?.most !== undefined && discAnswers[g.group_index]?.most === discAnswers[g.group_index]?.least && (
                <p className="text-sm text-red-600 mt-3">Paling dan Kurang tidak boleh sama.</p>
              )}
              <div className="flex justify-between mt-10">
                <Button variant="outline" data-testid="disc-prev-btn" disabled={discIdx === 0} onClick={() => setDiscIdx(discIdx - 1)} className="rounded-full px-6 transition-transform hover:-translate-x-1">← Sebelumnya</Button>
                {discIdx < discItems.length - 1 ? (
                  <Button data-testid="disc-next-btn" onClick={() => setDiscIdx(discIdx + 1)} className="bg-slate-900 text-white rounded-full px-6 shadow-lg transition-transform hover:translate-x-1 hover:bg-slate-800 hover:shadow-xl">Berikutnya →</Button>
                ) : (
                  <Button data-testid="submit-disc-btn" onClick={submitDisc} disabled={discDone < discItems.length}
                    className="bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700 text-white rounded-full px-6 shadow-lg shadow-indigo-200 transition-all hover:scale-105 disabled:opacity-50 disabled:hover:scale-100">
                    Selesaikan Ujian ({discDone}/{discItems.length})
                  </Button>
                )}
              </div>
            </div>
          )}
        </div>

        <div className="col-span-full md:col-span-4 lg:col-span-3 space-y-6">
          <div className="bg-white/60 backdrop-blur-xl border border-white/50 shadow-xl rounded-3xl p-6 text-center">
            <p className="text-xs uppercase tracking-widest text-indigo-500 font-semibold mb-2">
              Sisa Waktu {stage === "tkj" ? "TKJ" : stage === "scenario" ? "Asesmen Situasi PKL" : stage === "work_disc" ? "Situasi Kerja DISC" : "DISC lama"}
            </p>
            <p data-testid="exam-timer" className={`font-mono text-5xl font-black tracking-tighter drop-shadow-sm ${remaining < 300 ? "text-red-500 animate-pulse" : "text-slate-800"}`}>{fmt(remaining)}</p>
          </div>
          <div className="rounded-3xl overflow-hidden shadow-lg border border-white/50 bg-black">
            <CameraPreview stream={streams.camera} />
          </div>
          <div className="flex items-center justify-between text-sm px-2">
            <span data-testid="autosave-indicator" className={saveStatus === "saved" ? "text-emerald-500 font-medium" : saveStatus === "offline" ? "text-amber-500 font-medium" : "text-slate-400"}>
              {saveStatus === "saving" ? "Menyimpan..." : saveStatus === "saved" ? "Tersimpan ✓" : saveStatus === "offline" ? "Offline — antre" : saveStatus === "error" ? "Gagal simpan" : ""}
            </span>
            <span data-testid="violation-counter" className={violations > 0 ? "text-red-500 font-bold bg-red-50 px-2 py-0.5 rounded-full" : "text-slate-400"}>
              Pelanggaran: {violations}/{threshold}
            </span>
          </div>
          {stage === "tkj" && (
            <div className="bg-white/60 backdrop-blur-xl border border-white/50 shadow-xl rounded-3xl p-5">
              <p className="text-xs uppercase tracking-widest text-indigo-500 font-semibold mb-3 text-center">Navigasi Soal</p>
              <div className="grid grid-cols-5 gap-2" data-testid="question-nav-grid">
                {questions.map((qq, qi) => (
                  <button key={qq.id} data-testid={`nav-q-${qi}`} onClick={() => setIdx(qi)}
                    className={`w-full aspect-square text-sm font-mono font-medium rounded-xl border transition-all duration-200 transform hover:scale-105
                      ${qi === idx ? "ring-2 ring-indigo-500 ring-offset-2 ring-offset-indigo-50 bg-indigo-50 border-indigo-200 text-indigo-700" : ""}
                      ${qq.id in answers ? "bg-indigo-600 text-white border-indigo-600 shadow-md" : "bg-white/80 text-slate-600 border-white/60 hover:bg-white hover:shadow-sm"}`}>
                    {qi + 1}
                  </button>
                ))}
              </div>
            </div>
          )}
          {stage === "disc" && (
            <div className="bg-white/60 backdrop-blur-xl border border-white/50 shadow-xl rounded-3xl p-5">
              <p className="text-xs uppercase tracking-widest text-indigo-500 font-semibold mb-3 text-center">Navigasi Grup</p>
              <div className="grid grid-cols-6 gap-2" data-testid="disc-nav-grid">
              {discItems.map((it, gi) => {
                const a = discAnswers[it.group_index];
                const done = a && a.most !== undefined && a.least !== undefined && a.most !== a.least;
                return (
                  <button key={gi} onClick={() => setDiscIdx(gi)}
                    className={`w-full aspect-square text-xs font-mono font-medium rounded-xl border transition-all duration-200 transform hover:scale-105
                      ${gi === discIdx ? "ring-2 ring-indigo-500 ring-offset-2 ring-offset-indigo-50 bg-indigo-50 border-indigo-200 text-indigo-700" : ""}
                      ${done ? "bg-indigo-600 text-white border-indigo-600 shadow-md" : "bg-white/80 text-slate-600 border-white/60 hover:bg-white hover:shadow-sm"}`}>
                    {gi + 1}
                  </button>
                );
              })}
              </div>
            </div>
          )}
          {stage === "scenario" && (
            <div className="bg-white/60 backdrop-blur-xl border border-white/50 shadow-xl rounded-3xl p-5">
              <p className="text-xs uppercase tracking-widest text-indigo-500 font-semibold mb-3 text-center">Navigasi Skenario</p>
              <div className="grid grid-cols-4 gap-2" data-testid="scenario-nav-grid">
                {scenarioItems.map((item, itemIdx) => (
                  <button key={item.id} data-testid={`nav-scenario-${itemIdx}`}
                    onClick={() => setScenarioIdx(itemIdx)}
                    className={`w-full aspect-square text-xs font-mono font-medium rounded-xl border transition-all ${
                      itemIdx === scenarioIdx
                        ? "ring-2 ring-indigo-500 ring-offset-2 bg-indigo-50 border-indigo-200 text-indigo-700"
                        : item.id in scenarioAnswers
                          ? "bg-indigo-600 text-white border-indigo-600"
                          : "bg-white/80 text-slate-600 border-white/60 hover:bg-white"
                    }`}>
                    {itemIdx + 1}
                  </button>
                ))}
              </div>
            </div>
          )}
          {stage === "work_disc" && (
            <div className="rounded-3xl border border-white/50 bg-white/60 p-5 shadow-xl backdrop-blur-xl">
              <p className="mb-3 text-center text-xs font-semibold uppercase tracking-widest text-indigo-500">
                Navigasi Pertanyaan
              </p>
              <div className="grid grid-cols-5 gap-2" data-testid="work-disc-nav-grid">
                {workDiscItems.map((item, itemIndex) => {
                  const answered = Number.isInteger(workDiscAnswers[item.id]);
                  return (
                    <button
                      key={item.id}
                      data-testid={`nav-work-disc-${itemIndex}`}
                      onClick={() => setWorkDiscIdx(itemIndex)}
                      className={`aspect-square rounded-xl border text-xs font-mono font-medium transition-all ${
                        itemIndex === workDiscIdx
                          ? "ring-2 ring-indigo-500 ring-offset-2 bg-indigo-50 border-indigo-200 text-indigo-700"
                          : answered
                            ? "bg-indigo-600 text-white border-indigo-600"
                            : "bg-white/80 text-slate-600 border-white/60 hover:bg-white"
                      }`}
                    >
                      {itemIndex + 1}
                    </button>
                  );
                })}
              </div>
              <p className="mt-3 text-center text-xs text-slate-500">
                {workDiscAnsweredCount}/{workDiscItems.length} terjawab
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
