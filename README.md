# MedPro - Healthcare Management System

A comprehensive Flask-based healthcare management system with AI-powered disease prediction, appointment scheduling, and file management capabilities.

## 🚀 Features

- **AI Disease Prediction**: Machine learning-based symptom analysis and disease prediction
- **User Authentication**: Secure multi-level user authentication system
- **Appointment Management**: Comprehensive appointment booking and scheduling
- **File Management**: Secure document upload, storage, and management
- **Dashboard**: User-friendly dashboard with analytics and quick actions
- **Responsive Design**: Mobile-friendly interface built with Bootstrap 5
- **SQL Database**: SQLite database with SQLAlchemy ORM
- **Security**: Password hashing, session management, and role-based access

## 🛠️ Technology Stack

- **Backend**: Flask 3.0, Python 3.11+
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: Bootstrap 5, Font Awesome, jQuery
- **AI/ML**: Scikit-learn, Random Forest Classifier
- **Authentication**: Flask-Login, Werkzeug security
- **Deployment**: Netlify-ready configuration

## 📋 Prerequisites

- Python 3.11 or higher
- pip package manager
- Git (for version control)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd MedPro
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

### 4. Access the System

- **Default Admin Account**: 
  - Username: `admin`
  - Password: `admin123`

## 🗄️ Database Setup

The application automatically creates the database and tables on first run. The SQLite database file (`medpro.db`) will be created in the project root.

### Database Models

- **User**: User accounts with role-based access
- **Appointment**: Patient appointment records
- **UploadedFile**: File management and storage
- **Contact**: Contact form submissions

## 🔐 User Types

- **User Type A**: Full access to all features (Primary users)
- **User Type B**: Limited access, requires User A approval (Secondary users)

## 📱 Key Pages

- **Home**: Landing page with feature overview
- **Dashboard**: User dashboard with files, appointments, and quick actions
- **Disease Prediction**: AI-powered symptom analysis
- **Appointment Booking**: Schedule medical appointments
- **File Management**: Upload, view, and manage medical documents
- **About/Services**: Information about the healthcare facility

## 🚀 Deployment to Netlify

### 1. Prepare for Deployment

```bash
python deploy.py
```

### 2. Commit and Push

```bash
git add .
git commit -m "Prepare for Netlify deployment"
git push origin main
```

### 3. Deploy on Netlify

1. Go to [Netlify](https://netlify.com)
2. Click "New site from Git"
3. Connect your repository
4. Set build settings:
   - Build command: `pip install -r requirements.txt`
   - Publish directory: `.`
5. Click "Deploy site"

### 4. Environment Variables

Set these environment variables in Netlify:

- `FLASK_ENV`: `production`
- `SECRET_KEY`: Your secure secret key
- `DATABASE_URL`: Your production database URL

## 🔧 Configuration

### Environment Variables

Create a `.env` file (not included in repository):

```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-super-secret-key-change-this-in-production
DATABASE_URL=sqlite:///medpro.db
```

### File Upload Settings

- Maximum file size: 16MB
- Supported formats: PDF, DOC, DOCX, JPG, PNG
- Upload directory: `uploads/`

## 🧪 Testing

### Run Tests

```bash
python -m pytest tests/
```

### Manual Testing

1. Create a new user account
2. Test file upload functionality
3. Book an appointment
4. Test disease prediction
5. Verify user authentication

## 📊 AI Model

The disease prediction system uses a Random Forest Classifier trained on medical symptom data. The model:

- Analyzes up to 5 symptoms
- Provides disease predictions with confidence levels
- Supports 40+ different diseases
- Uses 132 different symptoms for analysis

## 🔒 Security Features

- Password hashing with Werkzeug
- Session management with Flask-Login
- Role-based access control
- Secure file upload validation
- SQL injection prevention with SQLAlchemy

## 📁 Project Structure

```
MedPro/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── netlify.toml          # Netlify configuration
├── runtime.txt           # Python runtime version
├── Procfile             # Process file for deployment
├── deploy.py            # Deployment script
├── README.md            # This file
├── templates/           # HTML templates
│   ├── base.html       # Base template
│   ├── index.html      # Home page
│   ├── login.html      # Login page
│   ├── signup.html     # Registration page
│   ├── dashboard.html  # User dashboard
│   ├── predict.html    # Disease prediction
│   ├── appointment.html # Appointment booking
│   ├── contact.html    # Contact form
│   ├── about.html      # About page
│   ├── services.html   # Services page
│   ├── doctors.html    # Doctors page
│   └── departments.html # Departments page
├── static/              # Static assets (CSS, JS, images)
├── uploads/             # File upload directory
└── medpro.db           # SQLite database (created on first run)
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Database Errors**: Delete `medpro.db` and restart the application
3. **File Upload Issues**: Check upload directory permissions
4. **Port Conflicts**: Change port in `app.py` if 5000 is busy

### Logs

Check console output for error messages and debugging information.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Contact: support@medpro.com
- Documentation: [Wiki](link-to-wiki)

## 🔄 Updates

### Version 2.0.0
- Complete rewrite with modern Flask architecture
- SQL database integration
- Enhanced security features
- Responsive Bootstrap 5 design
- Netlify deployment support

### Future Plans
- Multi-language support
- Advanced analytics dashboard
- Mobile app development
- Integration with external healthcare systems
- Advanced AI features

---

**Note**: This is a demonstration system. For production use in healthcare, ensure compliance with relevant regulations (HIPAA, GDPR, etc.) and implement additional security measures.

