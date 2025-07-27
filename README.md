# QGenie Backend App - AI Agentic Evaluation Partner

QGenie is an AI-powered backend application that serves as an intelligent evaluation partner, designed to assist educators and institutions in assessment and educational tasks.

## 🚀 Features

- Firebase Authentication Integration
- Chat Interface with AI
- Paper Properties Management
- Institution Management
- Educational Tools and Services
- Database Management System
- RESTful API Endpoints

## 📋 Prerequisites

- Python 3.8+
- Firebase Account and Credentials
- PostgreSQL Database

## 🛠️ Project Structure

```
backend/
├── assets/              # Static assets and knowledge base
├── auth/               # Authentication related modules
├── chat/              # AI chat implementation
├── db/                # Database configurations and models
├── educator/          # Educator-specific routes
├── institutions/      # Institution management
├── paper_props/       # Paper properties management
└── main.py           # Application entry point
```

## 🔧 Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd gGenie-be/backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Set up Firebase credentials:
- Place your `firebase_service_account.json` in the root directory
- Update Firebase configuration in `auth/firebase_utils.py`

5. Initialize the database:
```bash
python -m db.reset_db
```

## 🚀 Running the Application

Start the development server:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## 🔒 Authentication

The application uses Firebase Authentication. Make sure to:
- Configure Firebase in your frontend application
- Use the provided JWT tokens in your API requests
- Include the token in the Authorization header: `Bearer <token>`

## 📚 API Documentation

Once the server is running, access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🧪 Testing

Run the test suite:

```bash
pytest
```

## 📝 License

[License Type] - See LICENSE file for details

## 👥 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

For support, please contact [support contact information]
