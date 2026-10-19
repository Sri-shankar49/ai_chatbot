import "./ConversationSidebar.css";

export default function ConversationSidebar({
  conversations,
  activeConversationId,
  onNewChat,
  onSelectConversation,
  loading,
}) {
  return (
    <aside className="conversation-sidebar">
      <h2>AI Chatbot</h2>

      <button
        className="new-chat-button"
        onClick={onNewChat}
      >
        + New Chat
      </button>

      <h3>Your conversations</h3>

      {loading && <p>Loading conversations...</p>}

      {!loading && conversations.length === 0 && (
        <p className="empty-history">
          No saved conversations yet.
        </p>
      )}

      <div className="conversation-list">
        {conversations.map((conversation) => (
          <button
            key={conversation.id}
            className={`conversation-item ${
              activeConversationId === conversation.id
                ? "active"
                : ""
            }`}
            onClick={() =>
              onSelectConversation(conversation.id)
            }
            title={conversation.title}
          >
            <span className="conversation-title">
              {conversation.title || "New conversation"}
            </span>

            <span className="conversation-count">
              {conversation.message_count ?? 0} messages
            </span>
          </button>
        ))}
      </div>
    </aside>
  );
}