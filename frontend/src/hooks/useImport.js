import { useState, useRef, useCallback } from "react";
import { API } from "../constants";
import { normalizeExtracted } from "../utils/normalizeExtracted";

/**
 * Manages CV upload, LinkedIn import, confirmation modal, and profile fill.
 *
 * @param {{ profile: object, setProfile: Function, pushMsg: Function }} opts
 */
export default function useImport({ profile, setProfile, pushMsg }) {
  const [modalData, setModalData] = useState(null);
  const [importLoading, setImportLoading] = useState("");
  const [linkedinUrl, setLinkedinUrl] = useState("");
  const [showLinkedin, setShowLinkedin] = useState(false);
  const fileInputRef = useRef(null);

  // ── CV Upload ──────────────────────────────────────────────────
  const handleCvUpload = useCallback(
    async (e) => {
      const file = e.target.files?.[0];
      if (!file) return;
      setImportLoading("cv");
      const form = new FormData();
      form.append("file", file);
      try {
        const res = await fetch(`${API}/tools/parse-cv`, {
          method: "POST",
          body: form,
        });
        const data = await res.json();
        if (data.error)
          pushMsg({
            type: "assistant",
            text: `CV parsing failed: ${data.error}`,
          });
        else {
          const raw = data.profile ?? data.extracted ?? data;
          setModalData({ extracted: normalizeExtracted(raw) });
        }
      } catch (err) {
        pushMsg({
          type: "assistant",
          text: `Could not reach backend: ${err.message}`,
        });
      } finally {
        setImportLoading("");
        e.target.value = "";
      }
    },
    [pushMsg],
  );

  // ── LinkedIn Import ────────────────────────────────────────────
  const handleLinkedinImport = useCallback(async () => {
    if (!linkedinUrl.trim()) return;
    setImportLoading("linkedin");
    try {
      const res = await fetch(`${API}/tools/parse-linkedin`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: linkedinUrl.trim() }),
      });
      const data = await res.json();
      if (data.error) {
        const isBlocked =
          data.error.toLowerCase().includes("999") ||
          data.error.toLowerCase().includes("automated");
        pushMsg({
          type: "assistant",
          text: isBlocked
            ? [
                `**LinkedIn blocked the request** (HTTP 999 — automated access detected).`,
                ``,
                `LinkedIn actively blocks scrapers. Here are your options:`,
                ``,
                `1. **Upload your CV instead** — click Upload CV in the sidebar`,
                `2. **Export from LinkedIn** — go to [linkedin.com/settings](https://www.linkedin.com/settings/) → Data privacy → Get a copy of your data → download the **Profile.csv**, then upload it as a file`,
                `3. **Fill the profile manually** — just type your role, skills, and experience directly in the sidebar`,
              ].join("\n")
            : `**LinkedIn import failed:** ${data.error}${data.suggestion ? `\n\n${data.suggestion}` : ""}`,
        });
      } else {
        const raw = data.profile ?? data.extracted ?? data;
        setModalData({
          extracted: normalizeExtracted(raw),
          source_url: linkedinUrl,
        });
        setShowLinkedin(false);
        setLinkedinUrl("");
      }
    } catch (err) {
      pushMsg({
        type: "assistant",
        text: `Could not reach backend: ${err.message}`,
      });
    } finally {
      setImportLoading("");
    }
  }, [linkedinUrl, pushMsg]);

  // ── Confirm profile fill ───────────────────────────────────────
  const handleConfirmProfile = useCallback(
    (extracted) => {
      setProfile((prev) => ({
        ...prev,
        role: extracted.role || prev.role,
        location: extracted.location || prev.location,
        skills: extracted.skills?.length ? extracted.skills : prev.skills,
        current_salary: extracted.current_salary || prev.current_salary,
        years_of_experience:
          extracted.years_of_experience || prev.years_of_experience,
      }));
      const source = modalData?.source_url ? "LinkedIn" : "CV";
      setModalData(null);
      pushMsg({
        type: "assistant",
        text: `Profile filled from your ${source}${
          extracted.name ? ` (${extracted.name})` : ""
        }. Want me to run a full career report based on your profile?`,
      });
    },
    [modalData, setProfile, pushMsg],
  );

  const cancelModal = useCallback(() => setModalData(null), []);

  return {
    modalData,
    importLoading,
    linkedinUrl,
    setLinkedinUrl,
    showLinkedin,
    setShowLinkedin,
    fileInputRef,
    handleCvUpload,
    handleLinkedinImport,
    handleConfirmProfile,
    cancelModal,
  };
}
