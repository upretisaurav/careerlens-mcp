import ErrorCard from "./ErrorCard";

export default function SalaryCard({ data }) {
  if (data.error) return <ErrorCard message={data.error} />;
  const { role, location, salary_stats, sample_size, sample_jobs } = data;
  return (
    <div className="result-card salary-card">
      <div className="card-header">
        <div className="card-icon-wrap" />
        <div className="card-header-text">
          <div className="card-title">Salary Benchmark</div>
          <div className="card-subtitle">
            {role} · {location}
          </div>
        </div>
        <div className="badge">{sample_size} listings</div>
      </div>
      <div className="salary-stats">
        <div className="stat-box">
          <div className="stat-label">25th %ile</div>
          <div className="stat-value low">{salary_stats?.p25_low_end}</div>
        </div>
        <div className="stat-box median-box">
          <div className="stat-label">Median</div>
          <div className="stat-value median">{salary_stats?.median}</div>
          <div className="median-tag">market midpoint</div>
        </div>
        <div className="stat-box">
          <div className="stat-label">75th %ile</div>
          <div className="stat-value high">{salary_stats?.p75_high_end}</div>
        </div>
      </div>
      {sample_jobs?.length > 0 && (
        <div className="card-section">
          <div className="section-label">Sample listings</div>
          {sample_jobs.map((job, i) => (
            <a
              key={i}
              href={job.url}
              target="_blank"
              rel="noopener noreferrer"
              className="job-mini"
            >
              <span className="job-mini-company">{job.company}</span>
              <span className="job-mini-salary">{job.salary_range}</span>
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
