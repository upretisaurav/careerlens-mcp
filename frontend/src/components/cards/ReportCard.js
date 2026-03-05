import ErrorCard from "./ErrorCard";

export default function ReportCard({ data }) {
  if (data.error) return <ErrorCard message={data.error} />;
  const {
    report_for,
    salary_gap_analysis,
    salary_intelligence,
    top_job_matches,
    skill_demand_ranking,
    action_plan,
  } = data;
  const gapClass =
    salary_gap_analysis?.direction === "below"
      ? "gap-below"
      : salary_gap_analysis?.direction === "above"
        ? "gap-above"
        : "gap-ok";
  return (
    <div className="result-card report-card">
      <div className="card-header">
        <div className="card-icon-wrap" />
        <div className="card-header-text">
          <div className="card-title">Career Intelligence Report</div>
          <div className="card-subtitle">
            {report_for?.role} · {report_for?.location}
          </div>
        </div>
      </div>
      {salary_gap_analysis?.available && (
        <div className={`gap-banner ${gapClass}`}>
          <div className="gap-verdict">{salary_gap_analysis.verdict}</div>
          <div className="gap-message">{salary_gap_analysis.message}</div>
          <div className="gap-nums">
            <span>
              Your salary: <strong>{salary_gap_analysis.your_salary}</strong>
            </span>
            <span>
              Market median:{" "}
              <strong>{salary_gap_analysis.market_median}</strong>
            </span>
            <span>
              Gap:{" "}
              <strong>
                {salary_gap_analysis.gap_amount} (
                {salary_gap_analysis.gap_percentage})
              </strong>
            </span>
          </div>
        </div>
      )}
      {salary_intelligence && !salary_intelligence.error && (
        <div className="mini-salary-row">
          <span>
            Median <strong>{salary_intelligence.median}</strong>
          </span>
          <span className="divider" />
          <span>
            Range {salary_intelligence.p25_low_end} –{" "}
            {salary_intelligence.p75_high_end}
          </span>
          <span className="divider" />
          <span>{salary_intelligence.sample_size} listings</span>
        </div>
      )}
      {skill_demand_ranking?.length > 0 && (
        <div className="card-section">
          <div className="section-label">Your skills ranked by demand</div>
          {skill_demand_ranking.slice(0, 5).map((s, i) => (
            <div key={i} className="mini-skill-row">
              <span className="mini-rank">#{i + 1}</span>
              <span className="mini-skill-name">{s.skill}</span>
              <span className="mini-skill-score">{s.demand_score}</span>
              <span className="mini-skill-trend">{s.trend}</span>
            </div>
          ))}
        </div>
      )}
      {action_plan?.length > 0 && (
        <div className="card-section">
          <div className="section-label">Action Plan</div>
          {action_plan.map((a, i) => (
            <div key={i} className="action-row">
              {a}
            </div>
          ))}
        </div>
      )}
      {top_job_matches?.length > 0 && (
        <div className="card-section">
          <div className="section-label">Top job matches</div>
          {top_job_matches.map((job, i) => (
            <a
              key={i}
              href={job.apply_url}
              target="_blank"
              rel="noopener noreferrer"
              className="job-mini"
            >
              <div>
                <div className="job-mini-title">{job.title}</div>
                <div className="job-mini-meta">
                  {job.company} · {job.location}
                </div>
              </div>
              <span
                className={
                  job.salary === "Not disclosed" ? "muted" : "job-mini-salary"
                }
              >
                {job.salary}
              </span>
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
