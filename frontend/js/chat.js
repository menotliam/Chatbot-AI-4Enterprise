// CHATBOTAI Frontend JavaScript
class ChatbotUI {
    constructor() {
        this.apiUrl = 'http://localhost:8000';
        this.userId = 'user123';
        this.sessionId = null;
        this.isTyping = false;

        this.initializeElements();
        this.attachEventListeners();
        this.checkConnection();
        this.loadSettings();
    }

    initializeElements() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.clearButton = document.getElementById('clearButton');
        this.settingsButton = document.getElementById('settingsButton');
        this.statusDot = document.getElementById('statusDot');
        this.statusText = document.getElementById('statusText');
        this.typingIndicator = document.getElementById('typingIndicator');

        // Modal elements
        this.settingsModal = document.getElementById('settingsModal');
        this.closeSettings = document.getElementById('closeSettings');
        this.saveSettings = document.getElementById('saveSettings');
        this.cancelSettings = document.getElementById('cancelSettings');
        this.userIdInput = document.getElementById('userId');
        this.apiUrlInput = document.getElementById('apiUrl');
        this.themeSelect = document.getElementById('theme');
        this.enhanceResponseCheckbox = document.getElementById('enhanceResponse');
    }

    attachEventListeners() {
        // Send message events
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Input validation
        this.messageInput.addEventListener('input', () => {
            this.updateSendButton();
        });

        // Clear chat
        this.clearButton.addEventListener('click', () => this.clearChat());

        // Settings modal
        this.settingsButton.addEventListener('click', () => this.openSettings());
        this.closeSettings.addEventListener('click', () => this.closeSettingsModal());
        this.cancelSettings.addEventListener('click', () => this.closeSettingsModal());
        this.saveSettings.addEventListener('click', () => this.saveSettings());

        // Click outside modal to close
        this.settingsModal.addEventListener('click', (e) => {
            if (e.target === this.settingsModal) {
                this.closeSettingsModal();
            }
        });
    }

    async checkConnection() {
        try {
            const response = await fetch(`${this.apiUrl}/docs`);
            if (response.ok) {
                this.setStatus(true, 'Đã kết nối');
            } else {
                this.setStatus(false, 'Lỗi kết nối');
            }
        } catch (error) {
            this.setStatus(false, 'Không thể kết nối');
            console.error('Connection check failed:', error);
        }
    }

    setStatus(connected, message) {
        this.statusDot.classList.toggle('connected', connected);
        this.statusText.textContent = message;
    }

    updateSendButton() {
        const message = this.messageInput.value.trim();
        this.sendButton.disabled = !message || this.isTyping;
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isTyping) return;

        // Add user message to chat
        this.addMessage(message, 'user');
        this.messageInput.value = '';
        this.updateSendButton();

        // Show typing indicator
        this.showTyping();

        try {
            const response = await this.callChatAPI(message);

            if (response) {
                this.addMessage(response.reply, 'bot');
                if (response.session_id) {
                    this.sessionId = response.session_id;
                }
            } else {
                this.addMessage('Xin lỗi, có lỗi xảy ra. Vui lòng thử lại.', 'bot', true);
            }
        } catch (error) {
            console.error('Chat API error:', error);
            this.addMessage('Không thể kết nối đến server. Vui lòng kiểm tra kết nối.', 'bot', true);
        } finally {
            this.hideTyping();
        }
    }

    async callChatAPI(message) {
        const payload = {
            user_id: this.userId,
            message: message,
            session_id: this.sessionId,
            enhance_response: this.enhanceResponseCheckbox.checked
        };

        try {
            const response = await fetch(`${this.apiUrl}/api/chatbot/interact`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API call failed:', error);
            return null;
        }
    }

    addMessage(text, sender, isError = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;

        const avatarDiv = document.createElement('div');
        avatarDiv.className = `${sender}-avatar`;

        const avatarIcon = document.createElement('i');
        avatarIcon.className = sender === 'user' ? 'fas fa-user' : 'fas fa-robot';
        avatarDiv.appendChild(avatarIcon);

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        if (isError) {
            contentDiv.classList.add('error');
        }

    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    // Render rich text (bold, links, line breaks) safely without innerHTML
    this.renderRichText(textDiv, text);

        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = new Date().toLocaleTimeString('vi-VN', {
            hour: '2-digit',
            minute: '2-digit'
        });

        contentDiv.appendChild(textDiv);
        contentDiv.appendChild(timeDiv);

        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);

        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    showTyping() {
        this.isTyping = true;
        this.typingIndicator.style.display = 'flex';
        this.updateSendButton();
        this.scrollToBottom();
    }

    hideTyping() {
        this.isTyping = false;
        this.typingIndicator.style.display = 'none';
        this.updateSendButton();
    }

    clearChat() {
        if (confirm('Bạn có chắc muốn xóa tất cả tin nhắn?')) {
            // Keep only the welcome message
            const welcomeMessage = this.chatMessages.querySelector('.welcome-message');
            this.chatMessages.innerHTML = '';
            if (welcomeMessage) {
                this.chatMessages.appendChild(welcomeMessage);
            }
            this.sessionId = null;
        }
    }

    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }

    openSettings() {
        this.userIdInput.value = this.userId;
        this.apiUrlInput.value = this.apiUrl;
        this.settingsModal.style.display = 'flex';
    }

    closeSettingsModal() {
        this.settingsModal.style.display = 'none';
    }

    saveSettings() {
        this.userId = this.userIdInput.value.trim() || 'user123';
        this.apiUrl = this.apiUrlInput.value.trim() || 'http://localhost:8000';

        // Save to localStorage
        localStorage.setItem('chatbot_userId', this.userId);
        localStorage.setItem('chatbot_apiUrl', this.apiUrl);
        localStorage.setItem('chatbot_enhanceResponse', this.enhanceResponseCheckbox.checked);

        this.closeSettingsModal();
        this.checkConnection();
    }

    loadSettings() {
        const savedUserId = localStorage.getItem('chatbot_userId');
        const savedApiUrl = localStorage.getItem('chatbot_apiUrl');
        const savedEnhanceResponse = localStorage.getItem('chatbot_enhanceResponse');

        if (savedUserId) this.userId = savedUserId;
        if (savedApiUrl) this.apiUrl = savedApiUrl;
        if (savedEnhanceResponse !== null) {
            this.enhanceResponseCheckbox.checked = savedEnhanceResponse === 'true';
        }
    }
    // Remove emojis and common emoticons from text before rendering
    stripEmojis(text) {
        if (!text) return text;
        try {
            // remove variation selectors and ZWJ
            text = text.replace(/[\uFE0E\uFE0F\u200D]/g, '');
            // remove common emoji ranges (use u flag)
            text = text.replace(/[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F1E0}-\u{1F1FF}\u{2700}-\u{27BF}\u{1F900}-\u{1F9FF}\u{2600}-\u{26FF}\u{2B00}-\u{2BFF}]/gu, '');
            // remove common ASCII emoticons
            text = text.replace(/(:-\)|:\)|:-\(|:\(|:D|:P|:p|;\)|;-\)|:\]|:\[|:\/|:\\\\|:o|:O|<3|\^_\^|\(-_-?\)|\^_-\^)/gi, '');
            // collapse repeated whitespace
            text = text.replace(/\s{2,}/g, ' ').trim();
            return text;
        } catch (e) {
            return text;
        }
    }
    // Render a small, safe subset of markdown-like formatting into DOM nodes
    renderRichText(container, text) {
        // Clear existing
        container.innerHTML = '';
        if (!text) return;

        const platformMap = {
            'shopee.vn': 'Shopee',
            's.shopee.vn': 'Shopee',
            'tiktok.com': 'TikTok',
            'facebook.com': 'Facebook',
            'lazada.vn': 'Lazada',
            'tiki.vn': 'Tiki',
            'sendo.vn': 'Sendo',
            'drive.google.com': 'Drive',
            'docs.google.com': 'Google Docs',
            'drive.googleusercontent.com': 'Drive',
            'bit.ly': 'Link',
            'tinyurl.com': 'Link'
        };

        // Extract images first (markdown images and raw image URLs), remove them from text
        const imageMdRe = /!\[([^\]]*)\]\((https?:\/\/[^\s)]+)\)/gi;
        const rawImageRe = /https?:\/\/[^\s)]+\.(?:png|jpe?g|gif|webp)(?:\?[^\s]*)?/gi;
        const images = [];
        let mImg;
        while ((mImg = imageMdRe.exec(text)) !== null) {
            images.push({url: mImg[2], alt: mImg[1] || 'image'});
        }
        // find raw image urls
        const rawMatches = text.matchAll(rawImageRe);
        for (const rm of rawMatches) {
            // avoid duplicates
            if (!images.find(i => i.url === rm[0])) images.push({url: rm[0], alt: 'image'});
        }
        // limit to 3 images
        const imagesToShow = images.slice(0, 3);
        // Remove image markdown and raw image urls from text to avoid duplicate anchors/display
        let textNoImgs = text.replace(imageMdRe, '').replace(rawImageRe, '');

        const lines = textNoImgs.split(/\r?\n/);
        // Strip emojis from the whole text before processing lines
        textNoImgs = this.stripEmojis(textNoImgs);
        lines.forEach((line, idx) => {
            const lineDiv = document.createElement('div');

            // Combined regex: markdown link | raw url | bold **text**
            const combined = /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)|https?:\/\/[^\s)]+|\*\*([^*]+)\*\*/g;
            let lastIndex = 0;
            let m;
            while ((m = combined.exec(line)) !== null) {
                if (m.index > lastIndex) {
                    lineDiv.appendChild(document.createTextNode(line.slice(lastIndex, m.index)));
                }

                if (m[1] && m[2]) {
                    // markdown link [text](url)
                    const a = document.createElement('a');
                    a.href = m[2];
                    a.target = '_blank';
                    a.rel = 'noopener noreferrer';
                    a.textContent = m[1];
                    lineDiv.appendChild(a);
                } else if (m[0].startsWith('http')) {
                    // raw url -> map to platform name if possible
                    const url = m[0];
                    let name = null;
                    try {
                        const host = new URL(url).hostname.toLowerCase();
                        for (const key in platformMap) {
                            if (host.includes(key)) { name = platformMap[key]; break; }
                        }
                    } catch (e) { /* ignore URL parse errors */ }
                    const a = document.createElement('a');
                    a.href = url;
                    a.target = '_blank';
                    a.rel = 'noopener noreferrer';
                    a.textContent = name || url;
                    lineDiv.appendChild(a);
                } else if (m[3]) {
                    // bold
                    const strong = document.createElement('strong');
                    strong.textContent = m[3];
                    lineDiv.appendChild(strong);
                }

                lastIndex = combined.lastIndex;
            }

            if (lastIndex < line.length) {
                lineDiv.appendChild(document.createTextNode(line.slice(lastIndex)));
            }

            container.appendChild(lineDiv);
            if (idx < lines.length - 1) container.appendChild(document.createElement('br'));
        });

        // If there are images extracted, render them below the text
        if (imagesToShow.length > 0) {
            const gallery = document.createElement('div');
            gallery.className = 'message-images';
            imagesToShow.forEach(imgObj => {
                const img = document.createElement('img');
                img.src = imgObj.url;
                img.alt = imgObj.alt || '';
                img.loading = 'lazy';
                img.className = 'bot-image';
                // small error handler to hide broken images
                img.addEventListener('error', () => img.style.display = 'none');
                gallery.appendChild(img);
            });
            container.appendChild(gallery);
        }
    }
}

// Initialize the chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const chatbot = new ChatbotUI();

    // Add some helpful keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + / to focus input
        if ((e.ctrlKey || e.metaKey) && e.key === '/') {
            e.preventDefault();
            document.getElementById('messageInput').focus();
        }

        // Escape to close modal
        if (e.key === 'Escape' && document.getElementById('settingsModal').style.display === 'flex') {
            document.getElementById('settingsModal').style.display = 'none';
        }
    });

    // Auto-resize textarea (if we change to textarea later)
    // For now, we'll keep the input but add max length handling
    document.getElementById('messageInput').addEventListener('input', function() {
        if (this.value.length > 1000) {
            this.value = this.value.substring(0, 1000);
        }
    });
});
