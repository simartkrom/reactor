function MainCtaArrowIcon({ active }) {
  return (
    <span
      className={active ? "text-white/90" : "text-slate-400"}
      aria-hidden
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth={2.25}
        strokeLinecap="round"
        strokeLinejoin="round"
        className="w-[1.25rem] h-[1.25rem] shrink-0"
      >
        <path d="M5 12h14" />
        <path d="M13 5l7 7-7 7" />
      </svg>
    </span>
  );
}

export default function Main({
  onStart,
  onGoPromptSet,
  onGoCanvasForm,
  onGoAiColleagueForm,
  sessionCode,
  setSessionCode,
  onValidateSession,
  isSessionValid,
  isValidatingSession,
  sessionError,
}) {
  const isSessionLocked = Boolean(isSessionValid && sessionCode);

  return (
    <div className="min-h-dvh bg-[#f6f7f9] text-slate-950">
      <div className="mx-auto w-full max-w-md px-5 pt-10 pb-8 flex flex-col gap-8">
        <header className="flex flex-col gap-3 text-center">
          <div className="flex justify-center">
            <div className="inline-flex items-center justify-center rounded-full bg-[color:var(--key-primary)] px-4 py-2 text-white font-extrabold text-sm sm:text-base shadow-sm">
            AI 시대 나의 캐릭터는?
            </div>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight leading-snug">
            THE TEMPO
            <br />
            <span className="text-[color:var(--key-primary)]">
              스킬 밸런스 게임
            </span>
          </h1>
          <p className="text-slate-500 text-base sm:text-lg leading-relaxed">
            <span className="font-bold text-slate-800">
              일하는 방식이 달라진 2030년,
              <br />
              당신의 템포는?
            </span>
          </p>
          <div className="w-full mt-2 -mx-0.5 sm:mx-0">
            <div className="rounded-3xl overflow-hidden border border-black/10 shadow-[0_12px_40px_-12px_rgba(15,23,42,0.35)] ring-1 ring-white/60">
              <img
                src="/main-hero-characters-11.png"
                alt="2030년 AI 시대, 열한 가지 캐릭터가 함께 협업하며 일하는 모습"
                className="w-full h-auto block"
                width={1376}
                height={768}
                loading="eager"
                decoding="async"
              />
            </div>
          </div>
          <p className="text-slate-500 text-base sm:text-lg leading-relaxed mt-4">
            AI 기술의 거대한 물결 속에서
            <br />
            나만의 리듬을 찾아보세요.
            <br />
            가장 나다운 일하는 방식을 발견하는
            <br />
            흥미진진한 밸런스 게임이 시작됩니다.
          </p>
        </header>

        <div className="w-full flex flex-col gap-4">
          <div className="w-full rounded-3xl bg-white p-5 shadow-sm border border-black/5">
            <p className="text-sm font-semibold text-slate-500 mb-2">
              차수 코드
            </p>
            <div className="flex gap-2 items-stretch">
              <input
                type="text"
                value={sessionCode}
                onChange={(e) => setSessionCode(e.target.value.toUpperCase())}
                placeholder="예: SK001"
                inputMode="text"
                className="min-w-0 flex-1 rounded-2xl bg-[#f6f7f9] border border-black/10 px-4 py-3 text-base text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-[color:var(--key-primary)] focus:ring-2 focus:ring-[color:var(--key-primary)]/15"
              />
              <button
                type="button"
                onClick={onValidateSession}
                disabled={isValidatingSession || isSessionLocked}
                className={`shrink-0 px-3 sm:px-4 rounded-2xl text-base font-semibold whitespace-nowrap transition-colors ${
                  isValidatingSession
                    ? "bg-slate-200 text-slate-400 cursor-wait"
                    : isSessionLocked
                      ? "bg-slate-200 text-slate-400 cursor-not-allowed"
                      : "bg-[color:var(--key-primary)] text-white hover:opacity-90"
                }`}
              >
                {isValidatingSession ? "확인 중" : "확인"}
              </button>
            </div>
            <div className="min-h-[1.25rem] mt-2 text-sm">
              {sessionError && (
                <p className="text-[color:var(--key-danger)]">{sessionError}</p>
              )}
              {!sessionError && isSessionValid && sessionCode && (
                <p className="text-slate-600">
                  유효한 차수 코드입니다. 이 코드로 결과가 저장됩니다.
                </p>
              )}
              {!sessionError && !isSessionValid && sessionCode && (
                <p className="text-slate-500">
                  코드를 입력한 뒤 확인을 눌러 주세요.
                </p>
              )}
            </div>
          </div>

          <button
            type="button"
            onClick={onStart}
            disabled={!isSessionValid}
            className={`w-full py-4 px-5 rounded-3xl font-extrabold text-base transition-[transform,box-shadow,filter] duration-200 flex items-center justify-between ${
              isSessionValid
                ? "main-cta-reveal main-cta-reveal-d0 cursor-pointer bg-gradient-to-r from-[#DC2626] to-[#FB7185] text-white hover:opacity-95 shadow-[0_12px_26px_-12px_rgba(220,38,38,0.75)] border border-rose-400/45 active:scale-[0.99]"
                : "bg-slate-200 text-slate-400 cursor-not-allowed border border-slate-200/80"
            }`}
          >
            <span>캐릭터 확인</span>
            <MainCtaArrowIcon active={isSessionValid} />
          </button>

          <button
            type="button"
            onClick={onGoPromptSet}
            disabled={!isSessionValid}
            className={`w-full py-4 px-5 rounded-3xl font-extrabold text-base transition-[transform,box-shadow,filter] duration-200 flex items-center justify-between ${
              isSessionValid
                ? "main-cta-reveal main-cta-reveal-d1 cursor-pointer bg-gradient-to-r from-[#7C3AED] to-[#DB2777] text-white border border-fuchsia-400/40 hover:opacity-95 shadow-[0_12px_26px_-12px_rgba(124,58,237,0.65)] active:scale-[0.99]"
                : "bg-slate-200 text-slate-400 cursor-not-allowed border border-slate-200/80"
            }`}
          >
            <span>AI Native 이미지 생성</span>
            <MainCtaArrowIcon active={isSessionValid} />
          </button>

          <button
            type="button"
            onClick={onGoCanvasForm}
            disabled={!isSessionValid}
            className={`w-full py-4 px-5 rounded-3xl font-extrabold text-base transition-[transform,box-shadow,filter] duration-200 flex items-center justify-between ${
              isSessionValid
                ? "main-cta-reveal main-cta-reveal-d2 cursor-pointer bg-gradient-to-r from-[#0D9488] to-[#22C55E] text-white border border-emerald-400/45 hover:opacity-95 shadow-[0_12px_26px_-12px_rgba(13,148,136,0.65)] active:scale-[0.99]"
                : "bg-slate-200 text-slate-400 cursor-not-allowed border border-slate-200/80"
            }`}
          >
            <span>캔버스 기입</span>
            <MainCtaArrowIcon active={isSessionValid} />
          </button>

          <button
            type="button"
            onClick={onGoAiColleagueForm}
            disabled={!isSessionValid}
            className={`w-full py-4 px-5 rounded-3xl font-extrabold text-base transition-[transform,box-shadow,filter] duration-200 flex items-center justify-between ${
              isSessionValid
                ? "main-cta-reveal main-cta-reveal-d3 cursor-pointer bg-gradient-to-r from-[#2563EB] to-[#06B6D4] text-white border border-sky-400/45 hover:opacity-95 shadow-[0_12px_26px_-12px_rgba(37,99,235,0.6)] active:scale-[0.99]"
                : "bg-slate-200 text-slate-400 cursor-not-allowed border border-slate-200/80"
            }`}
          >
            <span>워크플로우 재설계</span>
            <MainCtaArrowIcon active={isSessionValid} />
          </button>
        </div>
      </div>
    </div>
  );
}
