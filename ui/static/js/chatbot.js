/**
 * Smart College Assistant — Chatbot JavaScript
 * Handles AI chat interactions, typing animation, suggestions, export.
 */

"use strict";

const SESSION_ID = 'chat-' + Math.random().toString(36).substr(2, 9);
let isTyping = false;

// ── Initialize ────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  loadSuggestions();
  loadQuickTopics();
  initChatInput();
});

// ── Load Suggestions ──────────────────────────────────────────
async function loadSuggestions() {
  try {
    const res = await fetch('/api/chat/suggestions');
    const data = await res.json();
    if (!data.success) return;
    const chips = document.getElementById('suggestionChips');
    if (!chips) return;
    chips.innerHTML = data.suggestions
      .slice(0, 6)
      .map(s => `<button class="suggestion-chip" onclick="sendSuggestion('${s.replace(/'/g, "\\'")}')">💬 ${s}</button>`)
      .join('');
  } catch (e) { console.warn('Suggestions failed:', e); }
}

// ── Quick Topics ──────────────────────────────────────────────
function loadQuickTopics() {
  const container = document.getElementById('quickTopics');
  if (!container) return;
  const topics = [
    '🎓 Admission Process', '📋 CGPA Calculator', '💼 Placement Drives',
    '📅 Exam Schedule', '📚 Library Rules', '🏠 Hostel Facilities',
    '🏆 Scholarships', '👔 Dress Code',
  ];
  container.innerHTML = topics.map(t =>
    `<button class="quick-topic-btn" onclick="sendSuggestion('${t.slice(2).trim()}')">${t}</button>`
  ).join('');
}

// ── Chat Input Setup ──────────────────────────────────────────
function initChatInput() {
  const input = document.getElementById('chatInput');
  const charCount = document.getElementById('charCount');
  if (!input) return;

  input.addEventListener('input', () => {
    charCount.textContent = `${input.value.length} / 2000`;
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 120) + 'px';
  });

  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
}

// ── Send Message ──────────────────────────────────────────────
async function sendMessage() {
  const input = document.getElementById('chatInput');
  const message = input?.value?.trim();
  if (!message || isTyping) return;

  input.value = '';
  input.style.height = 'auto';
  document.getElementById('charCount').textContent = '0 / 2000';

  // Hide suggestions after first message
  const suggestionsEl = document.getElementById('chatSuggestions');
  if (suggestionsEl) suggestionsEl.style.display = 'none';

  appendMessage('user', message);
  setTyping(true);

  try {
    const res = await fetch('/api/chat/message', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ message, session_id: SESSION_ID }),
    });
    const data = await res.json();
    setTyping(false);

    if (data.success) {
      appendMessage('assistant', data.response, {
        agent: data.agent,
        confidence: data.confidence,
        sources: data.sources,
      });
      // Update current agent badge
      const badge = document.getElementById('currentAgent');
      if (badge && data.agent) {
        badge.textContent = data.agent.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
      }
    } else {
      appendMessage('assistant', '⚠️ I encountered an issue. Please try again.');
    }
  } catch (e) {
    setTyping(false);
    appendMessage('assistant', '❌ Network error. Please check your connection and try again.');
  }
}

function sendSuggestion(text) {
  const input = document.getElementById('chatInput');
  if (input) {
    input.value = text;
    sendMessage();
  }
}

// ── Append Message ────────────────────────────────────────────
function appendMessage(role, content, meta = {}) {
  const container = document.getElementById('chatMessages');
  if (!container) return;

  const wrapper = document.createElement('div');
  wrapper.className = `msg-wrapper msg-${role}`;

  const isUser = role === 'user';
  const avatarIcon = isUser ? 'bi-person-fill' : 'bi-robot';

  let sourcesHtml = '';
  if (meta.sources && meta.sources.length > 0) {
    sourcesHtml = `<div class="msg-sources">
      ${meta.sources.map(s => `<span class="source-tag">📄 ${s.file}</span>`).join('')}
    </div>`;
  }

  let metaHtml = '';
  if (!isUser && meta.agent) {
    const conf = meta.confidence ? ` · ${(meta.confidence * 100).toFixed(0)}% confidence` : '';
    metaHtml = `<div class="msg-meta">${meta.agent.replace(/_/g,' ')}${conf}</div>`;
  }

  const formattedContent = formatMessage(content);

  wrapper.innerHTML = `
    <div class="msg-avatar"><i class="bi ${avatarIcon}"></i></div>
    <div class="msg-content">
      <div class="msg-bubble">${formattedContent}</div>
      ${sourcesHtml}
      ${metaHtml}
    </div>
  `;

  container.appendChild(wrapper);
  container.scrollTop = container.scrollHeight;
}

// ── Format Message ────────────────────────────────────────────
function formatMessage(text) {
  // Convert markdown-like formatting
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code style="background:rgba(99,130,255,0.1);padding:2px 6px;border-radius:4px;font-size:0.85em;">$1</code>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br/>')
    .replace(/^(.*)$/m, (m) => `<p>${m}</p>`);
}

// ── Typing Indicator ──────────────────────────────────────────
function setTyping(active) {
  isTyping = active;
  const indicator = document.getElementById('typingIndicator');
  const sendBtn = document.getElementById('chatSendBtn');
  if (indicator) indicator.style.display = active ? 'flex' : 'none';
  if (sendBtn) sendBtn.disabled = active;
}

// ── Clear Chat ────────────────────────────────────────────────
async function clearChat() {
  const container = document.getElementById('chatMessages');
  if (!container) return;
  container.innerHTML = '';
  appendMessage('assistant', '👋 Chat cleared! How can I help you today?');
  try {
    await fetch('/api/chat/clear', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: SESSION_ID }),
    });
  } catch (e) { /* ignore */ }
  const sugg = document.getElementById('chatSuggestions');
  if (sugg) sugg.style.display = '';
}

// ── Export Chat ───────────────────────────────────────────────
function exportChat() {
  const messages = document.querySelectorAll('.msg-wrapper');
  let text = `Smart College Assistant — Chat Export\n${'='.repeat(40)}\n\n`;

  messages.forEach(msg => {
    const isUser = msg.classList.contains('msg-user');
    const bubble = msg.querySelector('.msg-bubble');
    if (bubble) {
      const role = isUser ? 'You' : 'Assistant';
      text += `[${role}]: ${bubble.innerText.trim()}\n\n`;
    }
  });

  const blob = new Blob([text], { type: 'text/plain' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `chat-export-${new Date().toISOString().slice(0, 10)}.txt`;
  a.click();
  URL.revokeObjectURL(a.href);
  showToast('Chat exported successfully!', 'success');
}
