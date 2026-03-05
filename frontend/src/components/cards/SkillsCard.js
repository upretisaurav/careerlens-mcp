import ErrorCard from "./ErrorCard";

const trendColor = (trend) => {
  if (trend?.includes("hot")) return "#FF5C28";
  if (trend?.includes("rising")) return "#00D98B";
  if (trend?.includes("stable")) return "#6366F1";
  return "#4E5168";
};

export default function SkillsCard({ data }) {
  if (data.error) return <ErrorCard message={data.error} />;
  const { ranking, location } = data;
  return (
    <div className="result-card skills-card">
      <div className="card-header">
        <div className="card-icon-wrap" />
        <div className="card-header-text">
          <div className="card-title">Skill Demand Analysis</div>
          <div className="card-subtitle">
            {location} market · relative index
          </div>
        </div>
      </div>
      <div className="skills-bars">
        {ranking?.map((s, i) => (
          <div key={i} className="skill-row">
            <div className="skill-name">{s.skill}</div>
            <div className="skill-bar-track">
              <div
                className="skill-bar-fill"
                style={{
                  width: `${s.demand_score}%`,
                  background: trendColor(s.trend),
                }}
              />
            </div>
            <div className="skill-row-meta">
              <span className="skill-score">{s.demand_score}</span>
              <span className="skill-trend">{s.trend}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
