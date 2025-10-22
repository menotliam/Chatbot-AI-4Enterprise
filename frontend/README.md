# CHATBOTAI Frontend

A modern, responsive web interface for the CHATBOTAI backend API.

## 🚀 Features

- **🎨 Modern UI**: Beautiful gradient design with smooth animations
- **💬 Real-time Chat**: Instant messaging with typing indicators
- **⚙️ Settings Panel**: Configurable User ID, API URL, and theme
- **📱 Responsive**: Works on desktop, tablet, and mobile
- **⌨️ Keyboard Shortcuts**: Quick navigation and actions
- **🔄 Auto-scroll**: Automatically scrolls to new messages
- **🛠️ Error Handling**: Graceful error messages and connection status
- **💾 Local Storage**: Remembers user settings

## 🛠️ Setup

### Prerequisites
- Backend API running (see main README.md)
- Modern web browser

### Quick Start

1. **Start the Backend**:
   ```bash
   # From project root
   docker-compose up -d
   ```

2. **Open Frontend**:
   ```bash
   # Method 1: Direct file opening
   start frontend/index.html

   # Method 2: Simple HTTP server
   cd frontend
   python -m http.server 3000
   # Open http://localhost:3000
   ```

3. **Start Chatting!**
   - Type your message in the input field
   - Press Enter or click the send button
   - Enjoy the conversation!

## 🎯 Usage

### Basic Chat
1. Type your message in the input field
2. Press Enter or click the send button (📤)
3. Wait for the AI response
4. Continue the conversation!

### Settings
Click the settings icon (⚙️) to:
- **Change User ID**: Set your unique identifier
- **Update API URL**: Point to different backend instances
- **Switch Theme**: Light/Dark mode (coming soon)

### Keyboard Shortcuts
- **Ctrl + /**: Focus on message input
- **Escape**: Close settings modal
- **Enter**: Send message

### Message Features
- **Typing Indicator**: Shows when AI is responding
- **Timestamps**: Each message shows send time
- **Message History**: Conversations persist in sessions
- **Error Handling**: Clear error messages for connection issues

## 🏗️ Project Structure

```
frontend/
├── index.html          # Main chat interface
├── css/
│   └── style.css       # Styles and animations
└── js/
    └── chat.js         # Chat logic and API calls
```

## 🎨 Customization

### Colors and Themes
Edit `css/style.css` to customize:
```css
:root {
    --primary-color: #007bff;    /* Main theme color */
    --secondary-color: #6c757d;  /* Secondary elements */
    --success-color: #28a745;    /* Success states */
    --background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
```

### API Configuration
Default API endpoint is `http://localhost:8000`. Change in settings or modify `js/chat.js`:
```javascript
this.apiUrl = 'http://your-api-endpoint:port';
```

### Adding Features
The frontend is built with vanilla JavaScript for easy customization:

- **New Message Types**: Add to `addMessage()` function
- **Additional Settings**: Extend the settings modal
- **Custom Animations**: Modify CSS animations
- **New API Endpoints**: Add methods to `ChatbotUI` class

## 🔧 API Integration

### Chat Endpoint
```javascript
POST /api/chatbot/interact
{
    "user_id": "user123",
    "message": "Hello!",
    "session_id": "optional_session_id"
}
```

### Response Format
```javascript
{
    "session_id": "sess_123456",
    "reply": "Hello! How can I help you?",
    "history": [...]
}
```

## 📱 Browser Support

- ✅ Chrome 80+
- ✅ Firefox 75+
- ✅ Safari 13+
- ✅ Edge 80+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## 🐛 Troubleshooting

### Common Issues

**"Cannot connect to API"**
- Ensure backend is running on `http://localhost:8000`
- Check CORS settings in backend
- Verify API URL in settings

**"Messages not sending"**
- Check browser console for errors
- Verify User ID is set
- Ensure backend `/api/chatbot/interact` endpoint is accessible

**"Styling issues"**
- Clear browser cache
- Check CSS file paths
- Ensure modern browser support

### Debug Mode
Open browser Developer Tools (F12) to:
- View network requests
- Check console errors
- Inspect element styles
- Monitor API calls

## 🚀 Deployment

### For Production
1. **Build optimized version**:
   ```bash
   # Minify CSS and JS (optional)
   # Use a proper web server instead of file:// protocol
   ```

2. **Serve with web server**:
   ```bash
   # Nginx example
   server {
       listen 80;
       root /path/to/frontend;
       index index.html;
   }
   ```

3. **Update API URLs**:
   - Change default API URL in settings
   - Update CORS origins in backend

### CDN Deployment
Host on services like:
- GitHub Pages
- Netlify
- Vercel
- Firebase Hosting

## 🤝 Contributing

### Code Style
- Use modern ES6+ JavaScript
- Follow CSS custom properties for theming
- Add comments for complex logic
- Test on multiple browsers

### Adding New Features
1. Plan the feature and API requirements
2. Implement in `chat.js`
3. Update styles in `style.css`
4. Test thoroughly
5. Update this documentation

## 📄 License

Same as main project - see main README.md

---

**Enjoy chatting with CHATBOTAI! 🤖✨**
