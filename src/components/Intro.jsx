export default function Intro({ onProceed }) {
  return (
    <div className="min-h-dvh bg-[#f6f7f9] text-slate-950">
      <div className="mx-auto w-full max-w-md px-5 pt-10 pb-8 flex flex-col gap-5">
        <div className="w-full rounded-3xl bg-white p-6 shadow-sm border border-black/5">
          <header className="flex flex-col gap-3">
            <p className="text-xs font-semibold tracking-[0.18em] text-[color:var(--key-primary)] uppercase text-center">
              Skill Balance Game
            </p>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight leading-snug text-slate-950 text-center">
              시작하기 전에
            </h1>
            <p className="text-slate-600 text-base sm:text-lg leading-relaxed text-left">
              이 밸런스 게임은{" "}
              <span className="font-bold text-slate-800">
                세계경제포럼(WEF)
              </span>
              이 발표한{" "}
              <span className="font-bold text-slate-800">
                '2030년 미래 핵심 스킬(Core Skills)'
              </span>{" "}
              연구를 기반으로 설계되었습니다.
            </p>
            <p className="text-slate-600 text-base sm:text-lg leading-relaxed text-left">
              가까운 미래, AI가 우리의 동료가 된 실무 현장에서는 수많은 선택의 기로가 펼쳐집니다.
              주어지는 리얼한 업무 상황 속에서{" "}
              <span className="font-bold text-slate-900">
                나는 어떤 해결 방식을 더 선호하는지
              </span>{" "}
              직관적으로 선택해 주세요! 나의 선택들이 모여 나만의 고유한{" "}
              <span className="font-bold text-slate-900">
                'AI 시대 캐릭터(11가지 유형)'
              </span>
              를 도출해 냅니다.
            </p>
          </header>

          <div className="mt-4 pt-4 border-t border-dashed border-black/10">
            <p className="text-lg sm:text-xl font-extrabold text-[color:var(--key-primary)] mb-2">
              세 가지만 기억해 주세요!
            </p>
            <ul className="text-sm sm:text-base text-slate-700 leading-relaxed space-y-2">
              <li>
                <span className="font-bold text-slate-900">1. 정답은 없습니다</span>
                <span className="text-slate-500">
                  : '이렇게 해야 훌륭해 보이겠지?'라는 생각보다는, 가장{" "}
                  <span className="font-bold">'나다운'</span> 솔직한 선택이 나와 가장 찰떡인 결과를 만듭니다.
                </span>
              </li>
              <li>
                <span className="font-bold text-slate-900">
                  2. 직감적으로 선택하세요
                </span>
                <span className="text-slate-500">
                  : 너무 오래 고민하지 마세요. 상황을 읽고 내 마음이 더 강하게 끌리는 쪽을 가벼운 마음으로 골라주세요.
                </span>
              </li>
              <li>
                <span className="font-bold text-slate-900">
                  3. 나만의 템포를 발견하세요
                </span>
                <span className="text-slate-500">
                  : 이 결과는 절대적인 평가가 아닙니다. 거대한 기술의 물결 속에서, 나만의 스킬 선호도와 업무 리듬을
                  확인하기 위한 흥미로운 나침반이 될 것입니다.
                </span>
              </li>
            </ul>
          </div>
        </div>

        <button
          onClick={onProceed}
          className="w-full py-4 rounded-3xl bg-[color:var(--key-primary)] text-white font-bold text-lg hover:opacity-90 transition-all duration-200 cursor-pointer mt-1 shadow-sm"
        >
          문항 시작하기
        </button>
      </div>
    </div>
  );
}
