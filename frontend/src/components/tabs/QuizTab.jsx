import { useState } from "react";
import { CheckCircle2, XCircle, RotateCcw } from "lucide-react";

const DIFF_COLOR = { easy: "var(--success)", medium: "var(--warning)", hard: "var(--accent)" };

export default function QuizTab({ video }) {
  const quiz = video.quiz || [];
  const [answers, setAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);

  if (!quiz.length) return <Empty label="No quiz generated yet." />;

  const score = quiz.filter((q, i) => answers[i] === q.correct_index).length;

  const reset = () => { setAnswers({}); setSubmitted(false); };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      {/* Score bar */}
      {submitted && (
        <div className="neu-card" style={{ padding: 24, textAlign: "center" }}>
          <div className="font-display" style={{ fontSize: "2.5rem", fontWeight: 700, color: "var(--brand)" }}>
            {score}/{quiz.length}
          </div>
          <p className="text-muted" style={{ marginBottom: 16 }}>
            {score === quiz.length ? "Perfect score! 🎉" : score >= quiz.length * 0.7 ? "Great job! 👍" : "Keep practicing! 💪"}
          </p>
          <button className="neu-btn" onClick={reset} style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
            <RotateCcw size={15} /> Retry Quiz
          </button>
        </div>
      )}

      {quiz.map((q, qi) => {
        const chosen = answers[qi];
        const correct = q.correct_index;
        const isCorrect = chosen === correct;

        return (
          <div key={qi} className="neu-card" style={{ padding: 24 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 14 }}>
              <p style={{ fontWeight: 600, fontSize: "0.95rem", lineHeight: 1.5, flex: 1 }}>
                <span className="text-brand">Q{qi + 1}. </span>{q.question}
              </p>
              <span className="badge" style={{
                background: `${DIFF_COLOR[q.difficulty]}22`,
                color: DIFF_COLOR[q.difficulty] || "var(--text-muted)",
                marginLeft: 12, flexShrink: 0,
              }}>
                {q.difficulty}
              </span>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {q.options.map((opt, oi) => {
                let bg = "var(--bg-elevated)";
                let border = "1px solid var(--border)";
                let color = "var(--text)";
                if (submitted) {
                  if (oi === correct) { bg = "rgba(67,217,173,0.12)"; border = "1px solid var(--success)"; color = "var(--success)"; }
                  else if (oi === chosen && !isCorrect) { bg = "rgba(255,101,132,0.12)"; border = "1px solid var(--accent)"; color = "var(--accent)"; }
                } else if (chosen === oi) {
                  bg = "rgba(108,99,255,0.12)"; border = "1px solid var(--brand)"; color = "var(--brand)";
                }

                return (
                  <button key={oi} onClick={() => !submitted && setAnswers({ ...answers, [qi]: oi })}
                    style={{
                      background: bg, border, borderRadius: 10, color,
                      cursor: submitted ? "default" : "pointer",
                      display: "flex", alignItems: "center", gap: 10,
                      padding: "10px 14px", textAlign: "left", fontSize: "0.88rem",
                      transition: "all 0.2s",
                    }}>
                    <span style={{ width: 22, height: 22, borderRadius: "50%", border: `2px solid ${color}`,
                      display: "flex", alignItems: "center", justifyContent: "center", fontSize: "0.75rem", flexShrink: 0 }}>
                      {String.fromCharCode(65 + oi)}
                    </span>
                    {opt}
                    {submitted && oi === correct && <CheckCircle2 size={15} style={{ marginLeft: "auto" }} />}
                    {submitted && oi === chosen && !isCorrect && <XCircle size={15} style={{ marginLeft: "auto" }} />}
                  </button>
                );
              })}
            </div>

            {submitted && q.explanation && (
              <div style={{ marginTop: 12, padding: "10px 14px", borderRadius: 10,
                background: "rgba(108,99,255,0.08)", border: "1px solid rgba(108,99,255,0.2)",
                fontSize: "0.83rem", color: "var(--text-muted)", lineHeight: 1.6 }}>
                💡 {q.explanation}
              </div>
            )}
          </div>
        );
      })}

      {!submitted && Object.keys(answers).length > 0 && (
        <button className="btn-brand" onClick={() => setSubmitted(true)}
          style={{ alignSelf: "center", padding: "12px 40px" }}>
          Submit Quiz
        </button>
      )}
    </div>
  );
}

function Empty({ label }) {
  return (
    <div className="neu-card" style={{ padding: 48, textAlign: "center" }}>
      <p style={{ fontSize: "2rem", marginBottom: 8 }}>🧠</p>
      <p className="text-muted">{label}</p>
    </div>
  );
}
