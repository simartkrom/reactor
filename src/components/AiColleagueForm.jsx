import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "../supabaseClient";

const INITIAL = {
  colleague_name: "",
  colleague_role: "",
  expected_outcomes: "",
  background_context: "",
  do_and_donts: "",
};

export default function AiColleagueForm({ sessionId }) {
  const navigate = useNavigate();
  const [form, setForm] = useState(INITIAL);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const handleChange = (field) => (event) => {
    setForm((prev) => ({ ...prev, [field]: event.target.value }));
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

    if (
      !form.colleague_name.trim() ||
      !form.colleague_role.trim() ||
      !form.expected_outcomes.trim() ||
      !form.background_context.trim() ||
      !form.do_and_donts.trim()
    ) {
      setErrorMessage("모든 항목을 작성해 주세요.");
      return;
    }

    setIsSubmitting(true);
    try {
      const payload = {
        session_id: sessionId,
        colleague_name: form.colleague_name.trim(),
        colleague_role: form.colleague_role.trim(),
        expected_outcomes: form.expected_outcomes.trim(),
        background_context: form.background_context.trim(),
        do_and_donts: form.do_and_donts.trim(),
      };

      const { error } = await supabase
        .from("ai_colleague_profiles")
        .insert(payload);
      if (error) throw error;

      setSuccessMessage("제출이 완료되었습니다. 감사합니다!");
      if (typeof window !== "undefined") {
        window.alert("제출이 완료되었습니다!");
      }
      setForm(INITIAL);
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error("[Supabase] AI 동료 설문 저장 실패:", err);
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
            워크플로우 재설계
          </h1>
          <p className="text-slate-600 text-sm leading-relaxed mt-2">
            AI 동료 설정에 필요한 항목을 작성해 주세요. 제출 내용은 차수별로
            안전하게 저장됩니다.
          </p>

          <form onSubmit={handleSubmit} className="mt-5 flex flex-col gap-4">
            <FieldLabel
              text="AI 동료의 이름"
              required
              example="예) 박원인TL, 김정산봇, 이캘린더 대리"
            />
            <textarea
              value={form.colleague_name}
              onChange={handleChange("colleague_name")}
              rows={2}
              className="w-full rounded-2xl bg-[#f6f7f9] border border-black/10 px-4 py-3 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-[color:var(--key-primary)] focus:ring-2 focus:ring-[color:var(--key-primary)]/15 resize-y"
            />

            <FieldLabel
              text="위임 업무 및 기대하는 역할"
              required
              example="예) 회의록 정리, 초안 작성, 데이터 해석 지원 등 맡기는 일과 기대 역할"
            />
            <textarea
              value={form.colleague_role}
              onChange={handleChange("colleague_role")}
              rows={3}
              className="w-full rounded-2xl bg-[#f6f7f9] border border-black/10 px-4 py-3 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-[color:var(--key-primary)] focus:ring-2 focus:ring-[color:var(--key-primary)]/15 resize-y"
            />

            <FieldLabel
              text="업무 결과물 및 예상되는 효과"
              required
              example="예) 주간 리포트 초안, 의사결정 시간 단축, 반복 업무 30% 절감 등"
            />
            <textarea
              value={form.expected_outcomes}
              onChange={handleChange("expected_outcomes")}
              rows={3}
              className="w-full rounded-2xl bg-[#f6f7f9] border border-black/10 px-4 py-3 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-[color:var(--key-primary)] focus:ring-2 focus:ring-[color:var(--key-primary)]/15 resize-y"
            />

            <FieldLabel
              text="배경지식 및 참고자료"
              required
              example="예) 우리 팀 산업, 용어 정의, 현재 진행 중인 과제, 참고 링크/문서"
            />
            <textarea
              value={form.background_context}
              onChange={handleChange("background_context")}
              rows={5}
              className="w-full rounded-2xl bg-[#f6f7f9] border border-black/10 px-4 py-3 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-[color:var(--key-primary)] focus:ring-2 focus:ring-[color:var(--key-primary)]/15 resize-y"
            />

            <FieldLabel
              text="Do & Don'ts"
              required
              example="예) Do: 출처를 항상 표기 / Don't: 확정되지 않은 정보를 사실처럼 말하지 말 것"
            />
            <textarea
              value={form.do_and_donts}
              onChange={handleChange("do_and_donts")}
              rows={5}
              className="w-full rounded-2xl bg-[#f6f7f9] border border-black/10 px-4 py-3 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-[color:var(--key-primary)] focus:ring-2 focus:ring-[color:var(--key-primary)]/15 resize-y"
            />

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
        {required ? (
          <span className="text-[color:var(--key-danger)]"> *</span>
        ) : null}
      </p>
      {example ? <p className="text-xs text-slate-500">{example}</p> : null}
    </div>
  );
}
