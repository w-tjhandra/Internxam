import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { API } from "@/lib/api";
import { setStreams } from "@/lib/mediaStore";
import { Button } from "@/components/ui/button";
import { Camera, Monitor, ShieldCheck, CheckCircle, WarningCircle } from "@phosphor-icons/react";

export default function PreFlight() {
  const nav = useNavigate();
  const videoRef = useRef(null);
  const camRef = useRef(null);
  const screenRef = useRef(null);
  const [camOk, setCamOk] = useState(false);
  const [screenOk, setScreenOk] = useState(false);
  const [seb, setSeb] = useState({ require_seb: false, seb_detected: false });
  const [error, setError] = useState("");

  useEffect(() => {
    const session = localStorage.getItem("exam_session");
    if (!session) { nav("/"); return; }
    axios.get(`${API}/exam/seb-status`).then((r) => setSeb(r.data)).catch(() => {});
  }, [nav]);

  const enableCamera = async () => {
    setError("");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      camRef.current = stream;
      if (videoRef.current) videoRef.current.srcObject = stream;
      setCamOk(true);
    } catch {
      setError("Izin kamera ditolak. Aktifkan izin kamera di browser untuk melanjutkan.");
    }
  };

  const enableScreen = async () => {
    setError("");
    try {
      const stream = await navigator.mediaDevices.getDisplayMedia({ video: true });
      screenRef.current = stream;
      setScreenOk(true);
      stream.getVideoTracks()[0].addEventListener("ended", () => setScreenOk(false));
    } catch {
      setError("Izin berbagi layar ditolak. Pilih 'Seluruh Layar' saat diminta.");
    }
  };

  const proceed = () => {
    setStreams(camRef.current, screenRef.current);
    nav("/exam");
  };

  const sebBlocked = seb.require_seb && !seb.seb_detected;
  const ready = camOk && screenOk && !sebBlocked;

  const Item = ({ ok, icon: Icon, title, desc, action, actionLabel, testid }) => (
    <div className="flex items-start gap-4 border border-zinc-200 p-5">
      <Icon size={24} className={ok ? "text-emerald-600" : "text-zinc-400"} weight={ok ? "fill" : "regular"} />
      <div className="flex-1">
        <p className="font-medium text-zinc-900">{title}</p>
        <p className="text-sm text-zinc-500 mt-0.5">{desc}</p>
      </div>
      {ok ? (
        <CheckCircle size={22} weight="fill" className="text-emerald-600 mt-1" />
      ) : action ? (
        <Button size="sm" variant="outline" data-testid={testid} onClick={action}>{actionLabel}</Button>
      ) : null}
    </div>
  );

  return (
    <div className="min-h-screen bg-white flex items-center justify-center px-6">
      <div className="w-full max-w-2xl py-12">
        <div className="flex items-center gap-2 mb-8">
          <ShieldCheck size={24} weight="fill" className="text-[#0055FF]" />
          <span className="font-semibold tracking-tight">SecureCBT</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-semibold tracking-tight mb-2">Pemeriksaan Perangkat</h1>
        <p className="text-zinc-500 mb-8">Selama ujian, kamera dan layar kamu ditampilkan sebagai bagian dari pengawasan. <span className="font-medium text-zinc-700">Tidak ada rekaman yang disimpan.</span></p>

        <div className="space-y-3" data-testid="preflight-checklist">
          <Item ok={camOk} icon={Camera} title="Kamera" desc="Wajib aktif selama ujian. Jika dimatikan, ujian akan dijeda."
            action={enableCamera} actionLabel="Aktifkan Kamera" testid="enable-camera-btn" />
          <Item ok={screenOk} icon={Monitor} title="Berbagi Layar Penuh" desc="Pilih 'Seluruh Layar / Entire Screen' saat diminta."
            action={enableScreen} actionLabel="Bagikan Layar" testid="enable-screen-btn" />
          <div className="flex items-start gap-4 border border-zinc-200 p-5">
            <ShieldCheck size={24} className={seb.seb_detected ? "text-emerald-600" : "text-zinc-400"} />
            <div className="flex-1">
              <p className="font-medium text-zinc-900">Safe Exam Browser</p>
              <p className="text-sm text-zinc-500 mt-0.5">
                {seb.require_seb
                  ? (seb.seb_detected ? "SEB terdeteksi." : "Sesi ini WAJIB menggunakan Safe Exam Browser. Buka ujian melalui aplikasi SEB.")
                  : "Tidak diwajibkan untuk sesi ini (mode soft-lock aktif)."}
              </p>
            </div>
            {sebBlocked && <WarningCircle size={22} weight="fill" className="text-red-500 mt-1" />}
          </div>
        </div>

        <div className="mt-6 flex items-center gap-6">
          <video ref={videoRef} autoPlay muted playsInline
            className={`w-40 aspect-video object-cover bg-zinc-100 border border-zinc-200 ${camOk ? "" : "opacity-40"}`}
            data-testid="preflight-camera-preview" />
          <div className="text-sm text-zinc-500">
            <p className="font-medium text-zinc-900 mb-1">Aturan ujian</p>
            <ul className="list-disc pl-4 space-y-0.5">
              <li>Ujian berjalan dalam mode layar penuh</li>
              <li>Pindah tab / keluar fullscreen = pelanggaran</li>
              <li>3 pelanggaran = ujian ditutup otomatis</li>
            </ul>
          </div>
        </div>

        {error && <p data-testid="preflight-error" className="mt-4 text-sm text-red-600">{error}</p>}

        <Button data-testid="proceed-to-exam-btn" disabled={!ready} onClick={proceed}
          className="mt-8 h-12 w-full text-base bg-[#0055FF] hover:bg-[#0044CC] text-white disabled:opacity-40">
          Mulai Ujian Sekarang
        </Button>
      </div>
    </div>
  );
}
