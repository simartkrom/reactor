export default function Loading() {
  return (
    <div className="min-h-dvh flex flex-col items-center justify-center bg-[#f6f7f9] px-6">
      <div className="w-full max-w-md rounded-3xl bg-white border border-black/5 shadow-sm p-6 flex flex-col items-center gap-6">
        <div className="relative w-14 h-14">
          <div className="absolute inset-0 rounded-full border-4 border-black/10" />
          <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-[color:var(--key-primary)] animate-spin" />
          <div className="absolute inset-3 rounded-full border-4 border-transparent border-t-[color:var(--key-highlight)] animate-spin [animation-direction:reverse] [animation-duration:0.9s]" />
        </div>

        <div className="text-center flex flex-col gap-1.5">
          <p className="text-lg font-bold text-slate-900">
            스킬 캐릭터를 분석 중입니다
          </p>
          <p className="text-base text-slate-500">
            잠시만 기다려 주세요
          </p>
        </div>
      </div>
    </div>
  );
}
