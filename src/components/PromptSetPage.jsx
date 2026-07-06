import { useCallback, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

const CORE_SKILLS = [
  { ko: "회복탄력성 및 민첩성", en: "Resilience & Agility", char: "다이내믹 서퍼" },
  { ko: "AI 및 빅데이터 활용", en: "AI & Big Data Utilization", char: "디지털 오라클" },
  { ko: "분석적 사고", en: "Analytical Thinking", char: "데이터 연금술사" },
  { ko: "창의적 사고", en: "Creative Thinking", char: "아이디어 스파크" },
  { ko: "기술 리터러시", en: "Tech Literacy & Digital Fluency", char: "테크 플루언트" },
  { ko: "리더십 및 사회적 영향력", en: "Leadership & Social Influence", char: "컬처 크리에이터" },
  { ko: "호기심 및 평생 학습", en: "Curiosity & Lifelong Learning", char: "지적 유목민" },
  { ko: "시스템적 사고", en: "Systems Thinking", char: "매크로 렌즈" },
  { ko: "인재 관리 및 육성", en: "Talent Management & Development", char: "포텐셜 부스터" },
  { ko: "동기 부여 및 자기 인식", en: "Self-Motivation & Self-Awareness", char: "코어 모티베이터" },
  { ko: "공감 및 적극적 경청", en: "Empathy & Active Listening", char: "하트 핑퐁" },
];

const SKILL_CHAR_TO_VISUAL_ROLE = {
  "다이내믹 서퍼":
    "a fearless surfer carving across crashing waves of glowing digital light, board cutting bright trails of neon spray, body leaning into the speed with arms wide",
  "데이터 연금술사":
    "an alchemist hunched over a bubbling cauldron of luminescent data, distilling glowing potions of insight, runes of code and floating equations swirling around them",
  "디지털 오라클":
    "an oracle seated before a giant floating crystal sphere, prophetic visions of futures swirling within, eyes glowing softly with foresight, ancient symbols hovering nearby",
  "아이디어 스파크":
    "a creative wizard with arms thrown wide, brilliant lightning-bolts of ideas erupting from their fingertips, sparks of innovation scattering across the entire scene",
  "테크 플루언트":
    "a starship navigator standing at the helm of a holographic console, charting paths through living constellations of code, glowing UI panels bending around them",
  "컬처 크리에이터":
    "a grand conductor on a vast podium, baton raised mid-gesture, harmonizing flowing rivers of multicolored light and people-shaped silhouettes into a symphony",
  "지적 유목민":
    "a robed explorer wandering through endless floating archives, books and scrolls and holographic libraries suspended in a cosmic void around them",
  "매크로 렌즈":
    "a cosmic navigator overseeing a vast holographic map of interconnected systems, zooming fluidly between atoms and galaxies, multiple scales visible at once",
  "포텐셜 부스터":
    "an energy weaver with hands outstretched toward surrounding silhouettes, awakening dormant glowing potentials inside each one, light blooming from their chests",
  "코어 모티베이터":
    "a radiant lighthouse beacon piercing through a digital storm, leading silhouettes of teammates toward the light, rays cutting through dark clouds",
  "하트 핑퐁":
    "an empathic guardian gently cupping a glowing heart of artificial consciousness, their pulses syncing in perfect rhythm, soft warm light pulsing between them",
};

const hasKorean = (text) => /[가-힯ᄀ-ᇿ㄰-㆏]/.test(text);

function customStrengthToVisualRole(raw) {
  const text = String(raw ?? "").trim();
  if (!text) return "";
  if (hasKorean(text)) return `Visionary Specialist embodying "${text}"`;
  return text;
}

function joinEnglishList(parts) {
  const filtered = parts.map((s) => String(s).trim()).filter(Boolean);
  if (filtered.length === 0) return "";
  if (filtered.length === 1) return filtered[0];
  if (filtered.length === 2) return `${filtered[0]} and ${filtered[1]}`;
  return `${filtered.slice(0, -1).join(", ")}, and ${filtered[filtered.length - 1]}`;
}

const MOOD_KEYWORDS = [
  { ko: "속도", en: "Dynamic motion blur, pulsing light trails, high-speed evolution" },
  { ko: "조화", en: "Harmonious blend of human intuition and digital intelligence" },
  { ko: "미래지향적", en: "Hyper-tech Future Fab environment, neon accents" },
  { ko: "전문적인", en: "Cinematic lighting, sharp focus, professional corporate atmosphere" },
  { ko: "따뜻한", en: "Warm ambient glow, golden-hour lighting, nurturing and inviting aura" },
  { ko: "강렬한", en: "Bold dramatic contrast, vivid saturated colors, high-impact visual" },
  { ko: "혁신적인", en: "Glowing holographic overlays, floating AR/VR elements, cutting-edge tech" },
  { ko: "신비로운", en: "Ethereal mist, mystical aurora, otherworldly luminescence" },
  { ko: "자연친화적", en: "Bio-digital fusion, organic circuits intertwined with lush nature" },
  { ko: "에너지 넘치는", en: "Electric energy sparks, vibrant plasma effects, explosive particles" },
  { ko: "우주적인", en: "Deep space nebula, cosmic constellation patterns, interstellar backdrop" },
  { ko: "미니멀한", en: "Clean minimalist composition, soft gradients, elegant negative space" },
];

const IMAGE_TYPES = [
  { ko: "3D 캐릭터 (픽사 스타일)", en: "Pixar/Disney style 3D cute and expressive character", icon: "🧸" },
  { ko: "고품질 애니메이션", en: "High-end Studio Ghibli or Cyberpunk Anime style", icon: "🎨" },
  { ko: "실사 인물 사진", en: "Hyper-realistic 8k cinematic photography, professional portrait", icon: "📸" },
  { ko: "예술적 일러스트", en: "Abstract and artistic digital illustration, vibrant colors", icon: "🖌️" },
  {
    ko: "귀여운 동물·마스코트",
    en: "Adorable fluffy animal mascot character, kawaii illustration style, soft pastel palette, big expressive eyes, charming and friendly vibe",
    icon: "🐾",
  },
];

const OUTCOME_OPTIONS = [
  { ko: "의사결정 속도 향상", en: "decision paths illuminating instantly like flashes of lightning around them" },
  { ko: "반복 업무 자동화", en: "swarms of tiny luminous AI agent figures absorbing repetitive task icons like glowing fireflies" },
  { ko: "창의·전략 시간 확보", en: "a vast halo of open creative space around them, floating sketches of fresh ideas drifting freely" },
  { ko: "고품질 인사이트 도출", en: "brilliant gem-like insights crystallizing from streams of raw data flowing past their hands" },
  { ko: "업무 생산성 향상", en: "dozens of glowing tasks completing themselves in rapid bursts of light around them" },
  { ko: "산출물 품질 향상", en: "their finished works displayed in midair, each piece radiating exquisite craft and luminous detail" },
  { ko: "새로운 비즈니스 가치 창출", en: "new luminous worlds and possibilities blooming forth from their gestures" },
  { ko: "빠른 학습·성장", en: "branches of knowledge visibly growing and evolving around them in real time" },
  { ko: "데이터 기반 의사결정", en: "translucent data dashboards and predictive charts materializing precisely when needed" },
  { ko: "삶의 여유 회복", en: "soft golden warm light spilling around them, peaceful breath visible in the air" },
  { ko: "일의 본질에 집중", en: "all distractions fading to soft mist, only the essential glowing brightly before them" },
];

const AI_TOOLS = [
  { name: "ChatGPT", href: "https://chatgpt.com", desc: "이미지 생성 추천" },
  { name: "Gemini", href: "https://gemini.google.com", desc: "이미지 생성 추천" },
  { name: "Arena AI", href: "https://lmarena.ai", desc: "다양한 모델 비교" },
];

const TOTAL_STEPS = 4;

function StepBadge({ step, total }) {
  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-gradient-to-r from-violet-600 to-fuchsia-600 px-2.5 py-0.5 text-[11px] font-bold text-white tracking-wide shadow-sm">
      STEP {step}
      <span className="text-white/60">/ {total}</span>
    </span>
  );
}

function Chip({ selected, onClick, children, sub }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`relative rounded-2xl px-3.5 py-2.5 text-left text-sm font-semibold transition-all duration-200 border-2 ${
        selected
          ? "bg-gradient-to-br from-violet-50 to-fuchsia-50 border-violet-400 text-violet-900 shadow-[0_4px_16px_-6px_rgba(124,58,237,0.4)] scale-[1.02]"
          : "bg-white border-slate-200 text-slate-700 hover:border-slate-300 hover:bg-slate-50 active:scale-[0.98]"
      }`}
    >
      <span className="block leading-snug">{children}</span>
      {sub && (
        <span className={`block text-xs mt-0.5 font-medium ${selected ? "text-violet-500" : "text-slate-400"}`}>
          {sub}
        </span>
      )}
      {selected && (
        <span className="absolute top-1.5 right-2 text-violet-500 text-xs">✓</span>
      )}
    </button>
  );
}

function ImageTypeCard({ item, selected, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`w-full rounded-2xl p-4 text-left transition-all duration-200 border-2 ${
        selected
          ? "bg-gradient-to-br from-violet-50 to-fuchsia-50 border-violet-400 shadow-[0_6px_20px_-8px_rgba(124,58,237,0.45)] scale-[1.01]"
          : "bg-white border-slate-200 hover:border-slate-300 hover:bg-slate-50 active:scale-[0.99]"
      }`}
    >
      <div className="flex items-start gap-3">
        <span className="text-2xl shrink-0 mt-0.5">{item.icon}</span>
        <div className="min-w-0 flex-1">
          <p className={`font-bold text-sm ${selected ? "text-violet-900" : "text-slate-800"}`}>
            {item.ko}
          </p>
          <p className={`text-xs mt-0.5 leading-relaxed ${selected ? "text-violet-500" : "text-slate-400"}`}>
            {item.en}
          </p>
        </div>
        {selected && <span className="text-violet-500 text-sm font-bold shrink-0">✓</span>}
      </div>
    </button>
  );
}

export default function PromptSetPage() {
  const navigate = useNavigate();
  const [toast, setToast] = useState(null);

  const [selectedSkills, setSelectedSkills] = useState([]);
  const [customStrength, setCustomStrength] = useState("");
  const [aiInsightsContext, setAiInsightsContext] = useState("");
  const [selectedOutcomes, setSelectedOutcomes] = useState([]);
  const [customOutcome, setCustomOutcome] = useState("");
  const [selectedMoods, setSelectedMoods] = useState([]);
  const [selectedImageType, setSelectedImageType] = useState("");
  const [promptExpanded, setPromptExpanded] = useState(true);

  const showToast = useCallback((message) => {
    setToast(message);
    window.setTimeout(() => setToast(null), 2200);
  }, []);

  const toggleSkill = useCallback((skillKo) => {
    setSelectedSkills((prev) =>
      prev.includes(skillKo) ? prev.filter((s) => s !== skillKo) : [...prev, skillKo]
    );
  }, []);

  const toggleMood = useCallback((moodKo) => {
    setSelectedMoods((prev) =>
      prev.includes(moodKo) ? prev.filter((m) => m !== moodKo) : [...prev, moodKo]
    );
  }, []);

  const toggleOutcome = useCallback((outcomeKo) => {
    setSelectedOutcomes((prev) =>
      prev.includes(outcomeKo) ? prev.filter((o) => o !== outcomeKo) : [...prev, outcomeKo]
    );
  }, []);

  const moodsEn = useMemo(
    () => selectedMoods.map((ko) => MOOD_KEYWORDS.find((m) => m.ko === ko)?.en).filter(Boolean),
    [selectedMoods]
  );

  const imageTypeEn = useMemo(
    () => IMAGE_TYPES.find((t) => t.ko === selectedImageType)?.en ?? "",
    [selectedImageType]
  );

  const step1MappedValues = useMemo(() => {
    const fromSkills = selectedSkills
      .map((ko) => {
        const skill = CORE_SKILLS.find((s) => s.ko === ko);
        const char = skill?.char;
        if (!char) return null;
        return SKILL_CHAR_TO_VISUAL_ROLE[char] ?? skill.en;
      })
      .filter(Boolean);
    const customRole = customStrengthToVisualRole(customStrength);
    const parts = [...fromSkills];
    if (customRole) parts.push(customRole);
    return joinEnglishList(parts);
  }, [selectedSkills, customStrength]);

  const step4Atmosphere = useMemo(
    () => (moodsEn.length > 0 ? joinEnglishList(moodsEn) : ""),
    [moodsEn]
  );

  const aiInsightsContextText = useMemo(() => aiInsightsContext.trim(), [aiInsightsContext]);

  const outcomesEn = useMemo(
    () =>
      selectedOutcomes
        .map((ko) => OUTCOME_OPTIONS.find((o) => o.ko === ko)?.en)
        .filter(Boolean),
    [selectedOutcomes]
  );

  const aiOutcomeContextText = useMemo(() => {
    const parts = [...outcomesEn];
    const custom = customOutcome.trim();
    if (custom) {
      parts.push(hasKorean(custom) ? `vivid impact embodied as "${custom}"` : custom);
    }
    return joinEnglishList(parts);
  }, [outcomesEn, customOutcome]);

  const hasFreeKorean = useMemo(
    () =>
      hasKorean(customStrength) ||
      hasKorean(aiInsightsContext) ||
      hasKorean(customOutcome),
    [customStrength, aiInsightsContext, customOutcome]
  );

  const generatedPrompt = useMemo(() => {
    const imageType = imageTypeEn || "[이미지 유형을 선택하세요]";
    const step1ForPrompt = step1MappedValues || "[핵심 스킬 또는 강점을 입력하세요]";
    const aiVision_from_Step2 =
      aiInsightsContextText || "[내가 지향하는 AI Native 모습을 입력하세요]";
    const aiOutcome_from_Step3 =
      aiOutcomeContextText || "[AI Native로 만들어낼 결과·임팩트를 입력하세요]";
    const step4ForPrompt = step4Atmosphere || "[분위기 키워드를 선택하세요]";

    let prompt = `${imageType}, a highly symbolic and metaphorical AI Native artwork. A single visionary character at the center of the composition.

SUBJECT (one character, embodying the following role and action): ${step1ForPrompt}.

VISIBLE IMPACT AROUND THEM (render these as concrete visual phenomena, not text): with ${aiOutcome_from_Step3}.

ATMOSPHERE, LIGHTING & COLOR PALETTE: ${step4ForPrompt}.

CORE IDENTITY KEYWORDS (interpret visually through the character's posture, aura and expression — do NOT render as literal text): "${aiVision_from_Step2}".

RENDER STYLE: ${imageType}. Masterpiece, visually breathtaking, 8k resolution, highly detailed, cinematic lighting, dramatic composition, strong silhouette.

NEGATIVE: avoid generic office worker, avoid literal cubicle or desk, avoid plain corporate stock-photo look, avoid text or watermarks in the image.`;

    if (hasFreeKorean) {
      prompt += `\n\n(Note: Some parts of this prompt contain Korean text. Please interpret and translate them into natural English meaning for image generation.)`;
    }

    return prompt;
  }, [
    imageTypeEn,
    step1MappedValues,
    aiInsightsContextText,
    aiOutcomeContextText,
    step4Atmosphere,
    hasFreeKorean,
  ]);

  const isComplete =
    Boolean(imageTypeEn) &&
    Boolean(step1MappedValues) &&
    Boolean(aiInsightsContextText) &&
    Boolean(aiOutcomeContextText) &&
    moodsEn.length > 0;

  const completedSteps = [
    selectedSkills.length > 0 || customStrength.trim(),
    aiInsightsContextText,
    selectedOutcomes.length > 0 || customOutcome.trim(),
    selectedMoods.length > 0 && selectedImageType,
  ].filter(Boolean).length;

  const copyPrompt = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(generatedPrompt);
      showToast("프롬프트가 클립보드에 복사되었습니다!");
    } catch {
      showToast("복사에 실패했습니다. 브라우저 권한을 확인해주세요.");
    }
  }, [generatedPrompt, showToast]);

  return (
    <div className="min-h-dvh bg-[#f0f2f6] text-slate-950 pb-[max(2rem,env(safe-area-inset-bottom))]">
      <div className="mx-auto w-full max-w-md px-4 pt-4 pb-10 flex flex-col gap-5">

        <header className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="shrink-0 w-11 h-11 rounded-2xl bg-white border border-black/10 text-slate-700 font-bold text-sm shadow-sm flex items-center justify-center"
            aria-label="이전 화면"
          >
            ←
          </button>
          <div className="min-w-0 flex-1">
            <p className="text-xs font-bold text-violet-600 tracking-wide">
              The Tempo · AI Native Canvas
            </p>
            <h1 className="text-lg font-extrabold leading-tight tracking-tight">
              AI Native 이미지 프롬프트 빌더
            </h1>
          </div>
        </header>

        <section className="rounded-3xl bg-gradient-to-br from-violet-600 via-fuchsia-600 to-pink-500 p-5 shadow-[0_16px_48px_-16px_rgba(124,58,237,0.5)] text-white">
          <h2 className="text-base font-extrabold mb-1.5">나만의 AI Native 페르소나 이미지 만들기</h2>
          <p className="text-sm text-white/85 leading-relaxed">
            아래 항목을 선택하면 영문 프롬프트가 자동으로 생성됩니다.
            완성된 프롬프트를 복사해 AI 도구에 붙여넣으세요!
          </p>
          <div className="mt-3 flex items-center gap-2">
            <div className="flex-1 h-1.5 rounded-full bg-white/20 overflow-hidden">
              <div
                className="h-full rounded-full bg-white/90 transition-all duration-500"
                style={{ width: `${(completedSteps / TOTAL_STEPS) * 100}%` }}
              />
            </div>
            <span className="text-xs font-bold text-white/70">{completedSteps}/{TOTAL_STEPS}</span>
          </div>
        </section>

        <section className="rounded-3xl bg-white p-5 shadow-sm border border-black/5">
          <div className="flex items-center gap-2 mb-1">
            <StepBadge step={1} total={TOTAL_STEPS} />
            <h2 className="text-base font-extrabold text-slate-900">핵심 스킬 & 강점 (복수 선택 가능)</h2>
          </div>

          <p className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2 mt-4">캐릭터 연동 스킬</p>
          <div className="grid grid-cols-2 gap-2 mb-5">
            {CORE_SKILLS.map((s) => (
              <Chip
                key={s.ko}
                selected={selectedSkills.includes(s.ko)}
                onClick={() => toggleSkill(s.ko)}
                sub={s.char}
              >
                {s.ko}
              </Chip>
            ))}
          </div>

          {(selectedSkills.length > 0 || customStrength.trim()) && step1MappedValues && (
            <div className="mb-4 p-3 rounded-xl bg-violet-50/60 border border-violet-100">
              <p className="text-xs text-violet-600 leading-relaxed">
                → {step1MappedValues}
              </p>
            </div>
          )}

          <div className="border-t border-slate-100 pt-4">
            <label className="block text-sm font-bold text-slate-700 mb-2">
              위에 없는 강점 직접 입력 <span className="font-medium text-slate-400">(선택)</span>
            </label>
            <input
              type="text"
              value={customStrength}
              onChange={(e) => setCustomStrength(e.target.value)}
              placeholder="예: Global mindset, Networking"
              className="w-full rounded-2xl border-2 border-slate-200 bg-[#f6f7f9] px-4 py-3 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:border-violet-400 focus:bg-violet-50/30 transition-colors"
            />
            {customStrength.trim() && hasKorean(customStrength) && (
              <p className="mt-1.5 text-xs text-amber-600 font-medium">
                한국어가 감지되었습니다. 프롬프트에 AI 자동 번역 지시가 추가됩니다.
              </p>
            )}
          </div>
        </section>

        <section className="rounded-3xl bg-white p-5 shadow-sm border border-black/5">
          <div className="flex items-center gap-2 mb-1">
            <StepBadge step={2} total={TOTAL_STEPS} />
            <h2 className="text-base font-extrabold text-slate-900">나의 AI Native</h2>
          </div>
          <p className="text-sm text-slate-500 mb-3 leading-relaxed">
            내가 지향하는 나만의 AI Native 모습을 작성해주세요.
          </p>
          <textarea
            value={aiInsightsContext}
            onChange={(e) => setAiInsightsContext(e.target.value)}
            placeholder={`예) AI 명인, 디지털 마에스트로, AI 에이전트 지휘자,\n손짓 하나로 워크플로우를 움직이는 사람`}
            rows={4}
            className="w-full rounded-2xl border-2 border-slate-200 bg-[#f6f7f9] px-4 py-3 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:border-violet-400 focus:bg-violet-50/30 transition-colors resize-y leading-relaxed"
          />
          {aiInsightsContextText && hasKorean(aiInsightsContextText) && (
            <p className="mt-1.5 text-xs text-amber-600 font-medium">
              한국어가 감지되었습니다. 프롬프트에 AI 자동 번역 지시가 추가됩니다.
            </p>
          )}
          {aiInsightsContextText && (
            <div className="mt-3 p-3 rounded-xl bg-violet-50/60 border border-violet-100">
              <p className="text-xs text-violet-600 leading-relaxed break-words whitespace-pre-wrap">
                → {aiInsightsContextText}
              </p>
            </div>
          )}
        </section>

        <section className="rounded-3xl bg-white p-5 shadow-sm border border-black/5">
          <div className="flex items-center gap-2 mb-1">
            <StepBadge step={3} total={TOTAL_STEPS} />
            <h2 className="text-base font-extrabold text-slate-900">결과·임팩트 (복수 선택 가능)</h2>
          </div>
          <p className="text-sm text-slate-500 mb-4 leading-relaxed">
            AI Native가 되어 달성하고자 하는 결과·기대·성과를 골라주세요.
          </p>

          <div className="grid grid-cols-2 gap-2">
            {OUTCOME_OPTIONS.map((o) => (
              <Chip
                key={o.ko}
                selected={selectedOutcomes.includes(o.ko)}
                onClick={() => toggleOutcome(o.ko)}
              >
                {o.ko}
              </Chip>
            ))}
          </div>

          {(selectedOutcomes.length > 0 || customOutcome.trim()) && aiOutcomeContextText && (
            <div className="mt-4 p-3 rounded-xl bg-violet-50/60 border border-violet-100">
              <p className="text-xs text-violet-600 leading-relaxed break-words">
                → {aiOutcomeContextText}
              </p>
            </div>
          )}

          <div className="border-t border-slate-100 mt-5 pt-4">
            <label className="block text-sm font-bold text-slate-700 mb-2">
              직접 추가 <span className="font-medium text-slate-400">(선택)</span>
            </label>
            <input
              type="text"
              value={customOutcome}
              onChange={(e) => setCustomOutcome(e.target.value)}
              placeholder="예: 내가 가장 싫어했던 반복 업무가 사라진 일상"
              className="w-full rounded-2xl border-2 border-slate-200 bg-[#f6f7f9] px-4 py-3 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:border-violet-400 focus:bg-violet-50/30 transition-colors"
            />
            {customOutcome.trim() && hasKorean(customOutcome) && (
              <p className="mt-1.5 text-xs text-amber-600 font-medium">
                한국어가 감지되었습니다. 프롬프트에 AI 자동 번역 지시가 추가됩니다.
              </p>
            )}
          </div>
        </section>

        <section className="rounded-3xl bg-white p-5 shadow-sm border border-black/5">
          <div className="flex items-center gap-2 mb-1">
            <StepBadge step={4} total={TOTAL_STEPS} />
            <h2 className="text-base font-extrabold text-slate-900">분위기 & 이미지 유형</h2>
          </div>
          <p className="text-sm text-slate-500 mb-4">
            이미지의 분위기와 표현 스타일을 골라주세요
          </p>

          <p className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">분위기 키워드 (다중 선택 가능)</p>
          <div className="grid grid-cols-3 gap-2">
            {MOOD_KEYWORDS.map((m) => (
              <button
                key={m.ko}
                type="button"
                onClick={() => toggleMood(m.ko)}
                className={`rounded-2xl px-3 py-2.5 text-sm font-bold transition-all duration-200 border-2 text-center ${
                  selectedMoods.includes(m.ko)
                    ? "bg-gradient-to-br from-violet-50 to-fuchsia-50 border-violet-400 text-violet-800 shadow-[0_4px_12px_-4px_rgba(124,58,237,0.35)] scale-[1.03]"
                    : "bg-white border-slate-200 text-slate-600 hover:border-slate-300 active:scale-[0.97]"
                }`}
              >
                {m.ko}
              </button>
            ))}
          </div>
          {selectedMoods.length > 0 && (
            <div className="mt-3 p-3 rounded-xl bg-violet-50/60 border border-violet-100">
              <p className="text-xs text-violet-600 leading-relaxed">
                {step4Atmosphere}
              </p>
            </div>
          )}

          <div className="border-t border-slate-100 mt-5 pt-5">
            <p className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">이미지 유형</p>
            <div className="flex flex-col gap-2">
              {IMAGE_TYPES.map((t) => (
                <ImageTypeCard
                  key={t.ko}
                  item={t}
                  selected={selectedImageType === t.ko}
                  onClick={() => setSelectedImageType(t.ko)}
                />
              ))}
            </div>
          </div>
        </section>

        <section className="rounded-3xl overflow-hidden shadow-[0_16px_48px_-24px_rgba(124,58,237,0.4)] border border-violet-200/70 bg-white">
          <button
            type="button"
            onClick={() => setPromptExpanded((p) => !p)}
            className="w-full bg-gradient-to-r from-violet-600 to-fuchsia-600 px-5 py-4 flex items-center justify-between text-white"
          >
            <div>
              <h2 className="text-base font-extrabold text-left">생성된 영문 프롬프트</h2>
              <p className="text-xs text-white/70 mt-0.5 text-left">
                {isComplete ? "모든 항목이 입력되었습니다!" : "항목을 선택하면 실시간으로 반영됩니다"}
              </p>
            </div>
            <span className={`text-xl transition-transform duration-300 ${promptExpanded ? "rotate-180" : ""}`}>
              ▾
            </span>
          </button>

          {promptExpanded && (
            <div className="p-5 flex flex-col gap-4">
              {hasFreeKorean && (
                <div className="rounded-2xl bg-amber-50 border border-amber-200/90 px-3 py-2.5 text-[13px] text-amber-800 leading-relaxed">
                  한국어 자유 입력이 감지되어, AI가 자동으로 영어로 해석하도록 지시문이 추가되었습니다.
                </div>
              )}
              <div className="rounded-2xl bg-slate-50 border border-slate-200/80 max-h-[min(50vh,360px)] overflow-y-auto overscroll-contain p-4">
                <pre className="whitespace-pre-wrap break-words font-sans text-[12px] sm:text-[13px] text-slate-700 leading-relaxed">
                  {generatedPrompt}
                </pre>
              </div>

              <button
                type="button"
                onClick={copyPrompt}
                className={`w-full min-h-[52px] rounded-2xl font-extrabold text-base shadow-lg border transition-all active:scale-[0.99] ${
                  isComplete
                    ? "bg-gradient-to-r from-violet-600 to-fuchsia-600 text-white border-violet-400/40 shadow-[0_10px_24px_-12px_rgba(124,58,237,0.7)]"
                    : "bg-gradient-to-r from-violet-500/80 to-fuchsia-500/80 text-white/90 border-violet-300/40 shadow-[0_10px_24px_-12px_rgba(124,58,237,0.4)]"
                }`}
              >
                프롬프트 복사하기
              </button>
            </div>
          )}
        </section>

        <section className="rounded-3xl bg-white p-5 shadow-sm border border-black/5">
          <h2 className="text-base font-extrabold text-slate-900 mb-1">
            AI 도구에 붙여넣기
          </h2>
          <p className="text-sm text-slate-500 mb-3">
            프롬프트를 복사한 후, 아래 도구에서 새 채팅을 열어 붙여넣으세요
          </p>
          <div className="flex flex-col gap-2">
            {AI_TOOLS.map((t) => (
              <a
                key={t.name}
                href={t.href}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-between gap-3 rounded-2xl bg-[#f6f7f9] border border-black/8 px-4 py-3.5 min-h-[48px] active:bg-slate-100"
              >
                <div>
                  <span className="font-bold text-slate-900">{t.name}</span>
                  <span className="ml-2 text-xs text-slate-400">{t.desc}</span>
                </div>
                <span className="text-xs text-slate-500 shrink-0">새 채팅 →</span>
              </a>
            ))}
          </div>
        </section>

        <section className="rounded-3xl bg-slate-900 text-slate-100 p-5 shadow-inner border border-slate-700/50">
          <h2 className="text-base font-extrabold mb-3 text-white">주의사항</h2>
          <ul className="space-y-2.5 text-[14px] leading-relaxed text-slate-300">
            <li className="flex gap-2">
              <span className="text-violet-400 shrink-0">✓</span>
              이미지가 바로 안 나오면 &apos;이미지 생성&apos; 버튼을 누르거나 새 채팅에서 다시 붙여넣어 보세요.
            </li>
            <li className="flex gap-2">
              <span className="text-violet-400 shrink-0">✓</span>
              개인정보나 회사 기밀정보는 입력하지 마세요.
            </li>
            <li className="flex gap-2">
              <span className="text-violet-400 shrink-0">✓</span>
              결과가 마음에 들지 않으면 키워드를 바꿔 다시 시도해보세요!
            </li>
          </ul>
        </section>
      </div>

      {toast && (
        <div
          className="fixed bottom-6 left-1/2 z-50 -translate-x-1/2 px-5 py-3 rounded-2xl bg-slate-900 text-white text-sm font-semibold shadow-lg max-w-[min(90vw,20rem)] text-center"
          role="status"
        >
          {toast}
        </div>
      )}
    </div>
  );
}
