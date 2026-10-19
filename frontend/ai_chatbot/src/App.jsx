// import { useState } from 'react'
// import heroImg from './assets/hero.png'
// import reactLogo from './assets/react.svg'
// import viteLogo from './assets/vite.svg'
// import './App.css'

// function App() {
//   const [count, setCount] = useState(0)

//   return (
//     <>
//       <section id="center">
//         <div className="hero">
//           <img src={heroImg} className="base" width="170" height="179" alt="" />
//           <img src={reactLogo} className="framework" alt="React logo" />
//           <img src={viteLogo} className="vite" alt="Vite logo" />
//         </div>
//         <div>
//           <h1>Get started</h1>
//           <p>
//             Edit <code>src/App.jsx</code> and save to test <code>HMR</code>
//           </p>
//         </div>
//         <button
//           type="button"
//           className="counter"
//           onClick={() => setCount((count) => count + 1)}
//         >
//           Count is {count}
//         </button>
//       </section>

//       <div className="ticks"></div>

//       <section id="next-steps">
//         <div id="docs">
//           <svg className="icon" role="presentation" aria-hidden="true">
//             <use href="/icons.svg#documentation-icon"></use>
//           </svg>
//           <h2>Documentation</h2>
//           <p>Your questions, answered</p>
//           <ul>
//             <li>
//               <a href="https://vite.dev/" target="_blank">
//                 <img className="logo" src={viteLogo} alt="" />
//                 Explore Vite
//               </a>
//             </li>
//             <li>
//               <a href="https://react.dev/" target="_blank">
//                 <img className="button-icon" src={reactLogo} alt="" />
//                 Learn more
//               </a>
//             </li>
//           </ul>
//         </div>
//         <div id="social">
//           <svg className="icon" role="presentation" aria-hidden="true">
//             <use href="/icons.svg#social-icon"></use>
//           </svg>
//           <h2>Connect with us</h2>
//           <p>Join the Vite community</p>
//           <ul>
//             <li>
//               <a href="https://github.com/vitejs/vite" target="_blank">
//                 <svg
//                   className="button-icon"
//                   role="presentation"
//                   aria-hidden="true"
//                 >
//                   <use href="/icons.svg#github-icon"></use>
//                 </svg>
//                 GitHub
//               </a>
//             </li>
//             <li>
//               <a href="https://chat.vite.dev/" target="_blank">
//                 <svg
//                   className="button-icon"
//                   role="presentation"
//                   aria-hidden="true"
//                 >
//                   <use href="/icons.svg#discord-icon"></use>
//                 </svg>
//                 Discord
//               </a>
//             </li>
//             <li>
//               <a href="https://x.com/vite_js" target="_blank">
//                 <svg
//                   className="button-icon"
//                   role="presentation"
//                   aria-hidden="true"
//                 >
//                   <use href="/icons.svg#x-icon"></use>
//                 </svg>
//                 X.com
//               </a>
//             </li>
//             <li>
//               <a href="https://bsky.app/profile/vite.dev" target="_blank">
//                 <svg
//                   className="button-icon"
//                   role="presentation"
//                   aria-hidden="true"
//                 >
//                   <use href="/icons.svg#bluesky-icon"></use>
//                 </svg>
//                 Bluesky
//               </a>
//             </li>
//           </ul>
//         </div>
//       </section>

//       <div className="ticks"></div>
//       <section id="spacer"></section>
//     </>
//   )
// }

// export default App







// import { useEffect, useState } from "react";
// import "./App.css";

// const API_URL = "http://127.0.0.1:8000";

// function App() {
//   const [message, setMessage] = useState("");
//   const [messages, setMessages] = useState([
//     {
//       role: "assistant",
//       text: "Hello! I'm your AI chatbot. How can I help you?"
//     }
//   ]);
//   const [conversationId, setConversationId] = useState(() => localStorage.getItem("ai_chat_conversation_id"));
//   const [loading, setLoading] = useState(false);
//   const [error, setError] = useState("");

//   async function handleSend(event) {
//     event.preventDefault();

//     const userMessage = message.trim();

//     if (!userMessage || loading) return;

//     setMessages((previous) => [
//       ...previous,
//       { role: "user", text: userMessage }
//     ]);

//     setMessage("");
//     setLoading(true);
//     setError("");

//     try {
//       const response = await fetch(`${API_URL}/chat`, {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json"
//         },
//         body: JSON.stringify({
//           message: userMessage,
//           ...(conversationId
//             ? { conversation_id: conversationId }
//             : {}),
//         })
//       });

//       if (!response.ok) {
//         throw new Error(`Request failed: ${response.status}`);
//       }

//       const data = await response.json();

//       if (data.conversation_id) {
//         localStorage.setItem(
//           "ai_chat_conversation_id",
//           data.conversation_id
//         );

//         setConversationId(data.conversation_id);
//       }

//       setMessages((previous) => [
//         ...previous,
//         { role: "assistant", text: data.reply }
//       ]);
//     } catch (err) {
//       setError(
//         "Could not connect to the backend. Check that FastAPI is running."
//       );
//       console.error(err);
//     } finally {
//       setLoading(false);
//     }
//   }

//   useEffect(() => {
//     if (!conversationId) return;

//     async function loadHistory() {
//       try {
//         const response = await fetch(
//           `${API_URL}/conversations/${conversationId}/messages`
//         );

//         if (!response.ok) {
//           localStorage.removeItem("ai_chat_conversation_id");
//           setConversationId(null);
//           return;
//         }

//         const history = await response.json();

//         setMessages(
//           history.map((item) => ({
//             role: item.role,
//             text: item.content,
//           }))
//         );
//       } catch (error) {
//         console.error("Could not restore chat history:", error);
//       }
//     }

//     loadHistory();
//   }, [conversationId]);

//   return (
//     <main className="app">
//       <section className="chat">
//         <header className="chat-header">
//           <div className="bot-icon">AI</div>
//           <div>
//             <h1>AI Chatbot</h1>
//             <p>React + FastAPI</p>
//           </div>
//           <span className="status">● Online</span>
//         </header>

//         <div className="messages">
//           {messages.map((item, index) => (
//             <div
//               key={index}
//               className={`message ${item.role}`}
//             >
//               <span className="role">
//                 {item.role === "user" ? "You" : "AI"}
//               </span>
//               <p>{item.text}</p>
//             </div>
//           ))}

//           {loading && (
//             <div className="message assistant">
//               <span className="role">AI</span>
//               <p>Waiting for backend response...</p>
//             </div>
//           )}
//         </div>

//         {error && <p className="error">{error}</p>}

//         <form className="chat-form" onSubmit={handleSend}>
//           <input
//             type="text"
//             value={message}
//             onChange={(event) => setMessage(event.target.value)}
//             placeholder="Type your message..."
//             aria-label="Chat message"
//             disabled={loading}
//           />

//           <button
//             type="submit"
//             disabled={loading || !message.trim()}
//           >
//             {loading ? "Sending..." : "Send"}
//           </button>
//         </form>

//         <footer>Learning project · AI responses will be added later</footer>
//       </section>
//     </main>
//   );
// }

// export default App;



import { useEffect, useState } from "react";
import "./App.css";
import ConversationSidebar from "./components/ConversationSidebar";
import ReactMarkdown from "react-markdown";
import DocumentUpload from "./components/DocumentUpload";

const API_URL = "https://ai-chatbot-xrik.onrender.com";
// const API_URL = "http://127.0.0.1:8000";
// const API_URL = "http://127.0.0.1:8001";

const WELCOME_MESSAGE = {
  role: "assistant",
  text: "Hello! I'm your AI chatbot. How can I help you?",
};

function App() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([WELCOME_MESSAGE]);

  const [conversationId, setConversationId] = useState(() => localStorage.getItem("ai_chat_conversation_id"));

  const [conversations, setConversations] = useState([]);
  const [loadingConversations, setLoadingConversations] = useState(true);

  const [sources, setSources] = useState([]);
  console.log("sources", sources);


  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchConversations = async function () {
    try {
      const response = await fetch(`${API_URL}/conversations`);

      if (!response.ok) {
        throw new Error("Failed to load conversations");
      }

      const data = await response.json();
      setConversations(data);
    } catch (err) {
      console.error("Could not load conversations:", err);
    } finally {
      setLoadingConversations(false);
    }
  }

  useEffect(() => {
    const timeoutId = window.setTimeout(fetchConversations, 0);
    return () => window.clearTimeout(timeoutId);
  }, []);

  useEffect(() => {
    if (!conversationId) {
      // setMessages([WELCOME_MESSAGE]);
      return;
    }

    let cancelled = false;

    async function loadHistory() {
      try {
        const response = await fetch(
          `${API_URL}/conversations/${conversationId}/messages`
        );

        if (!response.ok) {
          if (!cancelled) {
            localStorage.removeItem("ai_chat_conversation_id");
            setConversationId(null);
            setMessages([WELCOME_MESSAGE]);
          }
          return;
        }

        const history = await response.json();

        if (!cancelled) {
          setMessages(
            history.map((item) => ({
              role: item.role,
              text: item.content,
              sources: item.sources ?? [],
            }))
          );
        }
      } catch (err) {
        if (!cancelled) {
          console.error("Could not restore chat history:", err);
          setError("Could not load this conversation's history.");
        }
      }
    }

    loadHistory();

    return () => {
      cancelled = true;
    };
  }, [conversationId]);

  function handleNewChat() {
    if (loading) return;

    localStorage.removeItem("ai_chat_conversation_id");
    setConversationId(null);
    setMessages([WELCOME_MESSAGE]);
    setMessage("");
    setError("");
  }

  function handleSelectConversation(id) {
    if (loading) return;

    localStorage.setItem("ai_chat_conversation_id", id);
    setConversationId(id);
    setError("");
  }

  async function handleSend(event) {
    event.preventDefault();

    const userMessage = message.trim();

    if (!userMessage || loading) return;

    setMessages((previous) => [
      ...previous,
      { role: "user", text: userMessage },
    ]);

    setMessage("");
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: userMessage,
          ...(conversationId
            ? { conversation_id: conversationId }
            : {}),
        }),
      });

      if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
      }

      const data = await response.json();

      setSources(Array.isArray(data.sources) ? data.sources : []);

      if (data.conversation_id) {
        localStorage.setItem(
          "ai_chat_conversation_id",
          data.conversation_id
        );

        if (data.conversation_id !== conversationId) {
          // The history effect loads the newly created conversation.
          setConversationId(data.conversation_id);
        } else {
          // setMessages((previous) => [
          //   ...previous,
          //   { role: "assistant", text: data.reply },
          // ]);
          setMessages((previous) => [
            ...previous,
            {
              role: "assistant",
              text: data.reply,
              sources: Array.isArray(data.sources)
                ? data.sources
                : [],
            },
          ]);
        }
      } else {
        // setMessages((previous) => [
        //   ...previous,
        //   { role: "assistant", text: data.reply },
        // ]);
        setMessages((previous) => [
          ...previous,
          {
            role: "assistant",
            text: data.reply,
            sources: Array.isArray(data.sources)
              ? data.sources
              : [],
          },
        ]);
      }

      await fetchConversations();
    } catch (err) {
      setError(
        "Could not send your message. Check that FastAPI is running."
      );
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app-layout">
      <ConversationSidebar
        conversations={conversations}
        activeConversationId={conversationId}
        onNewChat={handleNewChat}
        onSelectConversation={handleSelectConversation}
        loading={loadingConversations}
      />

      <main className="app">
        <section className="chat">
          <header className="chat-header">
            <div className="bot-icon">AI</div>

            <div>
              <h1>AI Chatbot</h1>
              <p>React + FastAPI</p>
            </div>

            <span className="status">● Online</span>
          </header>

          <DocumentUpload
            onUploaded={() => {
              setError("");
            }}
          />

          <div className="messages">
            {messages.map((item, index) => (
              <div
                key={`${conversationId ?? "new"}-${index}`}
                className={`message ${item.role}`}
              >
                <span className="role">
                  {item.role === "user" ? "You" : "AI"}
                </span>

                {/* <p>{item.text}</p> */}

                {/* <div className="message-content">
                  {item.role === "assistant" ? (
                    <ReactMarkdown>{item.text}</ReactMarkdown>
                  ) : (
                    <p>{item.text}</p>
                  )}
                </div> */}

                <div className="message-content">
                  {item.role === "assistant" ? (
                    <>
                      <ReactMarkdown>{item.text}</ReactMarkdown>

                      {item.sources?.length > 0 && (
                        <div className="message-sources">
                          <strong>Sources</strong>

                          <ul>
                            {item.sources.map((source, index) => (
                              <li key={`${source.source ?? source.filename ?? "source"}-${index}`}>
                                {source.source ?? source.filename ?? "Uploaded document"}
                                {source.chunk_index != null &&
                                  ` · Chunk ${source.chunk_index}`}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </>
                  ) : (
                    <p>{item.text}</p>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="message assistant">
                <span className="role">AI</span>
                <p>Waiting for backend response...</p>
              </div>
            )}
          </div>

          {error && <p className="error">{error}</p>}

          <form className="chat-form" onSubmit={handleSend}>
            <input
              type="text"
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              placeholder="Type your message..."
              aria-label="Chat message"
              disabled={loading}
            />

            <button
              type="submit"
              disabled={loading || !message.trim()}
            >
              {loading ? "Sending..." : "Send"}
            </button>
          </form>

          <footer>Learning project · Powered by your AI backend</footer>
        </section>
      </main>
    </div>
  );
}

export default App;