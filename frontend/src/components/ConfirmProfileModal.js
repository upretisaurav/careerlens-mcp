export default function ConfirmProfileModal({ data, onConfirm, onCancel }) {
  if (!data) return null;
  const { extracted, source_url } = data;
  if (!extracted) return null;
  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal-box" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title">
            {source_url ? "LinkedIn Profile Extracted" : "CV Parsed"}
          </div>
          <div className="modal-subtitle">
            Review the data below before filling your profile
          </div>
        </div>
        <div className="modal-body">
          {extracted.name && (
            <div className="modal-field">
              <span className="modal-label">Name</span>
              <span className="modal-value">{extracted.name}</span>
            </div>
          )}
          <div className="modal-field">
            <span className="modal-label">Role</span>
            <span className="modal-value">{extracted.role || "—"}</span>
          </div>
          <div className="modal-field">
            <span className="modal-label">Location</span>
            <span className="modal-value">{extracted.location || "—"}</span>
          </div>
          <div className="modal-field">
            <span className="modal-label">Experience</span>
            <span className="modal-value">
              {extracted.years_of_experience
                ? `${extracted.years_of_experience} years`
                : "—"}
            </span>
          </div>
          <div className="modal-field">
            <span className="modal-label">Current Salary</span>
            <span className="modal-value">
              {extracted.current_salary
                ? `$${Number(extracted.current_salary).toLocaleString()}`
                : "Not found"}
            </span>
          </div>
          <div className="modal-field modal-field-tall">
            <span className="modal-label">Skills</span>
            <div className="modal-pills">
              {extracted.skills?.length > 0 ? (
                extracted.skills.map((s, i) => (
                  <span key={i} className="pill pill-match">
                    {s}
                  </span>
                ))
              ) : (
                <span className="muted">None detected</span>
              )}
            </div>
          </div>
          {extracted.summary && (
            <div className="modal-field modal-field-tall">
              <span className="modal-label">Summary</span>
              <span className="modal-value modal-summary">
                {extracted.summary}
              </span>
            </div>
          )}
          {extracted.recent_companies?.length > 0 && (
            <div className="modal-field">
              <span className="modal-label">Recent companies</span>
              <span className="modal-value">
                {extracted.recent_companies.join(" · ")}
              </span>
            </div>
          )}
        </div>
        <div className="modal-footer">
          <button className="btn-ghost" onClick={onCancel}>
            Cancel
          </button>
          <button className="btn-confirm" onClick={() => onConfirm(extracted)}>
            Fill Profile with This Data
          </button>
        </div>
      </div>
    </div>
  );
}
