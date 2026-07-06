import { useEffect, useMemo, useState } from "react";
import {
  Navigate,
  Route,
  Routes,
  useLocation,
  useNavigate,
  useParams,
} from "react-router-dom";
import Main from "./components/Main";
import Intro from "./components/Intro";
import Question from "./components/Question";
import Tiebreaker from "./components/Tiebreaker";
import Loading from "./components/Loading";
import Result from "./components/Result";
import OpenFeedbackForm from "./components/OpenFeedbackForm";
import AiColleagueForm from "./components/AiColleagueForm";
import PromptSetPage from "./components/PromptSetPage";
import { questions as allQuestions } from "./data/questions";
import {
  INITIAL_MEMBER_SCORE,
  calculateResult,
  applyTiebreakerPick,
  selectTiebreakerCandidates,
} from "./data/scoringMap";
import { supabase } from "./supabaseClient";

const MEMBER_COUNT = 22;

const STORAGE_KEY = "game_state_v1";

function loadGameState() {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.sessionStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function saveGameState(next) {
  if (typeof window === "undefined") return;
  try {
    window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  } catch {
    // ignore
  }
}

function clearGameState() {
  if (typeof window === "undefined") return;
  try {
    window.sessionStorage.removeItem(STORAGE_KEY);
  } catch {
    // ignore
  }
}

function QuestionsRoute({
  questions,
  currentIndex,
  selectedChoice,
  onChoose,
  onNext,
  onPrevious,
}) {
  const params = useParams();
  const idx = Number(params.index);
  const navigate = useNavigate();

  useEffect(() => {
    if (!Number.isFinite(idx)) {
      navigate("/questions/1", { replace: true });
      return;
    }
    const clamped = Math.min(Math.max(idx, 1), questions.length);
    if (idx !== clamped) navigate(`/questions/${clamped}`, { replace: true });
  }, [idx, navigate, questions.length]);

  if (!Number.isFinite(idx)) return null;
  const desiredIndex = Math.min(Math.max(idx, 1), questions.length) - 1;
  if (desiredIndex !== currentIndex) return null;

  return (
    <Question
      questions={questions}
      currentIndex={currentIndex}
      selectedChoice={selectedChoice}
      onChoose={onChoose}
      onNext={onNext}
      onPrevious={onPrevious}
    />
  );
}

export default function App() {
  const navigate = useNavigate();
  const location = useLocation();
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState([]);
  const [draftChoice, setDraftChoice] = useState(null);
  const [memberScore, setMemberScore] = useState({ ...INITIAL_MEMBER_SCORE });
  const [resultType, setResultType] = useState(null);
  const [pendingTiebreaker, setPendingTiebreaker] = useState(null);
  const [coTopSkills, setCoTopSkills] = useState([]);

  const [sessionId, setSessionId] = useState(() => {
    if (typeof window === "undefined") return null;
    return window.sessionStorage.getItem("session_id");
  });
  const [sessionCode, setSessionCode] = useState(() => {
    if (typeof window === "undefined") return "";
    return window.sessionStorage.getItem("session_code") || "";
  });
  const [isSessionValid, setIsSessionValid] = useState(() => {
    if (typeof window === "undefined") return false;
    return Boolean(window.sessionStorage.getItem("session_id"));
  });
  const [isValidatingSession, setIsValidatingSession] = useState(false);
  const [sessionError, setSessionError] = useState("");

  const questions = useMemo(
    () => allQuestions.slice(0, MEMBER_COUNT),
    [allQuestions],
  );

  useEffect(() => {
    if (typeof window === "undefined") return;
    const next = loadGameState();
    if (!next) return;

    setCurrentQuestionIndex(Number(next.currentQuestionIndex ?? 0));
    setAnswers(Array.isArray(next.answers) ? next.answers : []);
    setDraftChoice(next.draftChoice ?? null);
    setMemberScore(next.memberScore ?? { ...INITIAL_MEMBER_SCORE });
    setResultType(next.resultType ?? null);
    setPendingTiebreaker(
      Array.isArray(next.pendingTiebreaker) ? next.pendingTiebreaker : null,
    );
    setCoTopSkills(Array.isArray(next.coTopSkills) ? next.coTopSkills : []);
  }, []);

  useEffect(() => {
    saveGameState({
      currentQuestionIndex,
      answers,
      draftChoice,
      memberScore,
      resultType,
      pendingTiebreaker,
      coTopSkills,
    });
  }, [
    answers,
    currentQuestionIndex,
    draftChoice,
    memberScore,
    resultType,
    pendingTiebreaker,
    coTopSkills,
  ]);

  useEffect(() => {
    if (typeof window === "undefined") return;
    window.scrollTo({ top: 0, left: 0, behavior: "auto" });
  }, [location.pathname]);

  useEffect(() => {
    if (!supabase || !resultType || !sessionId) return;

    const saveResult = async () => {
      try {
        const payload = {
          session_id: sessionId,
          user_type: "member",
          result_code: resultType.memberResult,
          leader_badge: null,
        };

        const { error } = await supabase.from("results").insert(payload);
        if (error) {
          // eslint-disable-next-line no-console
          console.error("[Supabase] 결과 저장 실패:", error.message);
        }
      } catch (err) {
        // eslint-disable-next-line no-console
        console.error("[Supabase] 결과 저장 중 예기치 못한 오류:", err);
      }
    };

    saveResult();
  }, [resultType, sessionId]);

  const handleValidateSession = async () => {
    if (!supabase) {
      setSessionError(
        "Supabase 설정을 찾을 수 없습니다. VITE_SUPABASE_URL / VITE_SUPABASE_ANON_KEY를 확인해 주세요.",
      );
      setIsSessionValid(false);
      return;
    }

    const trimmed = sessionCode.trim();
    if (!trimmed) {
      setSessionError("차수 코드를 입력해 주세요.");
      setIsSessionValid(false);
      return;
    }

    setIsValidatingSession(true);
    setSessionError("");

    try {
      const { data, error } = await supabase
        .from("sessions")
        .select("id, session_code")
        .eq("session_code", trimmed)
        .maybeSingle();

      if (error) throw error;

      if (!data) {
        setIsSessionValid(false);
        setSessionId(null);
        if (typeof window !== "undefined") {
          window.sessionStorage.removeItem("session_id");
          window.sessionStorage.removeItem("session_code");
        }
        setSessionError("해당 차수 코드를 찾을 수 없습니다.");
        return;
      }

      setSessionId(data.id);
      setIsSessionValid(true);
      if (typeof window !== "undefined") {
        window.sessionStorage.setItem("session_id", data.id);
        window.sessionStorage.setItem("session_code", data.session_code);
      }
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error("[Supabase] 세션 코드 조회 실패:", err);
      setIsSessionValid(false);
      setSessionError("차수 코드 확인 중 오류가 발생했습니다.");
    } finally {
      setIsValidatingSession(false);
    }
  };

  const handleStart = () => {
    if (!isSessionValid || !sessionId) {
      setSessionError(
        "게임을 시작하기 전에 유효한 차수 코드를 먼저 확인해 주세요.",
      );
      return;
    }
    setCurrentQuestionIndex(0);
    setAnswers([]);
    setDraftChoice(null);
    setMemberScore({ ...INITIAL_MEMBER_SCORE });
    setResultType(null);
    setPendingTiebreaker(null);
    setCoTopSkills([]);
    clearGameState();
    navigate("/guide");
  };

  const handleProceedIntro = () => {
    setDraftChoice(null);
    navigate("/questions/1");
  };

  const handleGoPromptSet = () => {
    navigate("/prompt-set");
  };

  const handleGoCanvasForm = () => {
    navigate("/open-feedback/canvas");
  };

  const handleGoAiColleagueForm = () => {
    navigate("/ai-colleague");
  };

  function applyOptionDelta(member, option, delta) {
    const nextMember = { ...member };
    if (option?.skill) nextMember[option.skill] += delta;
    return nextMember;
  }

  const handleNext = () => {
    if (!draftChoice) return;

    const currentQuestion = questions[currentQuestionIndex];
    const nextOption =
      draftChoice === "A" ? currentQuestion.optionA : currentQuestion.optionB;

    const prevAnswer = answers[currentQuestionIndex];
    const prevChoice =
      prevAnswer?.questionId === currentQuestion.id ? prevAnswer.choice : null;
    const prevOption =
      prevChoice === "A"
        ? currentQuestion.optionA
        : prevChoice === "B"
          ? currentQuestion.optionB
          : null;

    let score = memberScore;
    if (prevOption && prevChoice !== draftChoice) {
      score = applyOptionDelta(score, prevOption, -1);
    }
    if (!prevOption || prevChoice !== draftChoice) {
      score = applyOptionDelta(score, nextOption, +1);
    }

    const nextAnswers = [...answers];
    nextAnswers[currentQuestionIndex] = {
      questionId: currentQuestion.id,
      choice: draftChoice,
    };

    setAnswers(nextAnswers);
    setMemberScore(score);

    const nextIndex = currentQuestionIndex + 1;
    if (nextIndex < questions.length) {
      setCurrentQuestionIndex(nextIndex);
      const nextQ = questions[nextIndex];
      const existing = nextAnswers[nextIndex];
      setDraftChoice(existing?.questionId === nextQ.id ? existing.choice : null);
      navigate(`/questions/${nextIndex + 1}`);
    } else {
      const result = calculateResult(score);
      setDraftChoice(null);
      if (result.isTied) {
        setCoTopSkills(result.topSkillCandidates);
        setPendingTiebreaker(selectTiebreakerCandidates(result.topSkillCandidates));
        setResultType(null);
        navigate("/tiebreaker");
      } else {
        setCoTopSkills([]);
        setPendingTiebreaker(null);
        setResultType(result);
        navigate("/loading");
      }
    }
  };

  const handleTiebreakerSubmit = (skillCode) => {
    const nextScore = applyTiebreakerPick(memberScore, skillCode);
    const result = calculateResult(nextScore, { tieResolution: "random" });
    setMemberScore(nextScore);
    setResultType(result);
    navigate("/loading");
  };

  const handlePrevious = () => {
    if (currentQuestionIndex <= 0) {
      setDraftChoice(null);
      navigate("/guide");
      return;
    }
    const nextIndex = currentQuestionIndex - 1;
    setCurrentQuestionIndex(nextIndex);
    const prevQ = questions[nextIndex];
    const existing = answers[nextIndex];
    setDraftChoice(existing?.questionId === prevQ.id ? existing.choice : null);
    navigate(`/questions/${nextIndex + 1}`);
  };

  const handleRestart = () => {
    clearGameState();
    setCurrentQuestionIndex(0);
    setAnswers([]);
    setDraftChoice(null);
    setMemberScore({ ...INITIAL_MEMBER_SCORE });
    setResultType(null);
    setPendingTiebreaker(null);
    setCoTopSkills([]);
    navigate("/");
  };

  return (
    <Routes>
      <Route
        path="/"
        element={
          <Main
            sessionCode={sessionCode}
            setSessionCode={setSessionCode}
            onValidateSession={handleValidateSession}
            isSessionValid={isSessionValid}
            isValidatingSession={isValidatingSession}
            sessionError={sessionError}
            onStart={handleStart}
            onGoPromptSet={handleGoPromptSet}
            onGoCanvasForm={handleGoCanvasForm}
            onGoAiColleagueForm={handleGoAiColleagueForm}
          />
        }
      />
      <Route path="/prompt-set" element={<PromptSetPage />} />
      <Route
        path="/open-feedback/canvas"
        element={<OpenFeedbackForm mode="canvas" sessionId={sessionId} />}
      />
      <Route
        path="/open-feedback/leader"
        element={<OpenFeedbackForm mode="leader" sessionId={sessionId} />}
      />
      <Route
        path="/ai-colleague"
        element={<AiColleagueForm sessionId={sessionId} />}
      />
      <Route path="/guide" element={<Intro onProceed={handleProceedIntro} />} />
      <Route
        path="/questions/:index"
        element={
          <QuestionsRoute
            questions={questions}
            currentIndex={currentQuestionIndex}
            selectedChoice={draftChoice}
            onChoose={setDraftChoice}
            onNext={handleNext}
            onPrevious={handlePrevious}
          />
        }
      />
      <Route
        path="/tiebreaker"
        element={
          pendingTiebreaker && pendingTiebreaker.length > 1 ? (
            <Tiebreaker
              candidates={pendingTiebreaker}
              onSubmit={handleTiebreakerSubmit}
            />
          ) : resultType ? (
            <Navigate to="/result" replace />
          ) : (
            <Navigate to="/" replace />
          )
        }
      />
      <Route
        path="/loading"
        element={
          <LoadingRedirect
            hasResult={Boolean(resultType)}
            onDone={() => navigate("/result", { replace: true })}
          />
        }
      />
      <Route
        path="/result"
        element={
          resultType ? (
            <Result
              resultType={resultType}
              memberScore={memberScore}
              coTopSkills={coTopSkills}
              onRestart={handleRestart}
            />
          ) : (
            <Navigate to="/" replace />
          )
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function LoadingRedirect({ hasResult, onDone }) {
  useEffect(() => {
    if (!hasResult) return;
    const t = setTimeout(() => onDone(), 600);
    return () => clearTimeout(t);
  }, [hasResult, onDone]);

  return <Loading />;
}
