import { Button } from "@/components/ui/button";

export default function WorkDiscAssessment({
  items,
  itemIndex,
  answers,
  saveStatus,
  onAnswer,
  onPrevious,
  onNext,
  onSubmit,
}) {
  const item = items[itemIndex];
  const answeredCount = items.filter((question) =>
    Number.isInteger(answers[question.id])).length;

  if (!item) {
    return (
      <div className="rounded-3xl border border-white/50 bg-white/70 p-8 text-center text-slate-500">
        Memuat asesmen situasi kerja...
      </div>
    );
  }

  return (
    <div data-testid="work-disc-question-area" className="rounded-3xl border border-white/50 bg-white/70 p-7 shadow-xl backdrop-blur-xl md:p-9">
      <p className="mb-2 text-xs font-semibold uppercase tracking-widest text-indigo-600">
        Situasi Kerja · Pertanyaan {itemIndex + 1} dari {items.length}
      </p>
      <h2 className="mb-3 text-xl font-semibold leading-relaxed text-slate-800 md:text-2xl">
        {item.situation}
      </h2>
      <p className="mb-6 text-sm text-slate-500">
        Pilih respons yang paling menggambarkan tindakan yang biasanya kamu ambil. Tidak ada jawaban benar atau salah.
      </p>

      <div className="space-y-3">
        {item.options.map((option, optionIndex) => {
          const selected = answers[item.id] === optionIndex;
          return (
            <button
              key={`${item.id}-${optionIndex}`}
              type="button"
              data-testid={`work-disc-option-${optionIndex}`}
              aria-pressed={selected}
              onClick={() => onAnswer(item.id, optionIndex)}
              className={`flex w-full items-start gap-3 rounded-2xl border p-4 text-left transition-colors ${
                selected
                  ? "border-indigo-400 bg-indigo-50 text-indigo-950 ring-2 ring-indigo-100"
                  : "border-slate-200 bg-white hover:border-indigo-200 hover:bg-indigo-50/50"
              }`}
            >
              <span className={`mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full border ${
                selected ? "border-indigo-600" : "border-slate-300"
              }`}>
                {selected && <span className="h-2.5 w-2.5 rounded-full bg-indigo-600" />}
              </span>
              <span className="text-sm leading-relaxed">{option}</span>
            </button>
          );
        })}
      </div>

      <div className="mt-6 flex items-center justify-between text-xs text-slate-500">
        <span>{answeredCount}/{items.length} terjawab</span>
        <span data-testid="work-disc-save-status">
          {saveStatus === "saving" ? "Menyimpan..." : saveStatus === "saved" ? "Tersimpan" : saveStatus === "offline" ? "Offline — menunggu koneksi" : saveStatus === "error" ? "Gagal menyimpan" : ""}
        </span>
      </div>

      <div className="mt-8 flex justify-between gap-3">
        <Button variant="outline" data-testid="work-disc-prev-btn" disabled={itemIndex === 0} onClick={onPrevious}>
          ← Sebelumnya
        </Button>
        {itemIndex < items.length - 1 ? (
          <Button data-testid="work-disc-next-btn" onClick={onNext} className="bg-slate-900 text-white hover:bg-slate-800">
            Berikutnya →
          </Button>
        ) : (
          <Button
            data-testid="submit-work-disc-btn"
            onClick={onSubmit}
            disabled={answeredCount !== items.length}
            className="bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50"
          >
            Selesaikan DISC ({answeredCount}/{items.length})
          </Button>
        )}
      </div>
      {itemIndex === items.length - 1 && answeredCount !== items.length && (
        <p className="mt-3 text-right text-xs text-amber-700">
          Jawab semua pertanyaan untuk menyelesaikan sebelum waktu habis.
        </p>
      )}
    </div>
  );
}
