import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "../supabaseClient";

const INITIAL_CANVAS_FORM = {
  name: "",
  core_skill: "",
  self_action: "",
  ai_support: "",
  org_support: "",
};

const INITIAL_LEADER_FORM = {
  leader_message: "",
};

export default function OpenFeedbackForm({ mode, sessionId }) {
  const navigate = useNavigate();
  const isCanvasMode = mode === "canvas";
  const [canvasForm, setCanvasForm] = useState(INITIAL_CANVAS_FORM);
  const [leaderForm, setLeaderForm] = useState(INITIAL_LEADER_FORM);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const handleCanvasChange = (field) => (event) => {
    setCanvasForm((prev) => ({
      ...prev,
      [field]: event.target.value,
    }));
  };

  const handleLeaderChange = (event) => {
    setLeaderForm({ leader_message: event.target.value });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setErrorMessage("");
    setSuccessMessage("");

    if (!supabase) {
      setErrorMessage(
        "Supabase 설정을 찾을 수 없습니다. 환경 변수를 먼저 확인해 주세요.",
      );
      return;
    }

    if (!sessionId) {
      setErrorMessage("먼저 메인 화면에서 유효한 차수 코드를 확인해 주세요.");
      return;
    }

    if (isCanvasMode) {
      if (
        !canvasForm.core_skill.trim() ||
        !canvasForm.self_action.trim() ||
        !canvasForm.ai_support.trim() ||
        !canvasForm.org_support.trim()
      ) {
        setErrorMessage("핵심 스킬 및 4개 문항은 필수로 작성해 주세요.");
        return;
      }
    } else if (!leaderForm.leader_message.trim()) {
      setErrorMessage("리더에게 남길 한마디를 작성해 주세요.");
      return;
    }

    setIsSubmitting(true);
    try {
      const payload = isCanvasMode
        ? {
            session_id: sessionId,
            form_type: "canvas",
            name: canvasForm.name.trim() || null,
            core_skill: canvasForm.core_skill.trim(),
            self_action: canvasForm.self_action.trim(),
            ai_support: canvasForm.ai_support.trim(),
            org_support: canvasForm.org_support.trim(),
            leader_message: null,
          }
        : {
            session_id: sessionId,
            form_type: "leader",
            name: null,
            core_skill: null,
            self_action: null,
            ai_support: null,
            org_support: null,
            leader_message: leaderForm.leader_message.trim(),
          };

      const { error } = await supabase.from("open_feedbacks").insert(payload);
      if (error) throw error;

      setSuccessMessage("제출이 완료되었습니다. 감사합니다!");
      if (typeof window !== "undefined") {
        window.alert("제출이 완료되었습니다!");
      }
      if (isCanvasMode) {
        setCanvasForm(INITIAL_CANVAS_FORM);
      } else {
        setLeaderForm(INITIAL_LEADER_FORM);
      }
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error("[Supabase] 주관식 응답 저장 실패:", err);
      setErrorMessage("제출 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-dvh bg-[#f6f7f9] text-slate-950">
      <div className="mx-auto w-full max-w-md px-5 pt-10 pb-8">
        <div className="w-full rounded-3xl bg-white p-6 shadow-sm border border-black/5">
          <h1 className="text-2xl font-extrabold tracking-tight leading-snug text-slate-950">
            {isCanvasMode ? "캔버스 기입" : "리더에게"}
          </h1>
          <p className="text-slate-600 text-sm leading-relaxed mt-2">
            {isCanvasMode
              ? "AI Native가 되기 위한 나의 핵심 스킬과 나, 조직, AI 관점의 지원 필요 사항을 자유롭게 작성해 주세요."
              : "AI 시대, AI Native로 성장하기 위해 리더의 지원이나 조직의 변화가 필요하다고 느끼는 한마디를 작성해 주세요."}
          </p>

          <form onSubmit={handleSubmit} className="mt-5 flex flex-col gap-4">
            {isCanvasMode ? (
              <>
                <FieldLabel
                  text="성함 (익명 가능)"
                  example="예) 김OO / 익명"
                />
                <textarea
                  value={canvasForm.name}
                  onChange={handleCanvasChange("name")}
                  rows={2}
                  className="w-full rounded-2xl bg-[#f6f7f9] border border-black/10 px-4 py-3 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-[color:var(--key-primary)] focus:ring-2 focus:ring-[color:var(--key-primary)]/15 resize-y"
                />

                <FieldLabel
                  text="핵심 스킬"
                  required
                  example="예) 분석적 사고, AI and Big Data, 회복탄력성 등"
                />
                <textarea
                  value={canvasForm.core_skill}
                  onChange={handleCanvasChange("core_skill")}
                  rows={3}
                  className="w-full rounded-2xl bg-[#f6f7f9] border border-black/10 px-4 py-3 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-[color:var(--key-primary)] focus:ring-2 focus:ring-[color:var(--key-primary)]/15 resize-y"
                />

                <FieldLabel
                  text="'내'가 바로 실행할 수 있는 것"
                  required
                  example="예) AI가 이해할 수 있도록 데이터 정리하기"
                />
                <textarea
                  value={canvasForm.self_action}
                  onChange={handleCanvasChange("self_action")}
                  rows={3}
                  className="w-full rounded-2xl bg-[#f6f7f9] border border-black/10 px-4 py-3 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-[color:var(--key-primary)] focus:ring-2 focus:ring-[color:var(--key-primary)]/15 resize-y"
                />

                <FieldLabel
                  text="'AI'로부터 도움 받을 것"
                  required
                  example="예) 자료 요약, 초안 작성, 코드/문장 개선 피드백"
                />
                <textarea
                  value={canvasForm.ai_support}
                  onChange={handleCanvasChange("ai_support")}
                  rows={3}
                  className="w-full rounded-2xl bg-[#f6f7f9] border border-black/10 px-4 py-3 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-[color:var(--key-primary)] focus:ring-2 focus:ring-[color:var(--key-primary)]/15 resize-y"
                />

                <FieldLabel
                  text="'조직/팀'으로부터 지원 받을 것"
                  required
                  example="예) AI 기술 트렌드나 활용 사례 공유 받기"
                />
                <textarea
                  value={canvasForm.org_support}
                  onChange={handleCanvasChange("org_support")}
                  rows={3}
                  className="w-full rounded-2xl bg-[#f6f7f9] border border-black/10 px-4 py-3 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-[color:var(--key-primary)] focus:ring-2 focus:ring-[color:var(--key-primary)]/15 resize-y"
                />
              </>
            ) : (
              <>
                <FieldLabel text="리더에게 전하는 한마디" required />
                <textarea
                  value={leaderForm.leader_message}
                  onChange={handleLeaderChange}
                  rows={8}
                  placeholder="AI 시대에 필요한 리더의 지원/조직 변화에 대한 의견을 자유롭게 적어 주세요."
                  className="w-full rounded-2xl bg-[#f6f7f9] border border-black/10 px-4 py-3 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-[color:var(--key-primary)] focus:ring-2 focus:ring-[color:var(--key-primary)]/15 resize-y"
                />
              </>
            )}

            <div className="min-h-[1.25rem] text-sm">
              {errorMessage && (
                <p className="text-[color:var(--key-danger)]">{errorMessage}</p>
              )}
              {!errorMessage && successMessage && (
                <p className="text-slate-600">{successMessage}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className={`w-full py-4 rounded-3xl font-bold text-base transition-all duration-200 ${
                isSubmitting
                  ? "bg-slate-200 text-slate-400 cursor-wait"
                  : "bg-[color:var(--key-primary)] text-white hover:opacity-90"
              }`}
            >
              {isSubmitting ? "제출 중..." : "제출하기"}
            </button>
            <button
              type="button"
              onClick={() => navigate("/")}
              className="w-full py-3 rounded-3xl font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 transition-colors"
            >
              메인으로 돌아가기
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

function FieldLabel({ text, required = false, example = "" }) {
  return (
    <div className="flex flex-col gap-1">
      <p className="text-sm font-semibold text-slate-700">
        {text}
        {required ? <span className="text-[color:var(--key-danger)]"> *</span> : null}
      </p>
      {example ? <p className="text-xs text-slate-500">{example}</p> : null}
    </div>
  );
}
