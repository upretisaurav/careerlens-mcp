import ErrorCard from "./ErrorCard";

export default function JobsCard({ data }) {
  if (data.error) return <ErrorCard message={data.error} />;
  const { jobs, total_found, location } = data;
  return (
    <div className="result-card jobs-card">
      <div className="card-header">
        <div className="card-icon-wrap" />
        <div className="card-header-text">
          <div className="card-title">Live Job Listings</div>
          <div className="card-subtitle">
            {total_found} found · {location}
          </div>
        </div>
      </div>
      <div className="jobs-list">
        {jobs?.map((job, i) => (
          <a
            key={i}
            href={job.apply_url}
            target="_blank"
            rel="noopener noreferrer"
            className="job-card-item"
          >
            <div className="job-card-top">
              <span className="job-title">{job.title}</span>
              <span
                className={`job-salary-tag ${job.salary === "Not disclosed" ? "muted" : "has-salary"}`}
              >
                {job.salary}
              </span>
            </div>
            <div className="job-card-bottom">
              <span className="job-company">{job.company}</span>
              <span className="dot">·</span>
              <span className="job-location">{job.location}</span>
              {job.remote && <span className="remote-pill">Remote</span>}
              <span className="job-date">{job.posted_date}</span>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}
