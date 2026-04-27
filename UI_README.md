# StudyMind AI - Modern UI

A beautiful, modern web interface for your AI Study Assistant built with Tailwind CSS and jQuery.

## ✨ Features

- **Modern Design**: Sleek dark theme with gold accents
- **Responsive Layout**: Fixed sidebar with scrollable content area
- **Interactive Flashcards**: Click to flip cards with 3D animation
- **Rich MCQ Display**: Color-coded correct answers
- **Real-time Chat**: Beautiful chat interface for Q&A
- **Smooth Animations**: Fade-in effects and transitions
- **Loading States**: Professional loading overlays
- **Notifications**: Toast notifications for user feedback

## 🚀 Quick Start

### 1. Start the FastAPI Backend

```bash
# In terminal 1
uvicorn main:app --reload
```

The backend will run on `http://localhost:8000`

### 2. Start the UI Server

```bash
# In terminal 2
python server.py
```

The UI will be available at `http://localhost:3000`

### 3. Open in Browser

Navigate to: **http://localhost:3000**

## 📁 Files

- `index.html` - Main HTML structure with Tailwind CSS
- `app.js` - jQuery-based JavaScript for all functionality
- `server.py` - Simple Python HTTP server to serve the UI

## 🎨 Design Features

### Color Scheme
- **Primary**: Gold (#C9A84C, #E8C96A)
- **Background**: Dark gradients (#0f0f12, #1a1a1f)
- **Accents**: Green for success, Red for errors

### Components
- **Sidebar**: Fixed left sidebar with upload and status
- **Stats Cards**: Three cards showing session statistics
- **Tabs**: Four main sections (Ask, MCQ, Flashcards, History)
- **Flashcards**: 3D flip animation on click
- **MCQs**: Highlighted correct answers with badges
- **Chat**: Bubble-style messages with user/AI distinction

### Animations
- Fade-in effects for new content
- Card hover effects with lift
- Pulse animation for active status
- Smooth tab transitions
- 3D flip for flashcards

## 🔧 Customization

### Change Colors
Edit the Tailwind config in `index.html`:

```javascript
tailwind.config = {
    theme: {
        extend: {
            colors: {
                gold: {
                    DEFAULT: '#C9A84C',  // Change this
                    light: '#E8C96A',
                    dark: '#A68A3D',
                }
            }
        }
    }
}
```

### Change Port
Edit `server.py`:

```python
PORT = 3000  # Change to your preferred port
```

### API URL
Edit `app.js`:

```javascript
const API_URL = 'http://localhost:8000';  // Change if needed
```

## 📱 Browser Support

- Chrome/Edge (recommended)
- Firefox
- Safari
- Opera

## 🐛 Troubleshooting

### "Cannot reach backend" error
- Make sure FastAPI is running: `uvicorn main:app --reload`
- Check that it's on port 8000
- Verify CORS is enabled in FastAPI

### Flashcards not flipping
- Make sure jQuery is loaded (check browser console)
- Clear browser cache and reload

### Styles not loading
- Check internet connection (Tailwind loads from CDN)
- Try hard refresh (Ctrl+Shift+R)

## 🎯 Usage Tips

1. **Upload PDF**: Click the upload area in sidebar
2. **Process**: Click "Process PDF" button
3. **Ask Questions**: Type in the input and press Enter or click Ask
4. **Generate MCQs**: Enter topic and select count, then generate
5. **Create Flashcards**: Enter topic, select count, click to flip cards
6. **View History**: Switch to History tab to see saved items

## 🔄 Comparison with Streamlit

### Advantages
- ✅ Faster load times
- ✅ More control over UI/UX
- ✅ Better animations and transitions
- ✅ No reloading on interactions
- ✅ True single-page application
- ✅ Easier to customize

### Streamlit Advantages
- ✅ Faster development
- ✅ Python-only (no JavaScript needed)
- ✅ Built-in components

## 📝 Notes

- The UI communicates with the same FastAPI backend
- All data processing happens on the backend
- Frontend is purely for display and interaction
- No authentication implemented (add if needed)

## 🚀 Production Deployment

For production, consider:
1. Use a proper web server (nginx, Apache)
2. Minify JavaScript and CSS
3. Add authentication
4. Use environment variables for API URL
5. Enable HTTPS
6. Add error tracking (Sentry, etc.)

## 📄 License

Same as the main project

---

**Enjoy your modern AI Study Assistant! 🎓✨**
