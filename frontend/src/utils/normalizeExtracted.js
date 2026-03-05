/**
 * @typedef {{ name?: string, role?: string, location?: string,
 *             skills?: string[], years_of_experience?: number|null,
 *             current_salary?: number|null, summary?: string,
 *             recent_companies?: string[] }} ExtractedProfile
 *
 * @typedef {{ extracted: ExtractedProfile, source_url?: string }} ModalData
 */

/**
 * Normalises a raw backend profile object (CV or LinkedIn) into
 * the consistent ExtractedProfile shape the modal expects.
 * @param {Record<string,any>} raw
 * @returns {ExtractedProfile}
 */
export function normalizeExtracted(raw) {
  return {
    name: raw.name,
    role: raw.role || raw.current_role || raw.target_role,
    location: raw.location,
    skills: raw.skills ?? [],
    years_of_experience: raw.years_of_experience ?? null,
    current_salary: raw.current_salary ?? null,
    summary: raw.summary,
    recent_companies:
      raw.recent_companies ??
      (raw.experience ?? [])
        .map((/** @type {any} */ e) => e.company)
        .filter(Boolean),
  };
}
