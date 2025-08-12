class EnhancedChatbot {
    constructor() {
        this.isOpen = false;
        this.messages = [];
        this.isTyping = false;
        this.quickReplies = [];
        this.initializeElements();
        this.bindEvents();
        this.addWelcomeMessage();
    }

    initializeElements() {
        this.trigger = document.getElementById('chatbot-trigger');
        this.chatbot = document.getElementById('chatbot');
        this.closeBtn = document.getElementById('chatbot-close');
        this.input = document.getElementById('chatbot-input');
        this.sendBtn = document.getElementById('chatbot-send');
        this.messagesContainer = document.getElementById('chatbot-messages');
    }

    bindEvents() {
        if (this.trigger) {
            this.trigger.addEventListener('click', () => this.toggleChat());
        }
        
        if (this.closeBtn) {
            this.closeBtn.addEventListener('click', () => this.toggleChat());
        }
        
        if (this.sendBtn) {
            this.sendBtn.addEventListener('click', () => this.sendMessage());
        }
        
        if (this.input) {
            this.input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });

            this.input.addEventListener('input', () => {
                this.handleTypingIndicator();
            });
        }
    }

    toggleChat() {
        this.isOpen = !this.isOpen;
        
        if (this.chatbot) {
            if (this.isOpen) {
                this.chatbot.classList.add('active');
                this.trigger.style.display = 'none';
                this.focusInput();
            } else {
                this.chatbot.classList.remove('active');
                this.trigger.style.display
