import SalaryCard from "./cards/SalaryCard";
import JobsCard from "./cards/JobsCard";
import SkillsCard from "./cards/SkillsCard";
import ResumeCard from "./cards/ResumeCard";
import ReportCard from "./cards/ReportCard";

export default function ToolResultCard({ tool, result }) {
  if (tool === "salary_benchmark") return <SalaryCard data={result} />;
  if (tool === "job_search") return <JobsCard data={result} />;
  if (tool === "skill_demand") return <SkillsCard data={result} />;
  if (tool === "resume_fit_score") return <ResumeCard data={result} />;
  if (tool === "career_report") return <ReportCard data={result} />;
  return (
    <div className="result-card">
      <pre className="raw-json">{JSON.stringify(result, null, 2)}</pre>
    </div>
  );
}
