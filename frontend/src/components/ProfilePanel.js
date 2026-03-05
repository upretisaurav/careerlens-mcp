import { useState, useEffect } from "react";

export default function ProfilePanel({
  profile,
  onChange,
  onClearChat,
  onCvUpload,
  onLinkedinImport,
  importLoading,
  linkedinUrl,
  setLinkedinUrl,
  showLinkedin,
  setShowLinkedin,
  fileInputRef,
}) {
  const [skillsInput, setSkillsInput] = useState(
    profile.skills?.join(", ") || "",
  );

  useEffect(() => {
    setSkillsInput(profile.skills?.join(", ") || "");
  }, [profile.skills]);

  const handleSkillsChange = (e) => setSkillsInput(e.target.value);

  const handleSkillsBlur = () => {
    onChange({
      ...profile,
      skills: skillsInput
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean),
    });
  };

  return (
    <aside className="profile-panel">
      <div
        className="logo"
        onClick={onClearChat}
        title="Clear chat"
        style={{ cursor: "pointer" }}
      >
        <div className="logo-mark" />
        <div className="logo-text">CareerLens</div>
      </div>
      <div className="mcp-badge">MCP · Claude AI</div>

      <div className="import-row">
        <button
          className="import-btn"
          onClick={() => fileInputRef.current?.click()}
          disabled={!!importLoading}
        >
          {importLoading === "cv" ? (
            <span className="tool-spinner small" />
          ) : null}
          Upload CV
        </button>
        <button
          className="import-btn"
          onClick={() => setShowLinkedin((v) => !v)}
          disabled={!!importLoading}
        >
          {importLoading === "linkedin" ? (
            <span className="tool-spinner small" />
          ) : (
            "🔗"
          )}
          LinkedIn
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          style={{ display: "none" }}
          onChange={onCvUpload}
        />
      </div>

      {showLinkedin && (
        <div className="linkedin-row">
          <input
            value={linkedinUrl}
            onChange={(e) => setLinkedinUrl(e.target.value)}
            placeholder="linkedin.com/in/username"
            onKeyDown={(e) => e.key === "Enter" && onLinkedinImport()}
            autoFocus
          />
          <button
            className="linkedin-go"
            onClick={onLinkedinImport}
            disabled={!linkedinUrl.trim() || !!importLoading}
          >
            {importLoading === "linkedin" ? "…" : "→"}
          </button>
        </div>
      )}

      <div className="panel-section-label" style={{ marginTop: "20px" }}>
        Your Profile
      </div>

      <div className="form-group">
        <label>Role</label>
        <input
          value={profile.role}
          onChange={(e) => onChange({ ...profile, role: e.target.value })}
          placeholder="e.g. Software Engineer"
        />
      </div>
      <div className="form-group">
        <label>Location</label>
        <input
          value={profile.location}
          onChange={(e) => onChange({ ...profile, location: e.target.value })}
          placeholder="e.g. San Francisco, CA"
        />
      </div>
      <div className="form-group">
        <label>
          Skills <em>comma-separated</em>
        </label>
        <input
          value={skillsInput}
          onChange={handleSkillsChange}
          onBlur={handleSkillsBlur}
          placeholder="React, Python, AWS..."
        />
      </div>
      <div className="form-group">
        <label>
          Current Salary <em>USD/yr</em>
        </label>
        <input
          type="number"
          value={profile.current_salary || ""}
          onChange={(e) =>
            onChange({
              ...profile,
              current_salary: Number(e.target.value) || null,
            })
          }
          placeholder="e.g. 95000"
        />
      </div>
      <div className="form-group">
        <label>Years of Experience</label>
        <input
          type="number"
          value={profile.years_of_experience || ""}
          onChange={(e) =>
            onChange({
              ...profile,
              years_of_experience: Number(e.target.value) || null,
            })
          }
          placeholder="e.g. 4"
        />
      </div>
      <div className="form-group toggle-row">
        <label>Remote only</label>
        <button
          className={`toggle-btn ${profile.remote ? "active" : ""}`}
          onClick={() => onChange({ ...profile, remote: !profile.remote })}
        >
          <div className="toggle-thumb" />
        </button>
      </div>

      <div className="profile-tip">
        Fill in your profile so Claude has context for every question you ask.
      </div>
    </aside>
  );
}
