# SoilStory Frontend

A modern, professional, and beautiful user interface for the SoilStory web application built with HTML, CSS, JavaScript, and Bootstrap.

## 🌟 Features

- **Modern Design**: Earthy color palette with professional styling
- **Responsive Layout**: Works perfectly on all screen sizes
- **Drag & Drop**: Easy photo upload with drag and drop support
- **Real-time Analysis**: Live soil property visualization with progress bars
- **AI Story Generation**: Display AI-generated soil stories
- **Video Generation**: Convert stories to educational videos
- **Local Storage**: All data stored locally in the browser
- **Search & History**: Browse and search through analysis history
- **Export Functionality**: Download analysis data as JSON
- **Accessibility**: Built with accessibility best practices

## 🎨 Design Features

### Color Palette
- **Soil Brown**: #8B4513
- **Leaf Green**: #228B22
- **Sage Green**: #9CAF88
- **Moss Green**: #8A9A5B
- **Sand Beige**: #F5F5DC
- **Clay Red**: #CD5C5C

### UI Components
- Modern card-based layout
- Smooth hover animations
- Progress bars for soil properties
- Responsive grid system
- Bootstrap 5 integration
- Custom scrollbars
- Loading states and spinners

## 📁 File Structure

```
frontend/
├── index.html              # Main landing & upload page
├── history.html            # Analysis history page
├── static/
│   ├── css/
│   │   └── style.css      # Custom styles with earthy theme
│   └── js/
│       ├── storage.js      # LocalStorage management
│       ├── api.js          # Backend API communication
│       └── main.js         # Main application logic
└── README.md               # This file
```

## 🚀 Quick Start

### 1. Open in Browser
Simply open `index.html` in any modern web browser. No build process required!

### 2. Test the Application
- Upload a soil photo (drag & drop supported)
- Enter location coordinates or use GPS
- Click "Analyze Soil" to see results
- Generate videos from AI stories
- View analysis history

### 3. Backend Integration
The frontend automatically detects if the backend is available:
- **Online Mode**: Connects to Flask backend for real analysis
- **Demo Mode**: Uses mock data when backend is unavailable

## 🛠️ Development

### Prerequisites
- Modern web browser (Chrome, Firefox, Safari, Edge)
- No Node.js or build tools required

### Local Development
1. Clone the repository
2. Open `index.html` in your browser
3. Make changes to HTML, CSS, or JavaScript
4. Refresh browser to see changes

### File Modifications

#### HTML Structure
- `index.html`: Main application page
- `history.html`: History and analysis gallery

#### Styling
- `static/css/style.css`: All custom styles
- Uses CSS custom properties for consistent theming
- Responsive breakpoints for mobile/tablet/desktop

#### JavaScript
- `static/js/storage.js`: Data persistence layer
- `static/js/api.js`: Backend communication
- `static/js/main.js`: UI logic and event handling

## 🔧 Configuration

### Backend URL
The frontend automatically detects the current domain. For development:
- Local: `http://localhost:5000`
- Production: Your deployed domain

### Local Storage
- Maximum 50 analyses stored locally
- Automatic cleanup when limit exceeded
- Export/import functionality for data backup

### Demo Mode
When backend is unavailable:
- Mock soil analysis data
- Simulated processing delays
- Sample AI stories
- Placeholder video generation

## 📱 Responsive Design

### Breakpoints
- **Mobile**: < 576px
- **Tablet**: 576px - 768px
- **Desktop**: > 768px

### Mobile Features
- Touch-friendly buttons
- Swipe gestures for navigation
- Optimized image upload
- Collapsible navigation menu

## ♿ Accessibility

### Features
- Semantic HTML5 structure
- ARIA labels and roles
- Keyboard navigation support
- High contrast mode support
- Screen reader compatibility
- Focus indicators

### Standards
- WCAG 2.1 AA compliance
- Semantic markup
- Proper heading hierarchy
- Alt text for images
- Form labels and validation

## 🎯 Browser Support

### Supported Browsers
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Required Features
- ES6+ JavaScript
- CSS Grid and Flexbox
- LocalStorage API
- Fetch API
- Geolocation API (optional)

## 🚀 Deployment

### Static Hosting
The frontend can be deployed to any static hosting service:

1. **Netlify**: Drag and drop the `frontend/` folder
2. **Vercel**: Connect GitHub repository
3. **GitHub Pages**: Push to `gh-pages` branch
4. **AWS S3**: Upload files to S3 bucket

### Build Process
No build process required! The application runs directly in the browser.

### Environment Variables
No environment variables needed for the frontend. All configuration is handled automatically.

## 🧪 Testing

### Manual Testing
1. **Photo Upload**: Test various image formats and sizes
2. **Location Services**: Test GPS and manual coordinate entry
3. **Analysis Flow**: Complete end-to-end analysis
4. **Video Generation**: Test video creation process
5. **History Management**: Test search, export, and deletion

### Browser Testing
- Test on different browsers
- Test responsive design on various screen sizes
- Test with different network conditions

## 🔒 Security Features

### Client-Side Security
- Input validation and sanitization
- File type and size restrictions
- XSS prevention through proper escaping
- CSRF protection through token validation

### Data Privacy
- All data stored locally in browser
- No data sent to external services without consent
- Optional location sharing
- Export/import for data portability

## 📊 Performance

### Optimization Features
- Lazy loading of images
- Efficient DOM manipulation
- Minimal external dependencies
- Optimized CSS animations
- Efficient localStorage operations

### Loading Times
- **Initial Load**: < 2 seconds
- **Photo Upload**: < 1 second
- **Analysis**: 2-5 seconds (backend dependent)
- **Video Generation**: 3-10 seconds (backend dependent)

## 🐛 Troubleshooting

### Common Issues

#### Photos Not Uploading
- Check file size (max 10MB)
- Ensure file is an image (JPG, PNG, GIF)
- Check browser console for errors

#### Analysis Not Working
- Verify backend server is running
- Check network connectivity
- Look for console error messages

#### Local Storage Issues
- Check browser storage quota
- Clear browser data if needed
- Ensure cookies are enabled

### Debug Mode
Open browser console to see:
- API request logs
- Storage operations
- Error messages
- Performance metrics

## 🤝 Contributing

### Development Guidelines
1. Follow existing code structure
2. Use semantic HTML
3. Maintain accessibility standards
4. Test on multiple browsers
5. Update documentation

### Code Style
- Use ES6+ features
- Follow JavaScript best practices
- Maintain consistent CSS naming
- Add comments for complex logic

## 📄 License

This project is part of the SoilStory application. See the main project license for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review browser console for errors
3. Check backend server status
4. Review documentation

---

**SoilStory Frontend** - Making soil analysis beautiful and accessible! 🌱
