import { useState } from "react";

export default function AdminGate({ children }) {
  const [password, setPassword] = useState("");
  const [isAuthed, setIsAuthed] = useState(false);

  if (isAuthed) return children;

  return (
    <div className="min-h-dvh flex items-center justify-center bg-[var(--sk-ink)] text-white px-6">
      <div className="w-full max-w-sm flex flex-col gap-4">
        <h1 className="text-xl font-bold text-center">Admin</h1>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="비밀번호"
          className="rounded-xl bg-white/10 border border-white/20 px-4 py-3 text-white placeholder:text-white/40 focus:outline-none focus:border-white/50"
        />
        <button
          onClick={() => {
            if (password === "admin2030") setIsAuthed(true);
          }}
          className="py-3 rounded-xl bg-[color:var(--key-primary)] text-white font-bold hover:opacity-90"
        >
          로그인
        </button>
      </div>
    </div>
  );
}
