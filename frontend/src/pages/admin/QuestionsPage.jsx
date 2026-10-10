import { useEffect, useState } from "react";
import { api, errDetail } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner";
import { PencilSimple, Trash } from "@phosphor-icons/react";

const empty = { text: "", options: ["", "", "", ""], correct_index: 0, category: "Jaringan Dasar", difficulty: "sedang" };

export default function QuestionsPage() {
  const [questions, setQuestions] = useState([]);
  const [scenarioAssessment, setScenarioAssessment] = useState({ items: [], indicators: [] });
  const [form, setForm] = useState(empty);
  const [editId, setEditId] = useState(null);
  const [open, setOpen] = useState(false);

  const load = () => {
    api.get("/admin/questions").then((r) => setQuestions(r.data));
    api.get("/admin/scenario-items").then((r) => setScenarioAssessment(r.data));
  };
  useEffect(load, []);

  const importExcel = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const fd = new FormData();
    fd.append("file", file);
    try {
      const { data } = await api.post("/admin/questions/import", fd);
      toast.success(`${data.count} soal berhasil diimpor`);
      load();
    } catch (err) { toast.error(errDetail(err)); }
    e.target.value = null;
  };

  const save = async () => {
    if (!form.text.trim() || form.options.some((o) => !o.trim())) {
      toast.error("Lengkapi pertanyaan dan semua opsi");
      return;
    }
    try {
      if (editId) await api.put(`/admin/questions/${editId}`, form);
      else await api.post("/admin/questions", form);
      toast.success(editId ? "Soal diperbarui" : "Soal ditambahkan");
      setOpen(false);
      setForm(empty);
      setEditId(null);
      load();
    } catch (e) { toast.error(errDetail(e)); }
  };

  const del = async (id) => {
    await api.delete(`/admin/questions/${id}`);
    toast.success("Soal dihapus");
    load();
  };

  const openEdit = (q) => {
    setForm({ text: q.text, options: q.options, correct_index: q.correct_index, category: q.category, difficulty: q.difficulty });
    setEditId(q.id);
    setOpen(true);
  };

  return (
    <div data-testid="questions-page">
      <h1 className="text-2xl font-semibold tracking-tight mb-6">Bank Soal</h1>
      <Tabs defaultValue="tkj">
        <TabsList>
          <TabsTrigger value="tkj" data-testid="tab-tkj">Soal TKJ ({questions.length})</TabsTrigger>
          <TabsTrigger value="scenario" data-testid="tab-scenario">Asesmen Skenario ({scenarioAssessment.items.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="tkj" className="mt-4">
          <div className="mb-4">
            <Dialog open={open} onOpenChange={(v) => { setOpen(v); if (!v) { setForm(empty); setEditId(null); } }}>
              <DialogTrigger asChild>
                <Button data-testid="add-question-btn" className="bg-zinc-900 text-white hover:bg-zinc-800">+ Tambah Soal</Button>
              </DialogTrigger>
              <Button asChild variant="outline" className="ml-2 cursor-pointer">
                <label>
                  Import Excel/CSV
                  <input type="file" accept=".csv, .xlsx" className="hidden" onChange={importExcel} />
                </label>
              </Button>
              <DialogContent className="max-w-2xl">
                <DialogHeader><DialogTitle>{editId ? "Edit Soal" : "Tambah Soal TKJ"}</DialogTitle></DialogHeader>
                <div className="space-y-4">
                  <div className="space-y-1.5">
                    <Label>Pertanyaan</Label>
                    <Textarea data-testid="question-text-input" value={form.text} onChange={(e) => setForm({ ...form, text: e.target.value })} rows={3} />
                  </div>
                  {form.options.map((o, i) => (
                    <div key={i} className="flex items-center gap-3">
                      <input type="radio" name="correct" checked={form.correct_index === i}
                        onChange={() => setForm({ ...form, correct_index: i })}
                        className="accent-emerald-600 w-4 h-4" title="Tandai jawaban benar" />
                      <Input data-testid={`option-input-${i}`} value={o} placeholder={`Opsi ${String.fromCharCode(65 + i)}`}
                        onChange={(e) => setForm({ ...form, options: form.options.map((x, xi) => (xi === i ? e.target.value : x)) })} />
                    </div>
                  ))}
                  <p className="text-xs text-zinc-400">Pilih radio di kiri untuk menandai jawaban benar.</p>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-1.5">
                      <Label>Kategori</Label>
                      <Input data-testid="category-input" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} />
                    </div>
                    <div className="space-y-1.5">
                      <Label>Tingkat Kesulitan</Label>
                      <Select value={form.difficulty} onValueChange={(v) => setForm({ ...form, difficulty: v })}>
                        <SelectTrigger data-testid="difficulty-select"><SelectValue /></SelectTrigger>
                        <SelectContent>
                          <SelectItem value="mudah">Mudah</SelectItem>
                          <SelectItem value="sedang">Sedang</SelectItem>
                          <SelectItem value="sulit">Sulit</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <Button onClick={save} data-testid="save-question-btn" className="w-full bg-zinc-900 text-white hover:bg-zinc-800">Simpan</Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
          <div className="bg-white border border-zinc-200 shadow-sm">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-zinc-200 text-left text-xs uppercase tracking-wider text-zinc-400">
                  <th className="p-3 w-8">#</th><th className="p-3">Pertanyaan</th><th className="p-3">Kategori</th><th className="p-3">Level</th><th className="p-3 w-24">Aksi</th>
                </tr>
              </thead>
              <tbody data-testid="questions-table-body">
                {questions.map((q, i) => (
                  <tr key={q.id} className="border-b border-zinc-100 hover:bg-zinc-50">
                    <td className="p-3 text-zinc-400">{i + 1}</td>
                    <td className="p-3 max-w-md"><p className="line-clamp-2">{q.text}</p></td>
                    <td className="p-3 text-zinc-500">{q.category}</td>
                    <td className="p-3 text-zinc-500">{q.difficulty}</td>
                    <td className="p-3">
                      <div className="flex gap-1">
                        <button onClick={() => openEdit(q)} data-testid={`edit-q-${i}`} className="p-1.5 hover:bg-zinc-100"><PencilSimple size={16} /></button>
                        <button onClick={() => del(q.id)} data-testid={`delete-q-${i}`} className="p-1.5 hover:bg-red-50 text-red-600"><Trash size={16} /></button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </TabsContent>

        <TabsContent value="scenario" className="mt-4">
          <div className="border border-amber-200 bg-amber-50 p-4 mb-4 text-sm text-amber-900" data-testid="scenario-pilot-notice">
            <p className="font-semibold">Versi pilot · {scenarioAssessment.version}</p>
            <p>{scenarioAssessment.disclaimer}</p>
            <p className="mt-1">Rubrik ditampilkan untuk review panitia/pembimbing; skor bukan ambang lulus dan bukan diagnosis.</p>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4" data-testid="scenario-items-list">
            {scenarioAssessment.items.map((item, itemIndex) => {
              const indicator = scenarioAssessment.indicators.find((entry) => entry.id === item.indicator);
              return (
                <div key={item.id} className="bg-white border border-zinc-200 p-4 shadow-sm">
                  <p className="text-xs uppercase tracking-wider text-zinc-400 mb-1">Skenario {itemIndex + 1} · {indicator?.label}</p>
                  <p className="font-medium mb-3">{item.situation}</p>
                  <div className="space-y-3">
                    {item.options.map((option, optionIndex) => (
                      <div key={optionIndex} className="border-t border-zinc-100 pt-2">
                        <p className="text-sm">{option.text}</p>
                        <p className="text-xs text-zinc-500 mt-1">
                          Rubrik {option.score}/3 · {option.rationale}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
