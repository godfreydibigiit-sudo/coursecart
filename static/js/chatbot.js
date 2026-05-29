/**
 * CourseCart AI Chatbot - Professional JavaScript
 * With CourseCart Brand Logo Integration
 * Handles chat UI, API calls, message rendering, and animations
 */

(function() {
    'use strict';

    const Chatbot = {
        // Configuration
        config: {
            apiUrl: '/chatbot/api/chat/',
            suggestionsUrl: '/chatbot/api/suggestions/',
            maxHistory: 50,
            welcomeMessage: 'Hello! 👋 I\'m your CourseCart AI Assistant. I can help you find courses, understand payments, or guide you through the platform. How can I help you today?',
            botName: 'CourseCart AI',
            placeholder: 'Ask me anything about CourseCart...',
            // Path to your logo
            logoUrl: '/static/images/logo.png'
        },

        // State
        state: {
            isOpen: false,
            isLoading: false,
            messageHistory: [],
            csrfToken: null
        },

        // Initialize
        init: function() {
            this.state.csrfToken = this.getCSRFToken();
            this.loadHistory();
            this.render();
            this.bindEvents();
            this.loadSuggestions();
        },

        // Get CSRF token
        getCSRFToken: function() {
            const cookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
            return cookie ? cookie.split('=')[1] : '';
        },

        // Load chat history from localStorage
        loadHistory: function() {
            try {
                const saved = localStorage.getItem('coursecart_chat_history');
                if (saved) {
                    this.state.messageHistory = JSON.parse(saved);
                }
            } catch (e) {
                this.state.messageHistory = [];
            }
        },

        // Save chat history
        saveHistory: function() {
            try {
                const toSave = this.state.messageHistory.slice(-this.config.maxHistory);
                localStorage.setItem('coursecart_chat_history', JSON.stringify(toSave));
            } catch (e) {
                // localStorage full or unavailable
            }
        },

        // Get logo HTML
        getLogoHTML: function(size) {
            const w = size || 40;
            const h = size || 40;
            return `<img src="${this.config.logoUrl}" alt="CourseCart AI" style="width:${w}px;height:${h}px;object-fit:contain;" onerror="this.style.display='none';this.parentElement.innerHTML='📚';">`;
        },

        // Load suggested questions
        loadSuggestions: function() {
            fetch(this.config.suggestionsUrl)
                .then(r => r.json())
                .then(data => {
                    if (data.questions) {
                        this.renderSuggestions(data.questions);
                    }
                })
                .catch(() => {
                    // Use default suggestions
                    const defaults = [
                        { text: "📚 What courses are available?", icon: "📚" },
                        { text: "💰 How do I pay?", icon: "💰" },
                        { text: "👥 Who built CourseCart?", icon: "👥" },
                        { text: "🎓 How to get certificate?", icon: "🎓" },
                    ];
                    this.renderSuggestions(defaults);
                });
        },

        // Render the entire chatbot widget
        render: function() {
            const logoImg = this.getLogoHTML(36);
            const logoImgSmall = this.getLogoHTML(22);
            const logoImgWelcome = this.getLogoHTML(56);

            const html = `
                <!-- FAB Button with Logo -->
                <button class="chat-fab" id="chatFab" aria-label="Open CourseCart AI Assistant">
                    <span class="fab-logo-wrap">${logoImg}</span>
                    <span class="fab-badge"></span>
                    <span class="fab-tooltip">Need help? Ask AI!</span>
                </button>

                <!-- Chat Window -->
                <div class="chat-window" id="chatWindow">
                    <!-- Header with Brand Logo -->
                    <div class="chat-header">
                        <div class="ai-avatar">
                            ${logoImg}
                        </div>
                        <div class="header-info">
                            <div class="header-title">${this.config.botName}</div>
                            <div class="header-subtitle">
                                <span class="status-dot"></span> Online — Here to help
                            </div>
                        </div>
                        <button class="btn-close" id="btnClose" aria-label="Close chat">✕</button>
                    </div>

                    <!-- Messages -->
                    <div class="chat-messages" id="chatMessages">
                        <div class="chat-welcome">
                            <span class="welcome-icon">${logoImgWelcome}</span>
                            <div class="welcome-text">${this.config.botName}</div>
                            <div class="welcome-sub">AI-Powered Learning Assistant</div>
                        </div>
                    </div>

                    <!-- Suggestions -->
                    <div class="chat-suggestions" id="chatSuggestions"></div>

                    <!-- Input -->
                    <div class="chat-input-area">
                        <textarea 
                            id="chatInput" 
                            placeholder="${this.config.placeholder}" 
                            rows="1"
                            maxlength="500"
                        ></textarea>
                        <button class="btn-send" id="btnSend" aria-label="Send message">➤</button>
                    </div>
                </div>
            `;

            const container = document.createElement('div');
            container.id = 'chatbot-container';
            container.innerHTML = html;
            document.body.appendChild(container);

            // Store small logo for message avatars
            this._logoSmall = logoImgSmall;

            // Render message history
            this.renderMessages();
        },

        // Render chat messages
        renderMessages: function() {
            const messagesEl = document.getElementById('chatMessages');
            if (!messagesEl) return;

            const logoWelcome = this.getLogoHTML(56);

            // Keep welcome message and add history
            messagesEl.innerHTML = `
                <div class="chat-welcome">
                    <span class="welcome-icon">${logoWelcome}</span>
                    <div class="welcome-text">${this.config.botName}</div>
                    <div class="welcome-sub">AI-Powered Learning Assistant</div>
                </div>
            `;

            // Add initial bot message
            this.addMessageElement('bot', this.config.welcomeMessage);

            // Add history
            this.state.messageHistory.forEach(msg => {
                this.addMessageElement(msg.type, msg.text, msg.time);
            });

            this.scrollToBottom();
        },

        // Add a single message element
        addMessageElement: function(type, text, time) {
            const messagesEl = document.getElementById('chatMessages');
            if (!messagesEl) return;

            const timeStr = time || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            
            // Use logo for bot, user icon for user
            const avatar = type === 'bot' 
                ? `<div class="msg-avatar bot-avatar">${this._logoSmall || this.getLogoHTML(22)}</div>`
                : '<div class="msg-avatar user-avatar">👤</div>';

            const msgDiv = document.createElement('div');
            msgDiv.className = `chat-message ${type}`;
            msgDiv.innerHTML = `
                ${avatar}
                <div>
                    <div class="msg-bubble">${this.escapeHtml(text)}</div>
                    <div class="msg-time">${timeStr}</div>
                </div>
            `;

            messagesEl.appendChild(msgDiv);
            this.scrollToBottom();
        },

        // Add typing indicator
        showTyping: function() {
            const messagesEl = document.getElementById('chatMessages');
            if (!messagesEl) return;

            const typingDiv = document.createElement('div');
            typingDiv.className = 'chat-message bot';
            typingDiv.id = 'typingIndicator';
            typingDiv.innerHTML = `
                <div class="msg-avatar bot-avatar">${this._logoSmall || this.getLogoHTML(22)}</div>
                <div class="typing-indicator">
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                </div>
            `;

            messagesEl.appendChild(typingDiv);
            this.scrollToBottom();
        },

        // Remove typing indicator
        hideTyping: function() {
            const typing = document.getElementById('typingIndicator');
            if (typing) typing.remove();
        },

        // Send message to API
        sendMessage: async function(message) {
            if (this.state.isLoading || !message.trim()) return;

            this.state.isLoading = true;
            this.updateSendButton(true);

            // Add user message to UI and history
            const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            this.addMessageElement('user', message, time);
            this.state.messageHistory.push({ type: 'user', text: message, time: time });

            // Clear input
            const input = document.getElementById('chatInput');
            if (input) input.value = '';

            // Show typing with thinking steps if available
            this.showTyping();

            try {
                const response = await fetch(this.config.apiUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.state.csrfToken,
                    },
                    body: JSON.stringify({ message: message })
                });

                const data = await response.json();
                this.hideTyping();

                const botTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                
                // Show thinking steps if available
                if (data.thinking_steps && data.thinking_steps.length > 0) {
                    // Briefly show each thinking step (simulated)
                    for (let i = 0; i < Math.min(data.thinking_steps.length, 2); i++) {
                        const step = data.thinking_steps[i];
                        // Steps are shown via typing indicator already
                    }
                }
                
                this.addMessageElement('bot', data.response, botTime);
                this.state.messageHistory.push({ type: 'bot', text: data.response, time: botTime });
                this.saveHistory();

            } catch (error) {
                this.hideTyping();
                const errorMsg = 'Sorry, I\'m having trouble connecting. Please try again later. 🙏';
                const botTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                this.addMessageElement('bot', errorMsg, botTime);
            }

            this.state.isLoading = false;
            this.updateSendButton(false);
        },

        // Render suggested questions
        renderSuggestions: function(questions) {
            const container = document.getElementById('chatSuggestions');
            if (!container) return;

            container.innerHTML = questions.map(q => 
                `<button class="chat-suggestion" data-question="${this.escapeHtml(q.text)}">${q.icon} ${q.text}</button>`
            ).join('');

            // Bind click events
            container.querySelectorAll('.chat-suggestion').forEach(btn => {
                btn.addEventListener('click', () => {
                    const question = btn.getAttribute('data-question');
                    this.sendMessage(question);
                });
            });
        },

        // Update send button state
        updateSendButton: function(disabled) {
            const btn = document.getElementById('btnSend');
            if (btn) {
                btn.disabled = disabled;
                btn.textContent = disabled ? '⏳' : '➤';
            }
        },

        // Toggle chat window
        toggleChat: function() {
            const window = document.getElementById('chatWindow');
            const fab = document.getElementById('chatFab');
            
            if (!window || !fab) return;

            this.state.isOpen = !this.state.isOpen;

            if (this.state.isOpen) {
                window.classList.add('open');
                fab.classList.add('open');
                fab.querySelector('.fab-tooltip').style.opacity = '0';
                setTimeout(() => this.scrollToBottom(), 350);
            } else {
                window.classList.remove('open');
                fab.classList.remove('open');
                fab.querySelector('.fab-tooltip').style.opacity = '';
            }
        },

        // Scroll to bottom of messages
        scrollToBottom: function() {
            const messages = document.getElementById('chatMessages');
            if (messages) {
                setTimeout(() => {
                    messages.scrollTop = messages.scrollHeight;
                }, 50);
            }
        },

        // Escape HTML
        escapeHtml: function(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        },

        // Bind all events
        bindEvents: function() {
            // FAB click
            document.addEventListener('click', (e) => {
                if (e.target.closest('#chatFab')) {
                    this.toggleChat();
                }
            });

            // Close button
            document.addEventListener('click', (e) => {
                if (e.target.closest('#btnClose')) {
                    this.toggleChat();
                }
            });

            // Send button
            document.addEventListener('click', (e) => {
                if (e.target.closest('#btnSend')) {
                    const input = document.getElementById('chatInput');
                    if (input && input.value.trim()) {
                        this.sendMessage(input.value.trim());
                    }
                }
            });

            // Enter key to send (Shift+Enter for new line)
            document.addEventListener('keydown', (e) => {
                if (e.target.id === 'chatInput' && e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    const input = document.getElementById('chatInput');
                    if (input && input.value.trim()) {
                        this.sendMessage(input.value.trim());
                    }
                }
            });

            // Auto-resize textarea
            document.addEventListener('input', (e) => {
                if (e.target.id === 'chatInput') {
                    e.target.style.height = 'auto';
                    e.target.style.height = Math.min(e.target.scrollHeight, 100) + 'px';
                }
            });

            // Close on Escape key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && this.state.isOpen) {
                    this.toggleChat();
                }
            });
        }
    };

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => Chatbot.init());
    } else {
        Chatbot.init();
    }

})();