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
  const [discItems, setDiscItems] = useState([]);
  const [form, setForm] = useState(empty);
  const [editId, setEditId] = useState(null);
  const [open, setOpen] = useState(false);

  const load = () => {
    api.get("/admin/questions").then((r) => setQuestions(r.data));
    api.get("/admin/disc-items").then((r) => setDiscItems(r.data));
  };
  useEffect(load, []);

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
          <TabsTrigger value="disc" data-testid="tab-disc">Item DISC ({discItems.length} grup)</TabsTrigger>
        </TabsList>

        <TabsContent value="tkj" className="mt-4">
          <div className="mb-4">
            <Dialog open={open} onOpenChange={(v) => { setOpen(v); if (!v) { setForm(empty); setEditId(null); } }}>
              <DialogTrigger asChild>
                <Button data-testid="add-question-btn" className="bg-zinc-900 text-white hover:bg-zinc-800">+ Tambah Soal</Button>
              </DialogTrigger>
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

        <TabsContent value="disc" className="mt-4">
          <p className="text-sm text-zinc-500 mb-4">24 grup forced-choice. Setiap pernyataan terpetakan ke dimensi D / I / S / C. Jika sekolah memiliki instrumen berlisensi, item dapat diganti.</p>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4" data-testid="disc-items-list">
            {discItems.map((item) => (
              <div key={item.group_index} className="bg-white border border-zinc-200 p-4 shadow-sm">
                <p className="text-xs uppercase tracking-wider text-zinc-400 mb-2">Grup {item.group_index + 1}</p>
                {item.statements.map((s, si) => (
                  <div key={si} className="flex items-center justify-between py-1 border-b border-zinc-50 last:border-0">
                    <span className="text-sm">{s.text}</span>
                    <span className="text-xs font-mono font-semibold text-zinc-400 ml-2">{s.dimension}</span>
                  </div>
                ))}
              </div>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
