export default function Question({
  questions,
  currentIndex,
  selectedChoice,
  onChoose,
  onNext,
  onPrevious,
}) {
  const current = questions[currentIndex];
  const progress = ((currentIndex) / questions.length) * 100;
  const isLast = currentIndex + 1 === questions.length;

  return (
    <div className="min-h-dvh bg-[#f6f7f9] text-slate-950">
      <div className="w-full px-5 pt-6">
        <div className="max-w-md mx-auto">
          <div className="flex items-center justify-between text-sm text-slate-500 mb-2">
            <span>
              {currentIndex + 1} / {questions.length}
            </span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className="w-full h-2 bg-black/10 rounded-full overflow-hidden">
            <div
              className="h-full bg-[color:var(--key-primary)] rounded-full transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </div>

      <div className="flex-1 flex flex-col items-stretch px-5 py-6 pb-28">
        <div className="max-w-md w-full mx-auto flex flex-col gap-4">
          <div className="rounded-3xl bg-white p-6 shadow-sm border border-black/5">
            <p className="text-sm text-slate-500 font-semibold mb-3 tracking-wide uppercase">
              Situation {currentIndex + 1}
            </p>
            <h2 className="text-lg sm:text-xl font-bold leading-relaxed text-slate-900">
              {current.text}
            </h2>
          </div>

          <div className="flex flex-col gap-3">
            <button
              onClick={() => onChoose("A")}
              className={`w-full text-left px-6 py-5 rounded-3xl bg-white border text-slate-900 font-medium text-base leading-relaxed transition-all duration-150 cursor-pointer active:scale-[0.99] ${
                selectedChoice === "A"
                  ? "border-2 border-[color:var(--key-primary)] bg-[color:var(--key-primary)]/6 ring-2 ring-[color:var(--key-primary)]/15"
                  : "border-black/10 hover:border-[color:var(--key-primary)]"
              }`}
            >
              {current.optionA.text}
            </button>
            <button
              onClick={() => onChoose("B")}
              className={`w-full text-left px-6 py-5 rounded-3xl bg-white border text-slate-900 font-medium text-base leading-relaxed transition-all duration-150 cursor-pointer active:scale-[0.99] ${
                selectedChoice === "B"
                  ? "border-2 border-[color:var(--key-primary)] bg-[color:var(--key-primary)]/6 ring-2 ring-[color:var(--key-primary)]/15"
                  : "border-black/10 hover:border-[color:var(--key-primary)]"
              }`}
            >
              {current.optionB.text}
            </button>
          </div>
        </div>
      </div>

      <div className="fixed bottom-0 left-0 right-0 bg-[#f6f7f9] border-t border-black/10">
        <div className="max-w-md mx-auto px-5 py-4 flex gap-3">
          <button
            onClick={onPrevious}
            className="flex-1 py-4 rounded-3xl font-bold text-lg transition-all duration-150 bg-white border border-black/10 text-slate-900 hover:border-black/20 cursor-pointer"
          >
            이전
          </button>
          <button
            onClick={onNext}
            disabled={!selectedChoice}
            className={`flex-1 py-4 rounded-3xl font-bold text-lg transition-all duration-150 ${
              selectedChoice
                ? "bg-[color:var(--key-primary)] text-white hover:opacity-90 cursor-pointer shadow-sm"
                : "bg-slate-200 text-slate-400 cursor-not-allowed"
            }`}
          >
            {isLast ? "결과 보기" : "다음"}
          </button>
        </div>
      </div>
    </div>
  );
}
