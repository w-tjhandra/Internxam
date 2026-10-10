import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { API } from "@/lib/api";
import { setStreams } from "@/lib/mediaStore";
import { Button } from "@/components/ui/button";
import { Camera, Monitor, ShieldCheck, CheckCircle, WarningCircle, HourglassHigh } from "@phosphor-icons/react";
import * as faceapi from "@vladmandic/face-api";

export default function PreFlight() {
  const nav = useNavigate();
  const videoRef = useRef(null);
  const camRef = useRef(null);
  const screenRef = useRef(null);
  const [camOk, setCamOk] = useState(false);
  const [screenOk, setScreenOk] = useState(false);
  const [screenNotice, setScreenNotice] = useState("");
  const [seb, setSeb] = useState({ require_seb: false, seb_detected: false });
  const [error, setError] = useState("");
  const [modelsLoaded, setModelsLoaded] = useState(false);

  const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

  useEffect(() => {
    const loadAI = async () => {
      try {
        const cdn = "https://cdn.jsdelivr.net/npm/@vladmandic/face-api/model/";
        await Promise.all([
          faceapi.nets.ssdMobilenetv1.loadFromUri(cdn),
          faceapi.nets.faceLandmark68Net.loadFromUri(cdn),
          faceapi.nets.faceRecognitionNet.loadFromUri(cdn)
        ]);
        setModelsLoaded(true);
      } catch (e) {
        setError("Gagal memuat modul AI pendeteksi wajah. Cek koneksi internet.");
      }
    };
    loadAI();
  }, []);

  useEffect(() => {
    const session = localStorage.getItem("exam_session");
    if (!session) { nav("/"); return; }
    axios.get(`${API}/exam/seb-status`).then((r) => setSeb(r.data)).catch(() => {});
  }, [nav]);

  const enableCamera = async () => {
    setError("");
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setError("Akses kamera diblokir oleh browser. Pastikan menggunakan HTTPS atau localhost.");
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.onloadedmetadata = async () => {
          try {
            const opts = new faceapi.SsdMobilenetv1Options({ minConfidence: 0.2 });
            const faces = await faceapi.detectAllFaces(videoRef.current, opts).withFaceLandmarks().withFaceDescriptors();
            if (faces.length === 0) {
              stream.getTracks().forEach(t => t.stop());
              setError("Wajah tidak terdeteksi. Pastikan pencahayaan cukup dan wajah terlihat jelas.");
              return;
            }
            if (faces.length > 1) {
              stream.getTracks().forEach(t => t.stop());
              setError("Terdeteksi lebih dari satu orang. Pastikan hanya ada Anda di depan kamera.");
              return;
            }
            localStorage.setItem("baseline_face", JSON.stringify(Array.from(faces[0].descriptor)));
            camRef.current = stream;
            setCamOk(true);
          } catch (e) {
            stream.getTracks().forEach(t => t.stop());
            setError("Error memproses wajah. Coba lagi.");
          }
        };
      }
    } catch {
      setError("Izin kamera ditolak. Aktifkan izin kamera di browser untuk melanjutkan.");
    }
  };

  const enableScreen = async () => {
    setError("");
    setScreenNotice("");
    if (!window.confirm("Sistem akan merekam seluruh layar Anda untuk pengawasan. Anda WAJIB memilih 'Seluruh Layar' (Entire Screen) pada pop-up berikutnya. Izinkan merekam layar?")) {
      return;
    }

    if (!navigator.mediaDevices || !navigator.mediaDevices.getDisplayMedia) {
      setError("Fitur berbagi layar tidak didukung di browser atau perangkat ini.");
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getDisplayMedia({ video: { displaySurface: "monitor" } });
      const track = stream.getVideoTracks()[0];
      if (!track) {
        stream.getTracks().forEach((mediaTrack) => mediaTrack.stop());
        setError("Browser tidak memberikan track video untuk berbagi layar. Coba lagi.");
        return;
      }
      const settings = track.getSettings();

      if (settings.displaySurface && settings.displaySurface !== "monitor") {
        stream.getTracks().forEach((mediaTrack) => mediaTrack.stop());
        const selectedSurface = {
          browser: "tab browser",
          window: "window aplikasi",
        }[settings.displaySurface] || settings.displaySurface;
        setError(`Browser melaporkan sumber berbagi layar sebagai ${selectedSurface}. Pilih 'Seluruh Layar' (Entire Screen), bukan Tab atau Window.`);
        return;
      }

      if (window.screen && window.screen.isExtended) {
        stream.getTracks().forEach((mediaTrack) => mediaTrack.stop());
        setError("Kecurangan Terdeteksi: Penggunaan monitor ganda (Extended Display) tidak diizinkan. Cabut monitor tambahan Anda.");
        return;
      }

      screenRef.current = stream;
      setScreenOk(true);
      if (!settings.displaySurface) {
        setScreenNotice("Browser tidak memberi informasi jenis layar. Pastikan pilihan di dialog berbagi layar adalah Seluruh Layar / Entire Screen.");
      }
      track.addEventListener("ended", () => {
        screenRef.current = null;
        setScreenOk(false);
        setScreenNotice("");
      });
    } catch {
      setError("Izin berbagi layar ditolak atau dibatalkan. Pilih 'Seluruh Layar' saat diminta.");
    }
  };

  const proceed = () => {
    setStreams(camRef.current, screenRef.current);
    nav("/exam");
  };

  const sebBlocked = seb.require_seb && !seb.seb_detected;
  const ready = camOk && (isMobile ? true : screenOk) && !sebBlocked;

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
          <span className="font-semibold tracking-tight">INTERNXAM</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-semibold tracking-tight mb-2">Pemeriksaan Perangkat</h1>
        <p className="text-zinc-500 mb-8">Selama ujian, kamera dan layar kamu ditampilkan sebagai bagian dari pengawasan. <span className="font-medium text-zinc-700">Tidak ada rekaman yang disimpan.</span></p>

        <div className="space-y-3" data-testid="preflight-checklist">
          {!modelsLoaded ? (
            <div className="flex items-center gap-3 p-5 border border-amber-200 bg-amber-50 rounded-lg text-amber-700">
              <HourglassHigh size={24} className="animate-spin" />
              <span className="font-medium">Memuat modul AI Anti-Cheat (Face Recognition)...</span>
            </div>
          ) : (
            <>
              <Item ok={camOk} icon={Camera} title="Kamera & Verifikasi Wajah" desc="Wajah Anda akan dipindai sebagai baseline keamanan."
                action={enableCamera} actionLabel="Verifikasi Wajah" testid="enable-camera-btn" />
              {!isMobile && (
                <Item ok={screenOk} icon={Monitor} title="Berbagi Layar Penuh" desc="Pilih 'Seluruh Layar / Entire Screen' saat diminta."
                  action={enableScreen} actionLabel="Bagikan Layar" testid="enable-screen-btn" />
              )}
              {screenNotice && !isMobile && (
                <p className="ml-10 text-sm text-amber-700" role="status">{screenNotice}</p>
              )}
            </>
          )}
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
            <ul className="list-disc pl-4 space-y-0.5 mt-1">
              <li>Layar ujian harus berukuran penuh (Fullscreen).</li>
              <li>Sistem memantau pergerakan wajah secara real-time.</li>
              <li>Menutup kamera atau keluar dari halaman ujian akan dikenakan <strong>penalti beruntun</strong>.</li>
              <li>3 pelanggaran = Ujian ditutup otomatis.</li>
            </ul>
          </div>
        </div>

        {error && <p data-testid="preflight-error" className="mt-4 text-sm text-red-600">{error}</p>}

        <div className="mt-8 flex flex-col sm:flex-row items-center gap-4">
          <Button data-testid="proceed-to-exam-btn" disabled={!ready} onClick={proceed}
            className="w-full sm:flex-1 h-12 text-base bg-[#0055FF] hover:bg-[#0044CC] text-white disabled:opacity-40">
            Mulai Ujian Sekarang
          </Button>
          {sebBlocked && (
            <a href="https://safeexambrowser.org/download_en.html" target="_blank" rel="noreferrer" 
              className="text-sm font-medium text-[#0055FF] hover:underline shrink-0 px-2 text-center">
              Unduh / Install SEB
            </a>
          )}
        </div>
      </div>
    </div>
  );
}
