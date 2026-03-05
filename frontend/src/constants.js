export const API = process.env.REACT_APP_API_URL || "http://localhost:8000";

export const SUGGESTIONS = [
  "What should a Senior React Developer earn in NYC?",
  "Find remote Python backend jobs for my skills",
  "Compare demand: React vs Vue vs Angular vs Svelte",
  "Give me a full career report based on my profile",
];

export const TOOL_LABELS = {
  salary_benchmark: "Fetching live salary data...",
  job_search: "Searching job listings...",
  skill_demand: "Analysing skill demand...",
  resume_fit_score: "Scoring resume fit...",
  career_report: "Building career report...",
};
