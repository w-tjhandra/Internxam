import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ShieldCheck, WarningCircle, Camera, Monitor, Prohibit } from "@phosphor-icons/react";

export default function Preparation() {
  const nav = useNavigate();

  useEffect(() => {
    const session = localStorage.getItem("exam_session");
    if (!session) {
      nav("/");
    }
  }, [nav]);

  const proceed = () => {
    nav("/preflight");
  };

  return (
    <div className="min-h-screen bg-zinc-50 flex flex-col items-center justify-center px-6 py-12">
      <div className="w-full max-w-2xl bg-white border border-zinc-200 p-8 sm:p-12 shadow-sm rounded-lg">
        <div className="flex items-center gap-2 mb-8 justify-center">
          <ShieldCheck size={32} weight="fill" className="text-[#0055FF]" />
          <span className="font-semibold text-xl tracking-tight">INTERNXAM</span>
        </div>

        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-100 text-red-700 text-sm font-medium mb-4 uppercase tracking-widest">
            <WarningCircle size={18} weight="bold" /> Sesi Diawasi
          </div>
          <h1 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4 text-zinc-900">
            Peraturan Ujian Online
          </h1>
          <p className="text-lg text-zinc-600 max-w-lg mx-auto">
            Kerjakan dengan jujur. Sistem mencatat setiap pelanggaran secara otomatis.
          </p>
        </div>

        <div className="space-y-6 mb-10 text-zinc-700">
          <div className="flex gap-4 items-start p-4 bg-zinc-50 border border-zinc-100 rounded-lg">
            <Monitor size={28} className="text-[#0055FF] shrink-0 mt-1" />
            <div>
              <h3 className="font-semibold text-zinc-900 text-lg mb-1">Mode Layar Penuh (Fullscreen)</h3>
              <p>Khusus pengguna Laptop/PC, ujian hanya dapat dikerjakan dalam mode layar penuh. Keluar dari mode layar penuh akan dicatat sebagai pelanggaran.</p>
            </div>
          </div>
          
          <div className="flex gap-4 items-start p-4 bg-zinc-50 border border-zinc-100 rounded-lg">
            <Prohibit size={28} className="text-red-500 shrink-0 mt-1" />
            <div>
              <h3 className="font-semibold text-zinc-900 text-lg mb-1">Dilarang Pindah Tab/Aplikasi</h3>
              <p>Sistem akan mendeteksi jika Anda membuka tab baru, me-minimize browser, atau membuka aplikasi lain. <strong>Tiga (3) kali pelanggaran akan membuat ujian ditutup otomatis.</strong></p>
            </div>
          </div>

          <div className="flex gap-4 items-start p-4 bg-zinc-50 border border-zinc-100 rounded-lg">
            <Camera size={28} className="text-emerald-600 shrink-0 mt-1" />
            <div>
              <h3 className="font-semibold text-zinc-900 text-lg mb-1">Pengawasan Kamera & Layar</h3>
              <p>Kamera dan layar Anda akan dipantau selama ujian berlangsung. Pastikan wajah Anda terlihat jelas dan ikuti instruksi sistem.</p>
            </div>
          </div>
        </div>

        <div className="bg-blue-50 border border-blue-100 p-5 rounded-lg mb-10 text-blue-900 text-sm">
          <strong>Penting:</strong> Pastikan Anda menggunakan koneksi internet yang stabil dan berada di tempat yang kondusif sebelum melanjutkan.
        </div>

        <Button 
          data-testid="proceed-to-preflight-btn" 
          onClick={proceed}
          className="h-14 w-full text-lg bg-[#0055FF] hover:bg-[#0044CC] text-white shadow-md">
          Saya Mengerti, Lanjut Pemeriksaan Perangkat
        </Button>
      </div>
      
      <div className="mt-8 flex items-center gap-2 text-sm text-zinc-400">
        <span>Powered by</span>
        <img src="/AXELBIT.png" alt="Axelbit" className="h-6 object-contain opacity-50 grayscale" />
      </div>
    </div>
  );
}
