import { useMemo, useRef } from "react";
import {
  characterData,
  characterImageFile,
  wefSkills,
  SKILL_LABELS,
} from "../data/resultData";

function characterImageSrc(resultCode) {
  const file = characterImageFile?.[resultCode];
  if (!file) return null;
  return `/${encodeURIComponent(file)}`;
}

const SKILL_CODE_ORDER = Object.keys(SKILL_LABELS);

function getRankedSkills(memberScore) {
  return SKILL_CODE_ORDER
    .map((code) => ({
      code,
      name: SKILL_LABELS[code],
      score: Number(memberScore?.[code] ?? 0),
    }))
    .sort(
      (a, b) =>
        b.score - a.score ||
        SKILL_CODE_ORDER.indexOf(a.code) - SKILL_CODE_ORDER.indexOf(b.code),
    );
}

function SkillBar({ value, max }) {
  const pct = max > 0 ? Math.round((value / max) * 100) : 0;

  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 h-2.5 rounded-full bg-slate-200 overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-[color:var(--key-primary)] to-[color:var(--sk-red)] rounded-full"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

function renderLeadBold(text) {
  if (!text) return "";
  const normalized = String(text).trim();
  const match = normalized.match(/^(.*?\.)\s*(.*)$/);
  if (!match) return normalized;
  return (
    <>
      <strong className="font-extrabold text-slate-900">{match[1]}</strong>{" "}
      <span>{match[2]}</span>
    </>
  );
}

export default function Result({
  resultType,
  memberScore,
  coTopSkills = [],
  onRestart,
}) {
  const captureRef = useRef(null);

  const resultCode = resultType?.memberResult;
  const character = resultCode ? characterData?.[resultCode] : null;

  const ranked = useMemo(() => getRankedSkills(memberScore), [memberScore]);
  const maxScore = ranked[0]?.score ?? 0;

  const topSkillName = resultCode
    ? SKILL_LABELS?.[resultCode]
    : ranked[0]?.name;
  const topSkillDesc = topSkillName ? wefSkills?.[topSkillName] : "";

  const top3 = ranked.slice(0, 3);
  const allCoreSkills = SKILL_CODE_ORDER.map((code) => SKILL_LABELS[code]);

  const coStrengths = (coTopSkills || [])
    .filter((code) => code && code !== resultCode && SKILL_LABELS[code])
    .map((code) => ({ code, name: SKILL_LABELS[code] }));

  if (!character) return null;

  const charImgSrc = characterImageSrc(resultCode);

  return (
    <div className="min-h-dvh bg-[#f6f7f9] text-slate-950">
      <div className="max-w-2xl mx-auto px-5 py-8 sm:py-12 flex flex-col items-center gap-6">
        <div ref={captureRef} className="flex flex-col gap-6 w-full">
          <div className="w-full rounded-[28px] bg-white/45 backdrop-blur-xl border border-white/50 shadow-[0_20px_60px_-28px_rgba(2,6,23,0.45)] overflow-hidden">
            {charImgSrc && (
              <div className="-mb-px relative flex justify-center bg-white px-0 pt-0 pb-0 sm:px-8 sm:pt-8 sm:pb-3">
                <img
                  src={charImgSrc}
                  alt={character.name}
                  className="h-auto w-full object-contain sm:max-h-[min(56vh,520px)]"
                  loading="eager"
                  decoding="async"
                />
              </div>
            )}

            <div className="p-7 sm:p-9 pt-6 sm:pt-8">
              <p className="inline-flex items-center text-[11px] bg-[color:var(--key-primary)]/10 text-[color:var(--key-primary)] font-extrabold tracking-widest uppercase px-2.5 py-1 rounded-full mb-3">
                AI 시대 스킬 캐릭터 (11유형)
              </p>
              <h1 className="text-2xl sm:text-3xl font-black text-slate-950 mb-2 leading-tight">
                {character.name}
              </h1>
              <p className="text-sm sm:text-base text-slate-600 font-medium mb-5">
                {character.subtitle}
              </p>

              <div className="flex flex-wrap gap-2 mb-5">
                <span className="inline-flex items-center px-3 py-2 rounded-full bg-gradient-to-r from-[#fff7f2] to-white border border-[color:var(--key-primary)]/25 text-sm font-extrabold text-slate-900">
                  연결 스킬: {topSkillName}
                </span>
              </div>

              {topSkillDesc ? (
                <div className="rounded-3xl bg-gradient-to-br from-[#fff9f5] to-[#f8fafc] border border-black/10 px-6 py-5 mb-5">
                  <p className="text-xs font-extrabold text-[color:var(--key-primary)] uppercase tracking-wider mb-2">
                    스킬 설명
                  </p>
                  <p className="text-sm sm:text-base text-slate-700 leading-relaxed">
                    {renderLeadBold(topSkillDesc)}
                  </p>
                </div>
              ) : null}

              <p className="text-sm sm:text-base text-slate-700 leading-relaxed text-left">
                {renderLeadBold(character.description)}
              </p>
            </div>
          </div>

          {coStrengths.length > 0 ? (
            <div className="w-full rounded-[28px] bg-white/55 backdrop-blur-xl p-6 sm:p-7 border border-[color:var(--key-primary)]/20 shadow-[0_14px_36px_-22px_rgba(245,87,8,0.35)]">
              <p className="text-[11px] font-extrabold text-[color:var(--key-primary)] uppercase tracking-widest mb-2">
                함께 두드러진 스킬
              </p>
              <h3 className="text-base sm:text-lg font-extrabold text-slate-900 leading-snug mb-2">
                메인 강점 외에도 동등하게 높았던 영역이에요
              </h3>
              <p className="text-sm text-slate-600 leading-relaxed mb-4">
                22문항에서 메인 스킬과 동일하게 점수가 높았던 강점입니다.
                메인은 직접 정하셨지만, 아래 스킬도 당신의 핵심 자산이에요.
              </p>
              <div className="flex flex-wrap gap-2">
                {coStrengths.map((s) => (
                  <span
                    key={s.code}
                    className="inline-flex items-center px-3 py-2 rounded-full bg-white border border-[color:var(--key-primary)]/25 text-sm font-bold text-slate-800"
                  >
                    {s.name}
                  </span>
                ))}
              </div>
            </div>
          ) : null}

          <div className="w-full rounded-[28px] bg-white/40 backdrop-blur-xl p-6 sm:p-8 border border-white/55 shadow-[0_16px_40px_-24px_rgba(2,6,23,0.35)]">
            <div className="flex items-end justify-between gap-3 mb-4">
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                나의 스킬 분포 (22개 문항 및 11개 스킬)
              </h3>
              <p className="text-xs font-semibold text-slate-500">Top 3</p>
            </div>
            <p className="text-sm text-slate-500 mb-4">
              상위 3개 스킬의 정의와 상태를 함께 보여줍니다.
            </p>
            <div className="flex flex-col gap-3">
              {top3.map((s, idx) => (
                <div
                  key={s.code}
                  className="rounded-2xl bg-gradient-to-br from-white to-[#f8fafc] border border-black/10 px-4 py-4"
                >
                  <div className="flex items-center gap-2 mb-1.5">
                    <span className="inline-flex w-6 h-6 rounded-full bg-slate-900 text-white text-[11px] font-extrabold items-center justify-center">
                      {idx + 1}
                    </span>
                    <p className="text-base font-extrabold text-slate-900">
                      {s.name}
                    </p>
                  </div>
                  <p className="text-sm text-slate-600 leading-relaxed mb-3">
                    {renderLeadBold(wefSkills?.[s.name] || "")}
                  </p>
                  <SkillBar value={s.score} max={maxScore} />
                </div>
              ))}
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-1">
            <div className="w-full rounded-[28px] bg-white/40 backdrop-blur-xl p-6 border border-white/55 shadow-[0_16px_40px_-24px_rgba(2,6,23,0.35)]">
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-4">
                Core Skills (11개)
              </h3>
              <ul className="space-y-3">
                {allCoreSkills.map((name, idx) => (
                  <li
                    key={name}
                    className="rounded-2xl bg-gradient-to-br from-white to-[#f8fafc] border border-black/10 px-4 py-4"
                  >
                    <div className="flex items-center gap-2 mb-1.5">
                      <span className="inline-flex w-6 h-6 rounded-full bg-[color:var(--key-primary)] text-white text-[11px] font-extrabold items-center justify-center">
                        {idx + 1}
                      </span>
                      <p className="text-base font-extrabold text-slate-900">
                        {name}
                      </p>
                    </div>
                    <p className="text-sm text-slate-600 leading-relaxed">
                      {renderLeadBold(wefSkills?.[name] || "")}
                    </p>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        <div className="w-full max-w-xs flex flex-col gap-3 mt-1">
          <button
            type="button"
            onClick={onRestart}
            className="w-full py-4 rounded-3xl bg-gradient-to-r from-[color:var(--key-primary)] to-[color:var(--sk-red)] text-white font-bold text-sm hover:opacity-90 transition-all duration-200 cursor-pointer shadow-[0_14px_30px_-14px_rgba(245,87,8,0.7)]"
          >
            처음으로
          </button>
        </div>
      </div>
    </div>
  );
}
