import { Button } from "@/components/ui/button";

export default function ScenarioAssessment({
  scenario,
  scenarioIdx,
  scenarioCount,
  selectedIndex,
  answeredCount,
  saveStatus,
  onAnswer,
  onPrevious,
  onNext,
  onSubmit,
}) {
  if (!scenario) return null;

  return (
    <div data-testid="scenario-question-area" className="bg-white/70 backdrop-blur-xl border border-white/60 shadow-xl rounded-3xl p-8 md:p-10">
      <p className="text-xs uppercase tracking-widest text-indigo-500 font-semibold mb-2">
        Asesmen Situasi PKL · Skenario {scenarioIdx + 1} dari {scenarioCount}
      </p>
      <h2 className="text-xl sm:text-2xl font-medium text-slate-800 leading-relaxed mb-8">
        {scenario.situation}
      </h2>
      <p className="text-sm text-slate-500 mb-4">
        Pilih respons yang paling mungkin kamu lakukan. Tidak ada nilai lulus/gagal; jawaban ini bukan satu-satunya dasar keputusan.
      </p>
      <div className="space-y-3">
        {scenario.options.map((option, optionIdx) => (
          <label key={optionIdx} data-testid={`scenario-option-${optionIdx}`}
            className={`flex items-start gap-4 border-2 p-5 rounded-2xl cursor-pointer transition-all ${
              selectedIndex === optionIdx
                ? "border-indigo-500 bg-indigo-50/80 shadow-md"
                : "border-white/70 bg-white/60 hover:bg-white hover:border-indigo-200"
            }`}>
            <input type="radio" name={`scenario-${scenario.id}`}
              checked={selectedIndex === optionIdx}
              onChange={() => onAnswer(scenario.id, optionIdx)}
              className="mt-1 w-5 h-5 accent-indigo-600" />
            <span className="text-sm md:text-base text-left text-slate-700">{option}</span>
          </label>
        ))}
      </div>
      <p className="text-xs text-slate-500 mt-5">
        Versi pilot: hasil hanya menjadi bahan diskusi dengan panitia/pembimbing, bukan diagnosis atau satu-satunya dasar keputusan.
      </p>
      <div className="flex justify-between mt-10">
        <Button variant="outline" data-testid="scenario-prev-btn" disabled={scenarioIdx === 0}
          onClick={onPrevious} className="rounded-full px-6">
          ← Sebelumnya
        </Button>
        {scenarioIdx < scenarioCount - 1 ? (
          <Button data-testid="scenario-next-btn" onClick={onNext}
            className="bg-slate-900 text-white rounded-full px-6">
            Berikutnya →
          </Button>
        ) : (
          <Button data-testid="submit-scenario-btn" onClick={onSubmit}
            disabled={answeredCount < scenarioCount || saveStatus === "saving" || saveStatus === "offline"}
            className="bg-gradient-to-r from-indigo-600 to-blue-600 text-white rounded-full px-6 disabled:opacity-50">
            Selesaikan Asesmen ({answeredCount}/{scenarioCount})
          </Button>
        )}
      </div>
    </div>
  );
}
