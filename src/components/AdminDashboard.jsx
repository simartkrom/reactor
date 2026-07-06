import { useEffect, useState } from "react";
import { supabase } from "../supabaseClient";

export default function AdminDashboard() {
  const [results, setResults] = useState([]);

  useEffect(() => {
    if (!supabase) return;
    supabase.from("results").select("*").order("created_at", { ascending: false }).limit(100)
      .then(({ data }) => { if (data) setResults(data); });
  }, []);

  return (
    <div className="min-h-dvh bg-[var(--sk-ink)] text-white p-6">
      <h1 className="text-2xl font-bold mb-6">Admin Dashboard</h1>
      <div className="rounded-2xl bg-[var(--sk-ink-2)] border border-[var(--sk-border)] p-6">
        <h2 className="text-lg font-bold mb-4">최근 결과 ({results.length}건)</h2>
        {results.length === 0 ? (
          <p className="text-slate-400">결과 데이터가 없습니다.</p>
        ) : (
          <div className="space-y-2">
            {results.map((r, i) => (
              <div key={i} className="flex justify-between items-center py-2 border-b border-white/10">
                <span className="text-sm">{r.result_code}</span>
                <span className="text-xs text-slate-400">{r.user_type}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
