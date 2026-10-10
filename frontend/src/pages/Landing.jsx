import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { API, errDetail } from "@/lib/api";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { ShieldCheck } from "@phosphor-icons/react";

const HERO = "https://images.unsplash.com/photo-1516534775068-ba3e7458af70?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA1ODR8MHwxfHNlYXJjaHwzfHxzdHVkZW50JTIwdGFraW5nJTIwb25saW5lJTIwZXhhbSUyMGZvY3VzZWR8ZW58MHx8fHwxNzg3MTEzNjkxfDA&ixlib=rb-4.1.0&q=85";

export default function Landing() {
  const nav = useNavigate();
  const [form, setForm] = useState({ name: "", school: "", class_name: "", token: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    if (!form.name.trim() || !form.school.trim() || !form.class_name.trim() || form.token.trim().length !== 8) {
      setError("Lengkapi semua data. Token harus 8 karakter.");
      return;
    }
    setLoading(true);
    try {
      const { data } = await axios.post(`${API}/exam/start`, {
        ...form,
        token: form.token.trim().toUpperCase(),
      });
      localStorage.setItem("exam_session", JSON.stringify({
        participant_id: data.participant_id,
        token: form.token.trim().toUpperCase(),
        name: form.name.trim(),
      }));
      nav("/preparation");
    } catch (err) {
      setError(errDetail(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen grid grid-cols-1 lg:grid-cols-2">
      <div className="flex flex-col justify-center px-8 sm:px-16 xl:px-24 py-12 bg-white">
        <div className="flex items-center gap-2 mb-12">
          <ShieldCheck size={28} weight="fill" className="text-[#0055FF]" />
          <span className="font-semibold text-lg tracking-tight">INTERNXAM</span>
        </div>
        <h1 className="text-4xl sm:text-5xl tracking-tight font-semibold text-zinc-900 mb-3">
          Portal Ujian & Asesmen PKL
        </h1>
        <p className="text-zinc-500 mb-10 max-w-md">
          Masukkan data diri dan token ujian yang diberikan panitia. Sesi ini diawasi — pastikan kamera dan layar siap dibagikan.
        </p>
        <div className="max-w-md border border-amber-200 bg-amber-50 p-4 mb-6 text-sm text-amber-900" role="note">
          Sesi berisi tes kompetensi dan asesmen situasi PKL versi pilot. Jawaban skenario menjadi bahan diskusi, bukan diagnosis atau satu-satunya dasar keputusan. Jawaban tersimpan dan dapat dilihat panitia; saat ini sistem tidak menghapus hasil secara otomatis. Tanyakan kepada panitia tentang masa penyimpanan data.
        </div>
        <form onSubmit={submit} className="space-y-5 max-w-md" data-testid="participant-entry-form">
          <div className="space-y-1.5">
            <Label htmlFor="name">Nama Lengkap</Label>
            <Input id="name" data-testid="input-name" className="h-12 text-lg" value={form.name} onChange={set("name")} placeholder="Nama lengkap kamu" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <Label htmlFor="school">Asal Sekolah</Label>
              <Input id="school" data-testid="input-school" className="h-12" value={form.school} onChange={set("school")} placeholder="SMK ..." />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="class">Kelas</Label>
              <Input id="class" data-testid="input-class" className="h-12" value={form.class_name} onChange={set("class_name")} placeholder="XII TKJ 1" />
            </div>
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="token">Token Ujian</Label>
            <Input id="token" data-testid="input-token" maxLength={8}
              className="h-12 font-mono text-xl tracking-[0.4em] uppercase"
              value={form.token} onChange={set("token")} placeholder="XXXXXXXX" />
          </div>
          {error && <p data-testid="entry-error" className="text-sm text-red-600">{error}</p>}
          <Button type="submit" data-testid="start-exam-btn" disabled={loading}
            className="h-12 w-full text-base bg-zinc-900 hover:bg-zinc-800 text-white">
            {loading ? "Memvalidasi token..." : "Masuk Ujian"}
          </Button>
        </form>
        <a href="/admin/login" data-testid="admin-login-link" className="mt-12 text-xs text-zinc-400 hover:text-zinc-600 w-fit">
          Masuk sebagai admin →
        </a>
        <div className="mt-auto pt-16 flex items-center gap-2 text-sm text-zinc-500">
          <span>Powered by</span>
          <img src="/AXELBIT.png" alt="Axelbit" className="h-8 object-contain" />
        </div>
      </div>
      <div className="hidden lg:block relative">
        <img src={HERO} alt="Siswa fokus mengerjakan ujian" className="absolute inset-0 w-full h-full object-cover" />
        <div className="absolute inset-0 bg-black/40" />
        <div className="absolute bottom-12 left-12 right-12 text-white">
          <p className="text-sm uppercase tracking-widest mb-2 opacity-80">Sesi Diawasi</p>
          <p className="text-2xl font-medium max-w-md">Kerjakan dengan jujur. Sistem mencatat setiap pelanggaran secara otomatis.</p>
        </div>
      </div>
    </div>
  );
}
