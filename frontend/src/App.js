import { useState } from "react";
import "./App.css";
import { Analytics } from "@vercel/analytics/react";
import { SUGGESTIONS } from "./constants";
import ProfilePanel from "./components/ProfilePanel";
import MessageItem from "./components/MessageItem";
import ConfirmProfileModal from "./components/ConfirmProfileModal";
import useChat from "./hooks/useChat";
import useImport from "./hooks/useImport";

export default function App() {
  const [profile, setProfile] = useState({
    role: "",
    location: "United States",
    skills: [],
    current_salary: null,
    years_of_experience: null,
    remote: false,
  });

  const {
    messages,
    input,
    setInput,
    loading,
    bottomRef,
    textareaRef,
    sendMessage,
    handleKey,
    pushMsg,
    clearMessages,
  } = useChat({ profile });

  const {
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
  } = useImport({ profile, setProfile, pushMsg });

  const isEmpty = messages.length === 0;

  return (
    <div className="app">
      <Analytics />
      <ConfirmProfileModal
        data={modalData}
        onConfirm={handleConfirmProfile}
        onCancel={cancelModal}
      />
      <ProfilePanel
        profile={profile}
        onChange={setProfile}
        onClearChat={clearMessages}
        onCvUpload={handleCvUpload}
        onLinkedinImport={handleLinkedinImport}
        importLoading={importLoading}
        linkedinUrl={linkedinUrl}
        setLinkedinUrl={setLinkedinUrl}
        showLinkedin={showLinkedin}
        setShowLinkedin={setShowLinkedin}
        fileInputRef={fileInputRef}
      />

      <main className="chat-main">
        {isEmpty ? (
          <div className="empty-state">
            <div className="empty-glow" />
            <div className="empty-bolt" />
            <h1 className="empty-heading">
              What do you want to know
              <br />
              about your career?
            </h1>
            <p className="empty-sub">
              Real-time salary data, live jobs, skill trends &amp; resume
              scoring — all in one chat.
            </p>
            <div className="suggestion-grid">
              {SUGGESTIONS.map((s, i) => (
                <button
                  key={i}
                  className="suggestion-card"
                  onClick={() => sendMessage(s)}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="messages-wrap">
            {messages.map((msg) => (
              <MessageItem key={msg.id} msg={msg} />
            ))}
            {loading && (
              <div className="msg msg-assistant">
                <div className="avatar">CL</div>
                <div className="thinking-dots">
                  <span />
                  <span />
                  <span />
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        )}

        <div className="input-bar">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKey}
            placeholder="Ask anything about your career market..."
            disabled={loading}
            rows={1}
          />
          <button
            className="send-btn"
            onClick={() => sendMessage(input)}
            disabled={loading || !input.trim()}
          >
            ↑
          </button>
        </div>
      </main>
    </div>
  );
}
