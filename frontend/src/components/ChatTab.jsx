import React, { useState, useRef, useEffect } from 'react';
import { askQA } from '../api';

const SendIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>
  </svg>
);

const SparkleIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2z"/>
  </svg>
);

const DbIcon = () => (
  <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/>
    <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>
  </svg>
);

const INITIAL_MSG = {
  role: 'assistant',
  content: "Hello! I'm your AI Research Assistant, trained on the university document archive. Ask me anything about notices, exam schedules, scholarships, or policies — I'll cite my sources.",
  sources: [],
};

const ChatTab = () => {
  const [messages, setMessages] = useState([INITIAL_MSG]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (e) => {
    e?.preventDefault();
    const text = input.trim();
    if (!text || loading) return;

    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: text, sources: [] }]);
    setLoading(true);

    try {
      const data = await askQA(text);
      setMessages(prev => [...prev, { role: 'assistant', content: data.answer, sources: data.sources || [] }]);
    } catch {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Connection error: The AI backend could not be reached. Please ensure the server is running.',
        sources: [],
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-shell">
      <div className="chat-header page-header" style={{ marginBottom: 0 }}>
        <h2>AI Research Assistant</h2>
        <p>Context-aware Q&A with cited sources — powered by Mistral via Ollama.</p>
      </div>

      <div className="chat-messages-wrap">
        {messages.map((msg, i) => (
          <div key={i} className={`chat-message ${msg.role}`} style={{ animationDelay: `${i * 0.03}s` }}>
            <div className={`chat-avatar ${msg.role}`}>
              {msg.role === 'assistant' ? <SparkleIcon /> : 'U'}
            </div>
            <div className="chat-bubble">
              <span style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</span>
              {msg.sources?.length > 0 && (
                <div className="chat-sources">
                  <div className="chat-sources-label">
                    <DbIcon /> Referenced Sources
                  </div>
                  {msg.sources.map((src, si) => (
                    <div key={si} className="chat-source-item">{si + 1}. {src}</div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="chat-message assistant">
            <div className="chat-avatar ai"><SparkleIcon /></div>
            <div className="chat-bubble">
              <div className="chat-typing-bubble">
                <div className="typing-dot" />
                <div className="typing-dot" />
                <div className="typing-dot" />
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="chat-input-area">
        <form onSubmit={handleSend}>
          <div className="chat-input-row">
            <input
              id="chat-input"
              type="text"
              className="chat-input"
              placeholder="Ask about exam schedules, fee deadlines, holiday notices..."
              value={input}
              onChange={e => setInput(e.target.value)}
              disabled={loading}
            />
            <button type="submit" className="send-btn" disabled={loading || !input.trim()} aria-label="Send message">
              <SendIcon />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ChatTab;
