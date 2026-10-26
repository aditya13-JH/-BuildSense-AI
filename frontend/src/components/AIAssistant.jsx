import React, { useState, useEffect, useRef } from 'react';

function AIAssistant() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const exampleQuestions = [
    'What are the steps in building a house?',
    'How to check concrete quality?',
    'What safety equipment is needed on site?',
  ];

  // Auto-scroll to the bottom when messages or loading state changes
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSendMessage = async (textToSend) => {
    const query = typeof textToSend === 'string' ? textToSend.trim() : input.trim();
    if (!query || loading) return;

    setError(null);
    setInput('');

    const newMessages = [...messages, { role: 'user', content: query }];
    setMessages(newMessages);
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/assistant/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: query }),
      });

      if (!response.ok) {
        let errorDetail = `Request failed with status ${response.status}`;
        try {
          const errData = await response.json();
          errorDetail = errData.detail || errData.message || JSON.stringify(errData);
        } catch {
          const errText = await response.text();
          if (errText) errorDetail = errText;
        }
        throw new Error(errorDetail);
      }

      const data = await response.json();
      const botReply =
        data.reply ||
        data.response ||
        data.message ||
        data.answer ||
        (typeof data === 'string' ? data : JSON.stringify(data, null, 2));

      setMessages((prev) => [...prev, { role: 'assistant', content: botReply }]);
    } catch (err) {
      setError(err.message || 'An error occurred while contacting BuildSense AI.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleSuggestionClick = (question) => {
    handleSendMessage(question);
  };

  return (
    <div className="ai-assistant">
      <h1 className="page-title">🤖 AI Assistant</h1>
      <p className="page-description">Ask any construction-related question</p>

      {error && (
        <div className="error-box" style={{ marginBottom: '16px' }}>
          <span className="error-icon">⚠️</span>
          <span>{error}</span>
        </div>
      )}

      <div className="chat-container">
        <div className="chat-messages">
          {messages.length === 0 ? (
            <div className="chat-empty">
              <div className="empty-icon">🏗️</div>
              <h3>How can I assist your construction project today?</h3>
              <p>Ask about structural engineering, safety standards, materials, or building codes.</p>
              <div className="suggestion-chips">
                {exampleQuestions.map((q, idx) => (
                  <button
                    key={idx}
                    type="button"
                    className="suggestion-chip"
                    onClick={() => handleSuggestionClick(q)}
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((msg, index) => (
              <div key={index} className={`chat-message ${msg.role}`}>
                <div className="message-role">
                  {msg.role === 'user' ? 'You' : 'BuildSense AI'}
                </div>
                <div className="message-content">{msg.content}</div>
              </div>
            ))
          )}

          {loading && (
            <div className="chat-message assistant">
              <div className="message-role">BuildSense AI</div>
              <div className="message-content">
                <div className="loading" style={{ padding: 0 }}>
                  <div className="spinner"></div>
                  <span>BuildSense AI is thinking...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input-area">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              messages.length === 0
                ? 'e.g. What are the steps in building a house?'
                : 'Type your construction question here...'
            }
            disabled={loading}
          />
          <button
            type="button"
            className="btn btn-primary"
            onClick={() => handleSendMessage()}
            disabled={loading || !input.trim()}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default AIAssistant;
