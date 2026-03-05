import ErrorCard from "./ErrorCard";

export default function ResumeCard({ data }) {
  if (data.error) return <ErrorCard message={data.error} />;
  const {
    ats_score,
    grade,
    summary,
    skill_analysis,
    suggestions,
    score_breakdown,
  } = data;
  const color =
    ats_score >= 85
      ? "#00D98B"
      : ats_score >= 70
        ? "#6366F1"
        : ats_score >= 50
          ? "#FFB800"
          : "#FF3B30";
  return (
    <div className="result-card resume-card">
      <div className="card-header">
        <div className="card-icon-wrap" />
        <div className="card-header-text">
          <div className="card-title">Resume ATS Score</div>
          <div className="card-subtitle">{grade}</div>
        </div>
        <div className="ats-score-ring" style={{ "--score-color": color }}>
          <span className="ats-score-num" style={{ color }}>
            {ats_score}
          </span>
          <span className="ats-score-denom">/100</span>
        </div>
      </div>
      <p className="card-summary">{summary}</p>
      <div className="score-breakdown">
        {Object.entries(score_breakdown || {}).map(([k, v]) => (
          <div key={k} className="breakdown-item">
            <span className="breakdown-label">{k.replace(/_/g, " ")}</span>
            <span className="breakdown-value">{v}</span>
          </div>
        ))}
      </div>
      {skill_analysis?.missing_skills?.length > 0 && (
        <div className="card-section">
          <div className="section-label">Missing skills</div>
          <div className="pill-row">
            {skill_analysis.missing_skills.map((s, i) => (
              <span key={i} className="pill pill-miss">
                {s}
              </span>
            ))}
          </div>
        </div>
      )}
      {skill_analysis?.matched_skills?.length > 0 && (
        <div className="card-section">
          <div className="section-label">Matched skills</div>
          <div className="pill-row">
            {skill_analysis.matched_skills.map((s, i) => (
              <span key={i} className="pill pill-match">
                {s}
              </span>
            ))}
          </div>
        </div>
      )}
      <div className="card-section">
        <div className="section-label">Suggestions</div>
        {suggestions?.map((s, i) => (
          <div key={i} className="suggestion-row">
            {s}
          </div>
        ))}
      </div>
    </div>
  );
}
