/**
 * MoneyLeak Smart Finance Support Chatbot
 * Floating client-side chat panel with real-time financial intelligence.
 */
(function() {
  let isChatOpen = false;
  let chatHistory = [];
  let isAwaitingResponse = false;
  let lastFailedMessage = null;

  const PAGE_SUGGESTIONS = {
    '/dashboard': [
      "Explain my monthly budget & outflow",
      "Do I have any spending leaks?",
      "What is my current savings rate?",
      "How do I add a transaction?"
    ],
    '/budget': [
      "Explain my remaining budget",
      "What are Needs vs Wants vs Savings?",
      "How do I adjust category caps?",
      "Am I overspending in any category?"
    ],
    '/transactions': [
      "What is my largest expense category?",
      "How do I filter transactions by date?",
      "How do I edit or delete an entry?",
      "How do I add a custom category?"
    ],
    '/analysis': [
      "How are spending leaks detected?",
      "How do I track recurring subscriptions?",
      "What is subscription fatigue?",
      "Can I dismiss an alert?"
    ],
    '/simulator': [
      "How does the Savings Simulator work?",
      "What if I cut dining expenses by 15%?",
      "How are multi-year projections calculated?",
      "Will this change my actual transactions?"
    ],
    '/goals': [
      "How do I set up a new savings goal?",
      "How is my completion date calculated?",
      "What is my current savings progress?",
      "What goals does MoneyLeak support?"
    ],
    '/calculator': [
      "Explain SIP vs Lump Sum returns",
      "Are projected returns guaranteed?",
      "How does compound interest work here?",
      "What Indian schemes are supported?"
    ],
    '/reports': [
      "How do I export my data to PDF or CSV?",
      "What figures are included in monthly reports?",
      "How is financial health calculated?"
    ],
    '/settings': [
      "How do I switch between Student and Salaried?",
      "How do I change my currency or theme?",
      "How do I change my profile picture?",
      "How do I change my verified email?"
    ],
    '/assistant': [
      "Run a full financial health check",
      "Explain my 50/30/20 budget breakdown",
      "Do I have any spending leaks?",
      "Where can I find the investment calculator?"
    ]
  };

  const DEFAULT_SUGGESTIONS = [
    "How much did I spend this month?",
    "Explain my 50/30/20 budget",
    "Do I have any spending leaks?",
    "How do I add an expense?"
  ];

  function initChatbot() {
    const trigger = document.getElementById('floating-chat-trigger');
    const panel = document.getElementById('floating-chat-panel');
    const textarea = document.getElementById('chat-input-textarea');
    const sendBtn = document.getElementById('chat-send-btn');

    if (!trigger || !panel) return;

    // Render page context & suggestions
    updatePageContextAndSuggestions();

    // Textarea input listeners
    if (textarea) {
      textarea.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          sendFinanceChatMessage();
        }
      });

      textarea.addEventListener('input', () => {
        // Auto grow
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 90) + 'px';

        // Char count
        const charCount = document.getElementById('chat-char-count');
        if (charCount) charCount.textContent = `${textarea.value.length}/1000`;
      });
    }

    // Expose global window API
    window.openFinanceChat = openFinanceChat;
    window.toggleFinanceChat = toggleFinanceChat;
    window.minimizeFinanceChat = minimizeFinanceChat;
    window.restartFinanceChat = restartFinanceChat;
    window.sendFinanceChatMessage = sendFinanceChatMessage;
    window.retryFinanceChatMessage = retryFinanceChatMessage;
  }

  function updatePageContextAndSuggestions() {
    const path = window.location.pathname;
    const contextText = document.getElementById('chat-context-text');
    const row = document.getElementById('chat-suggested-row');

    // Page name
    let pageLabel = 'Dashboard';
    if (path.includes('budget')) pageLabel = 'Budget (50/30/20)';
    else if (path.includes('transactions')) pageLabel = 'Transactions Ledger';
    else if (path.includes('analysis')) pageLabel = 'Leak Detector';
    else if (path.includes('simulator')) pageLabel = 'Savings Simulator';
    else if (path.includes('goals')) pageLabel = 'Goals Planner';
    else if (path.includes('calculator')) pageLabel = 'Investment Calculator';
    else if (path.includes('reports')) pageLabel = 'Reports & PDF';
    else if (path.includes('settings')) pageLabel = 'Settings & Profile';
    else if (path.includes('assistant')) pageLabel = 'Financial Assistant';

    if (contextText) contextText.textContent = `Page Context: ${pageLabel}`;

    // Suggestions
    if (row) {
      const suggestions = PAGE_SUGGESTIONS[path] || DEFAULT_SUGGESTIONS;
      row.innerHTML = '';
      suggestions.forEach(q => {
        const chip = document.createElement('button');
        chip.type = 'button';
        chip.className = 'chat-suggest-chip';
        chip.textContent = q;
        chip.onclick = () => {
          const textarea = document.getElementById('chat-input-textarea');
          if (textarea) textarea.value = q;
          sendFinanceChatMessage();
        };
        row.appendChild(chip);
      });
    }
  }

  function toggleFinanceChat() {
    if (isChatOpen) {
      minimizeFinanceChat();
    } else {
      openFinanceChat();
    }
  }

  function openFinanceChat(initialMessage) {
    const panel = document.getElementById('floating-chat-panel');
    const botIcon = document.getElementById('chat-btn-icon-bot');
    const closeIcon = document.getElementById('chat-btn-icon-close');
    const textarea = document.getElementById('chat-input-textarea');

    if (!panel) return;

    panel.style.display = 'flex';
    isChatOpen = true;

    if (botIcon) botIcon.style.display = 'none';
    if (closeIcon) closeIcon.style.display = 'block';

    updatePageContextAndSuggestions();

    if (initialMessage && textarea) {
      textarea.value = initialMessage;
      sendFinanceChatMessage();
    } else if (textarea) {
      // Focus if on desktop
      if (window.innerWidth > 768) {
        setTimeout(() => textarea.focus(), 150);
      }
    }

    scrollToBottom();
    if (window.lucide) lucide.createIcons();
  }

  function minimizeFinanceChat() {
    const panel = document.getElementById('floating-chat-panel');
    const botIcon = document.getElementById('chat-btn-icon-bot');
    const closeIcon = document.getElementById('chat-btn-icon-close');

    if (!panel) return;

    panel.style.display = 'none';
    isChatOpen = false;

    if (botIcon) botIcon.style.display = 'block';
    if (closeIcon) closeIcon.style.display = 'none';
  }

  function restartFinanceChat() {
    if (!confirm('Start a fresh conversation? Your message history in this window will be cleared.')) return;
    const container = document.getElementById('chat-messages-container');
    if (!container) return;

    chatHistory = [];
    lastFailedMessage = null;

    container.innerHTML = `
      <div class="chat-msg-row assistant">
        <div class="chat-bubble assistant">
          <div class="chat-msg-text">
            Hello! I am your <strong>Finance Assistant</strong>. 
            How can I help you today? Ask about your current budget, recent spending, 
            leaks, or navigation across MoneyLeak.
          </div>
        </div>
      </div>
    `;

    const textarea = document.getElementById('chat-input-textarea');
    if (textarea) {
      textarea.value = '';
      textarea.style.height = 'auto';
      textarea.focus();
    }
    scrollToBottom();
  }

  function scrollToBottom() {
    const container = document.getElementById('chat-messages-container');
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  }

  function formatAssistantMessage(text, actions) {
    if (!text) return '';

    // Convert bold: **text** -> <strong>text</strong>
    let formatted = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Convert bullet points starting with • or -
    const lines = formatted.split('\n');
    let inList = false;
    let html = '';

    lines.forEach(line => {
      const trimmed = line.trim();
      if (trimmed.startsWith('• ') || trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
        if (!inList) {
          html += '<ul>';
          inList = true;
        }
        html += `<li>${trimmed.substring(2)}</li>`;
      } else {
        if (inList) {
          html += '</ul>';
          inList = false;
        }
        if (trimmed === '') {
          html += '<p style="margin:4px 0;"></p>';
        } else {
          html += `<p>${trimmed}</p>`;
        }
      }
    });

    if (inList) html += '</ul>';

    // Append action buttons if provided
    if (actions && actions.length > 0) {
      html += '<div class="chat-action-pills">';
      actions.forEach(a => {
        html += `<a href="${a.url}" class="chat-action-btn">
                  <span>${a.label}</span>
                  <i data-lucide="arrow-up-right" style="width:11px;height:11px;"></i>
                </a>`;
      });
      html += '</div>';
    }

    return html;
  }

  async function sendFinanceChatMessage() {
    if (isAwaitingResponse) return;

    const textarea = document.getElementById('chat-input-textarea');
    const sendBtn = document.getElementById('chat-send-btn');
    const container = document.getElementById('chat-messages-container');
    const typing = document.getElementById('chat-typing-indicator');

    if (!textarea || !container) return;

    const message = textarea.value.trim();
    if (!message) return;

    // Append User Message to UI
    const userRow = document.createElement('div');
    userRow.className = 'chat-msg-row user';
    userRow.innerHTML = `
      <div class="chat-bubble user">
        <div class="chat-msg-text">${escapeHtml(message)}</div>
      </div>
    `;
    container.appendChild(userRow);

    // Track in local history
    chatHistory.push({ role: 'user', text: message });

    // Clear input
    textarea.value = '';
    textarea.style.height = 'auto';
    const charCount = document.getElementById('chat-char-count');
    if (charCount) charCount.textContent = '0/1000';

    // Show typing indicator & disable send
    isAwaitingResponse = true;
    if (sendBtn) sendBtn.disabled = true;
    if (typing) typing.style.display = 'flex';
    scrollToBottom();

    try {
      const payload = {
        message: message,
        page_context: window.location.pathname,
        history: chatHistory.slice(-4)
      };

      const res = await secureFetch('/api/assistant/chat', {
        method: 'POST',
        body: JSON.stringify(payload)
      });

      if (!res.success) {
        throw new Error(res.error || 'Request failed');
      }

      // Hide typing
      if (typing) typing.style.display = 'none';

      // Append Assistant Message
      const assistantRow = document.createElement('div');
      assistantRow.className = 'chat-msg-row assistant';
      const formattedHtml = formatAssistantMessage(res.response, res.actions);
      assistantRow.innerHTML = `
        <div class="chat-bubble assistant">
          <div class="chat-msg-text">${formattedHtml}</div>
        </div>
      `;
      container.appendChild(assistantRow);

      chatHistory.push({ role: 'model', text: res.response });
      lastFailedMessage = null;
    } catch (err) {
      if (typing) typing.style.display = 'none';
      lastFailedMessage = message;

      const errorRow = document.createElement('div');
      errorRow.className = 'chat-msg-row assistant';
      errorRow.innerHTML = `
        <div class="chat-bubble assistant" style="border-color:rgba(239, 68, 68, 0.3);">
          <div class="chat-msg-text" style="color:var(--accent-danger);">
            <div style="font-weight:700;margin-bottom:4px;">Unable to fetch response</div>
            <div style="font-size:11.5px;color:var(--text-secondary);">${escapeHtml(err.message)}</div>
            <button type="button" class="btn btn-secondary btn-sm" onclick="retryFinanceChatMessage()" style="margin-top:8px;padding:3px 8px;font-size:11px;">
              <i data-lucide="rotate-ccw" style="width:11px;height:11px;margin-right:3px;"></i> Retry
            </button>
          </div>
        </div>
      `;
      container.appendChild(errorRow);
    } finally {
      isAwaitingResponse = false;
      if (sendBtn) sendBtn.disabled = false;
      scrollToBottom();
      if (window.lucide) lucide.createIcons();
    }
  }

  function retryFinanceChatMessage() {
    if (!lastFailedMessage) return;
    const textarea = document.getElementById('chat-input-textarea');
    if (textarea) textarea.value = lastFailedMessage;
    sendFinanceChatMessage();
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // Initialize on DOM load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initChatbot);
  } else {
    initChatbot();
  }
})();
