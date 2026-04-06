import React, { useEffect, useState } from "react";
import "./App.css";

export default function App() {
  const [userQuery, setUserQuery] = useState("");
  const [sessionId, setSessionId] = useState("");
  const [followupAnswer, setFollowupAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [response, setResponse] = useState(null);
  const [history, setHistory] = useState([]);
  const [activeTab, setActiveTab] = useState("summary");

  const [authMode, setAuthMode] = useState("login");
  const [token, setToken] = useState(localStorage.getItem("agex_token") || "");
  const [currentUser, setCurrentUser] = useState(
    JSON.parse(localStorage.getItem("agex_user") || "null"),
  );
  const [authName, setAuthName] = useState("");
  const [authEmail, setAuthEmail] = useState("");
  const [authPassword, setAuthPassword] = useState("");
  const [authLoading, setAuthLoading] = useState(false);
  const [authError, setAuthError] = useState("");

  const [savedChats, setSavedChats] = useState([]);
  const [localChats, setLocalChats] = useState([]);
  const [currentChatId, setCurrentChatId] = useState("");

  const authUser = new URLSearchParams(window.location.search).get("authuser");
  const authSuffix = authUser ? `?authuser=${authUser}` : "";
  const apiUrl = (path) => `/api${path}${authSuffix}`;

  const apiUrlWithToken = (path, tokenValue) => {
    const hasQuery = path.includes("?");
    const base = `/api${path}${hasQuery ? "&" : "?"}token=${encodeURIComponent(
      tokenValue,
    )}`;
    return authUser ? `${base}&authuser=${authUser}` : base;
  };

  const pushSystemMessage = (data) => {
    let text = "Response received.";

    if (data?.status === "need_followup") {
      text = data.followup_question || "I need one more detail.";
    } else if (data?.status === "complete") {
      text = data.message || "I’ve prepared your tax planning summary.";
    } else if (data?.status === "general") {
      text = data.message;
    } else if (data?.message) {
      text = data.message;
    }

    return {
      type: "system",
      text,
      data,
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };
  };

  const getChatTitle = (messages) => {
    const firstUserMessage = messages.find((m) => m.type === "user");
    if (!firstUserMessage?.text) return "New Chat";
    return firstUserMessage.text.slice(0, 40);
  };

  const buildChatPreview = (
    messages,
    existingId = "",
    summaryOverride = null,
  ) => {
    return {
      id: existingId || `local-${Date.now()}`,
      title: getChatTitle(messages),
      messages,
      updated_at: new Date().toISOString(),
      summary: summaryOverride || response?.summary || {},
      isLocal: true,
    };
  };

  const upsertLocalChat = (
    messages,
    existingId = "",
    summaryOverride = null,
  ) => {
    const preview = buildChatPreview(messages, existingId, summaryOverride);

    setLocalChats((prev) => {
      const filtered = prev.filter((chat) => chat.id !== preview.id);
      return [preview, ...filtered];
    });

    return preview.id;
  };

  const loadSavedChats = async () => {
    if (!token) return;

    try {
      const res = await fetch(apiUrlWithToken("/chats/list", token), {
        method: "GET",
      });

      const data = await res.json();

      if (res.ok) {
        setSavedChats(data.chats || []);
      } else {
        console.error("Failed to load chats:", data);
      }
    } catch (err) {
      console.error("Failed to load chats", err);
    }
  };

  const saveCurrentChat = async (
    messagesToSave,
    summaryToSave = null,
    activeLocalId = "",
  ) => {
    if (!token || !messagesToSave.length) return;

    try {
      const title = getChatTitle(messagesToSave);

      const payload = {
        token: String(token).trim(),
        chat_id:
          currentChatId && !String(currentChatId).startsWith("local-")
            ? currentChatId
            : null,
        title,
        messages: messagesToSave,
        summary: summaryToSave || response?.summary || {},
      };

      console.log("Saving chat payload:", payload);

      const res = await fetch(apiUrl("/chats/save"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      console.log("Save chat response:", data);

      if (res.ok) {
        const newId = data.chat.id;

        setLocalChats((prev) =>
          prev.filter((chat) => chat.id !== (activeLocalId || currentChatId)),
        );

        setCurrentChatId(newId);
        await loadSavedChats();
      } else {
        console.error("Save failed:", data);
      }
    } catch (err) {
      console.error("Failed to save chat", err);
    }
  };

  const mergeIntoResponse = (prev, data) => {
    if (!prev) return data;

    return {
      ...prev,
      ...data,

      status: data.status || prev.status,
      followup_question: data.followup_question || prev.followup_question || "",
      session_id: data.session_id || prev.session_id || "",

      profile:
        data.profile && Object.keys(data.profile).length > 0
          ? {
              ...(prev.profile || {}),
              ...data.profile,
            }
          : prev.profile || {},

      summary:
        data.summary && Object.keys(data.summary).length > 0
          ? {
              ...(prev.summary || {}),
              ...data.summary,
            }
          : prev.summary || {},

      tax_rules_considered:
        Array.isArray(data.tax_rules_considered) &&
        data.tax_rules_considered.length > 0
          ? data.tax_rules_considered
          : prev.tax_rules_considered || [],

      recommendations:
        Array.isArray(data.recommendations) && data.recommendations.length > 0
          ? data.recommendations
          : prev.recommendations || [],

      action_tasks:
        Array.isArray(data.action_tasks) && data.action_tasks.length > 0
          ? data.action_tasks
          : prev.action_tasks || [],

      document_checklist:
        Array.isArray(data.document_checklist) &&
        data.document_checklist.length > 0
          ? data.document_checklist
          : prev.document_checklist || [],

      investment_suggestions:
        data.investment_suggestions &&
        Object.keys(data.investment_suggestions).length > 0
          ? data.investment_suggestions
          : prev.investment_suggestions || {},

      document_checklist_mcp:
        data.document_checklist_mcp &&
        Object.keys(data.document_checklist_mcp).length > 0
          ? data.document_checklist_mcp
          : prev.document_checklist_mcp || {},

      calendar_reminder:
        data.calendar_reminder && Object.keys(data.calendar_reminder).length > 0
          ? data.calendar_reminder
          : prev.calendar_reminder || {},
    };
  };

  const loadOneChat = async (chatId) => {
    if (!token) return;

    try {
      const res = await fetch(apiUrlWithToken(`/chats/${chatId}`, token), {
        method: "GET",
      });

      const data = await res.json();

      if (res.ok) {
        setCurrentChatId(data.chat.id);
        setHistory(data.chat.messages || []);
        setResponse(
          data.chat.summary
            ? {
                status: "complete",
                summary: data.chat.summary,
                profile: data.chat.summary,
              }
            : null,
        );
        setSessionId("");
        setFollowupAnswer("");
      } else {
        console.error("Failed to load chat:", data);
      }
    } catch (err) {
      console.error("Failed to load chat", err);
    }
  };

  const deleteOneChat = async (chatId, e) => {
    e.stopPropagation();

    if (!token) return;

    try {
      const res = await fetch(apiUrlWithToken(`/chats/${chatId}`, token), {
        method: "DELETE",
      });

      const data = await res.json().catch(() => null);

      if (res.ok) {
        if (currentChatId === chatId) {
          handleNewChat();
        }
        await loadSavedChats();
      } else {
        console.error("Failed to delete chat:", data);
      }
    } catch (err) {
      console.error("Failed to delete chat", err);
    }
  };

  const handleNewChat = () => {
    setUserQuery("");
    setSessionId("");
    setFollowupAnswer("");
    setLoading(false);
    setError("");
    setResponse(null);
    setHistory([]);
    setCurrentChatId("");
    setActiveTab("summary");
  };

  useEffect(() => {
    if (token) {
      loadSavedChats();
    } else {
      setSavedChats([]);
    }
  }, [token]);

  const handleRegister = async () => {
    setAuthLoading(true);
    setAuthError("");

    try {
      const res = await fetch(apiUrl("/auth/register"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: authName,
          email: authEmail,
          password: authPassword,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Registration failed");
      }

      localStorage.setItem("agex_token", data.access_token);
      localStorage.setItem("agex_user", JSON.stringify(data.user));

      setToken(data.access_token);
      setCurrentUser(data.user);
      setAuthName("");
      setAuthEmail("");
      setAuthPassword("");
      setAuthError("");

      window.location.reload();
    } catch (err) {
      setAuthError(err.message);
    } finally {
      setAuthLoading(false);
    }
  };

  const handleLogin = async () => {
    setAuthLoading(true);
    setAuthError("");

    try {
      const res = await fetch(apiUrl("/auth/login"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: authEmail,
          password: authPassword,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Login failed");
      }

      localStorage.setItem("agex_token", data.access_token);
      localStorage.setItem("agex_user", JSON.stringify(data.user));

      setToken(data.access_token);
      setCurrentUser(data.user);
      setAuthEmail("");
      setAuthPassword("");
      setAuthError("");

      window.location.reload();
    } catch (err) {
      setAuthError(err.message);
    } finally {
      setAuthLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("agex_token");
    localStorage.removeItem("agex_user");
    setToken("");
    setCurrentUser(null);
    setSavedChats([]);
    window.location.reload();
  };

  const callAnalyze = async () => {
    if (!userQuery.trim()) return;

    setLoading(true);
    setError("");

    const userMessage = {
      type: "user",
      text: userQuery,
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };

    try {
      const res = await fetch(apiUrl("/analyze"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_query: userQuery,
          sessionId: sessionId || null,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Analyze request failed");
      }

      const newHistory = [...history, userMessage, pushSystemMessage(data)];
      const summaryToSave = {
        ...(response?.summary || {}),
        ...(response?.profile || {}),
        ...(data.summary || {}),
        ...(data.profile || {}),
      };

      setResponse((prev) => mergeIntoResponse(prev, data));
      setHistory(newHistory);

      let activeId = currentChatId;

      if (!activeId) {
        activeId = upsertLocalChat(newHistory, "", summaryToSave);
        setCurrentChatId(activeId);
      } else {
        upsertLocalChat(newHistory, activeId, summaryToSave);
      }

      if (data.session_id) {
        setSessionId(data.session_id);
      }

      setUserQuery("");

      if (data.status === "complete") {
        setActiveTab("summary");
      }

      if (token) {
        await saveCurrentChat(newHistory, summaryToSave, activeId);
      }
    } catch (e) {
      setError(e.message || "Could not connect to AGEX API.");
    } finally {
      setLoading(false);
    }
  };

  const callFollowup = async () => {
    if (!sessionId) {
      setError("No active session found.");
      return;
    }

    if (!followupAnswer.trim()) return;

    setLoading(true);
    setError("");

    const userMessage = {
      type: "user",
      text: followupAnswer,
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };

    try {
      const res = await fetch(apiUrl("/followup"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          session_id: sessionId,
          user_answer: followupAnswer,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Follow-up request failed");
      }

      const newHistory = [...history, userMessage, pushSystemMessage(data)];
      const summaryToSave = {
        ...(response?.summary || {}),
        ...(response?.profile || {}),
        ...(data.summary || {}),
        ...(data.profile || {}),
      };

      setResponse((prev) => mergeIntoResponse(prev, data));
      setHistory(newHistory);

      let activeId = currentChatId;

      if (!activeId) {
        activeId = upsertLocalChat(newHistory, "", summaryToSave);
        setCurrentChatId(activeId);
      } else {
        upsertLocalChat(newHistory, activeId, summaryToSave);
      }

      if (data.session_id) {
        setSessionId(data.session_id);
      }

      if (data.status === "complete") {
        setActiveTab("summary");
      }

      setFollowupAnswer("");

      if (token) {
        await saveCurrentChat(newHistory, summaryToSave, activeId);
      }
    } catch (e) {
      setError(e.message || "Follow-up request failed.");
    } finally {
      setLoading(false);
    }
  };

  const liveProfile = {
    ...(response?.summary || {}),
    ...(response?.profile || {}),
  };

  const summary = liveProfile;
  const taxRules = response?.tax_rules_considered || response?.rules || [];
  const recommendations = response?.recommendations || [];
  const actionTasks = response?.action_tasks || response?.tasks || [];
  const documents = response?.document_checklist || response?.documents || [];

  const tabs = [
    { id: "summary", label: "Chat workspace" },
    { id: "rules", label: "Tax planning view" },
    { id: "tasks", label: "Workflow logs" },
    { id: "docs", label: "Documents" },
  ];

  const sidebarChats = token
    ? [
        ...localChats.filter((lc) => !savedChats.find((sc) => sc.id === lc.id)),
        ...savedChats,
      ]
    : localChats;

  const renderMessageBubble = (entry, index) => {
    const isUser = entry.type === "user";

    return (
      <div
        key={index}
        className={`chat-row ${isUser ? "chat-row-user" : "chat-row-system"}`}
      >
        <div
          className={`chat-bubble ${
            isUser ? "chat-bubble-user" : "chat-bubble-system"
          }`}
        >
          <div className="chat-text">{entry.text}</div>
          <div
            className={`chat-time ${
              isUser ? "chat-time-user" : "chat-time-system"
            }`}
          >
            {entry.timestamp}
          </div>
        </div>
      </div>
    );
  };

  const renderSummaryCard = (label, value) => (
    <div className="summary-card">
      <div className="summary-card-label">{label}</div>
      <div className="summary-card-value">{value ?? "—"}</div>
    </div>
  );

  const renderStringList = (items) => {
    if (!items?.length) {
      return <div className="empty-state-small">No items yet.</div>;
    }

    return (
      <div className="content-list">
        {items.map((item, index) => (
          <div key={index} className="content-list-item">
            <div className="content-list-text">{item}</div>
          </div>
        ))}
      </div>
    );
  };

  const renderRules = () => {
    if (!taxRules.length) {
      return <div className="empty-state-small">No rules retrieved yet.</div>;
    }

    return (
      <div className="content-list">
        {taxRules.map((rule, index) => (
          <div key={index} className="rule-card">
            <div className="rule-card-top">
              <div>
                <div className="rule-title">{rule.title}</div>
                <div className="rule-category">{rule.category}</div>
              </div>
              <div className="rule-badge">{rule.applies_to}</div>
            </div>
            <div className="rule-description">{rule.description}</div>
          </div>
        ))}
      </div>
    );
  };

  const renderRightPanel = () => {
    if (!response) {
      return (
        <div className="right-panel-empty">
          Ask AGEX a tax question to generate a planning summary, action steps,
          and document checklist.
        </div>
      );
    }

    if (response.status === "need_followup") {
      return (
        <div className="followup-card">
          <div className="section-kicker">Follow-up needed</div>
          <h2 className="section-title">AGEX needs one more detail</h2>
          <p className="section-copy">{response.followup_question}</p>

          <div className="profile-preview">
            <div className="profile-preview-kicker">
              Current detected profile
            </div>
            <div className="profile-preview-grid">
              <div>
                Persona: <span>{summary.persona || "unknown"}</span>
              </div>
              <div>
                Rent: <span>{String(summary.rent_paid ?? "—")}</span>
              </div>
              <div>
                GST: <span>{String(summary.has_gst_concern ?? "—")}</span>
              </div>
              <div>
                Investments: <span>{String(summary.has_investments ?? "—")}</span>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="right-panel-content">
        <div className="hero-card">
          <div className="hero-card-top">
            <div>
              <div className="section-kicker">AGEX Tax Plan</div>
              <h2 className="section-title">Your tax planning workspace</h2>
            </div>
            <div className="status-pill">Ready</div>
          </div>

          <div className="summary-grid">
            {renderSummaryCard("Persona", summary.persona || "—")}
            {renderSummaryCard("Pays Rent", String(summary.rent_paid ?? "—"))}
            {renderSummaryCard(
              "GST Concern",
              String(summary.has_gst_concern ?? "—"),
            )}
            {renderSummaryCard(
              "Investments",
              String(summary.has_investments ?? "—"),
            )}
          </div>
        </div>

        <div className="tabs-card">
          <div className="tabs-row">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`tab-button ${
                  activeTab === tab.id ? "tab-button-active" : ""
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        <div className="panel-card">
          {activeTab === "summary" && (
            <div>
              <div className="panel-section-title">Chat workspace summary</div>
              <div className="panel-section-content">
                {renderStringList(recommendations)}
              </div>
            </div>
          )}
          {activeTab === "rules" && renderRules()}
          {activeTab === "tasks" && renderStringList(actionTasks)}
          {activeTab === "docs" && renderStringList(documents)}
        </div>
      </div>
    );
  };

  return (
    <div className="agex-shell">
      <div className="agex-layout">
        <aside className="sidebar">
          <div>
            <div className="sidebar-brand-card">
              <div className="sidebar-kicker">AGEX</div>
              <div className="sidebar-title">Tax AI</div>
              <p className="sidebar-copy">
                Multi-agent tax planning assistant for salaried users and small
                businesses.
              </p>
            </div>

            <button className="new-chat-btn" onClick={handleNewChat}>
              + New Chat
            </button>

            {!token || !currentUser ? (
              <div className="sidebar-auth-card">
                <div className="sidebar-auth-title">Save your workspace</div>
                <div className="sidebar-auth-copy">
                  Sign in to save chats, tax cases, and planning history.
                </div>

                <div className="auth-toggle">
                  <button
                    className={
                      authMode === "login" ? "auth-tab active" : "auth-tab"
                    }
                    onClick={() => setAuthMode("login")}
                  >
                    Login
                  </button>
                  <button
                    className={
                      authMode === "register" ? "auth-tab active" : "auth-tab"
                    }
                    onClick={() => setAuthMode("register")}
                  >
                    Register
                  </button>
                </div>

                {authMode === "register" && (
                  <input
                    type="text"
                    placeholder="Name"
                    value={authName}
                    onChange={(e) => setAuthName(e.target.value)}
                    className="auth-input"
                  />
                )}

                <input
                  type="email"
                  placeholder="Email"
                  value={authEmail}
                  onChange={(e) => setAuthEmail(e.target.value)}
                  className="auth-input"
                />

                <input
                  type="password"
                  placeholder="Password"
                  value={authPassword}
                  onChange={(e) => setAuthPassword(e.target.value)}
                  className="auth-input"
                />

                {authError && <div className="auth-error">{authError}</div>}

                <button
                  className="auth-submit"
                  onClick={authMode === "login" ? handleLogin : handleRegister}
                  disabled={authLoading}
                >
                  {authLoading
                    ? "Please wait..."
                    : authMode === "login"
                    ? "Login"
                    : "Create Account"}
                </button>
              </div>
            ) : (
              <div className="sidebar-user-card">
                <div className="sidebar-user-name">{currentUser?.name}</div>
                <div className="sidebar-user-email">{currentUser?.email}</div>
                <button className="sidebar-logout" onClick={handleLogout}>
                  Logout
                </button>
              </div>
            )}

            {sidebarChats.length > 0 && (
              <div className="saved-chats-wrap">
                <div className="saved-chats-title">
                  {token ? "Saved Chats" : "Current Chats"}
                </div>

                <div className="saved-chat-list">
                  {sidebarChats.map((chat) => (
                    <div
                      key={chat.id}
                      className={`saved-chat-item ${
                        currentChatId === chat.id
                          ? "saved-chat-item-active"
                          : ""
                      }`}
                      onClick={() => {
                        if (token && !String(chat.id).startsWith("local-")) {
                          loadOneChat(chat.id);
                        } else {
                          setCurrentChatId(chat.id);
                          setHistory(chat.messages || []);
                          setResponse(
                            chat.summary
                              ? {
                                  status: "complete",
                                  summary: chat.summary,
                                  profile: chat.summary,
                                }
                              : null,
                          );
                          setSessionId("");
                          setFollowupAnswer("");
                        }
                      }}
                    >
                      <div className="saved-chat-text">{chat.title}</div>

                      <button
                        className="saved-chat-delete"
                        onClick={(e) => {
                          e.stopPropagation();

                          if (token && !String(chat.id).startsWith("local-")) {
                            deleteOneChat(chat.id, e);
                          } else {
                            setLocalChats((prev) =>
                              prev.filter((c) => c.id !== chat.id),
                            );
                            if (currentChatId === chat.id) {
                              handleNewChat();
                            }
                          }
                        }}
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="sidebar-footer-card">
            <div className="sidebar-footer-title">Demo mode</div>
            <div className="sidebar-footer-copy">
              Ask natural tax questions and AGEX will guide the conversation.
            </div>
          </div>
        </aside>

        <main className="main-layout">
          <section className="chat-panel">
            <div className="chat-header">
              <div>
                <div className="chat-header-title">AGEX Assistant</div>
                <div className="chat-header-subtitle">
                  Conversational tax planning
                </div>
              </div>
              <div className="chat-header-badge">Online</div>
            </div>

            <div className="chat-history">
              {history.length === 0 ? (
                <div className="empty-chat-state">
                  <div className="empty-chat-card">
                    <div className="empty-chat-title">
                      Start a conversation with AGEX
                    </div>
                    <div className="empty-chat-copy">
                      Example: I work in a company, pay rent, invested in PPF
                      and ELSS, and want to reduce tax.
                    </div>
                  </div>
                </div>
              ) : (
                history.map(renderMessageBubble)
              )}
            </div>

            <div className="composer-wrap">
              {error && <div className="error-banner">{error}</div>}

              {response?.status === "need_followup" ? (
                <div className="composer-group">
                  <div className="followup-banner">
                    {response.followup_question}
                  </div>
                  <div className="composer-row">
                    <textarea
                      value={followupAnswer}
                      onChange={(e) => setFollowupAnswer(e.target.value)}
                      rows={2}
                      placeholder="Type your reply..."
                      className="composer-input"
                    />
                    <button
                      onClick={callFollowup}
                      disabled={loading || !followupAnswer.trim()}
                      className="composer-send"
                    >
                      {loading ? "Sending..." : "Send"}
                    </button>
                  </div>
                </div>
              ) : (
                <div className="composer-row">
                  <textarea
                    value={userQuery}
                    onChange={(e) => setUserQuery(e.target.value)}
                    rows={2}
                    placeholder="Message AGEX..."
                    className="composer-input"
                  />
                  <button
                    onClick={callAnalyze}
                    disabled={loading || !userQuery.trim()}
                    className="composer-send"
                  >
                    {loading ? "Thinking..." : "Send"}
                  </button>
                </div>
              )}
            </div>
          </section>

          <section className="right-panel">{renderRightPanel()}</section>
        </main>
      </div>
    </div>
  );
}