# Task Manager

A comprehensive full-stack task management application built with modern technologies, featuring AI-powered insights, user authentication, and intuitive day planning.

## 🚀 Features

### Core Functionality
- **User Management**: Secure user registration, login, and authentication with JWT tokens
- **Task Management**: Create, update, and track tasks with status tracking (pending, in-progress, completed, stopped)
- **Subtasks**: Break down complex tasks into manageable subtasks
- **Day Planning**: Organize your day with time slots and task scheduling
- **Time Logging**: Track actual time spent on tasks vs. estimated time

### AI-Powered Features
- **AI Feedback**: Get intelligent feedback on task completion and performance
- **AI Recommendations**: Receive personalized suggestions for task management and productivity
- **Smart Insights**: Leverage AI to optimize your workflow and time allocation

### Additional Features
- **Email Notifications**: Automated email services for important updates
- **Role-Based Access**: Support for different user roles and permissions
- **Responsive UI**: Modern, mobile-friendly interface built with React
- **Real-time Updates**: Live updates using React Query for seamless user experience

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with async support
- **ORM**: SQLAlchemy with Alembic for migrations
- **Authentication**: JWT tokens with bcrypt password hashing
- **AI Integration**: Custom AI service for task insights
- **Email Service**: Async SMTP for notifications
- **Testing**: Pytest with async support
- **Containerization**: Docker & Docker Compose

### Frontend
- **Framework**: React 19 with Vite
- **Styling**: Tailwind CSS
- **State Management**: React Query (TanStack Query)
- **Routing**: React Router DOM
- **HTTP Client**: Axios
- **Date Handling**: date-fns with Flatpickr
- **Icons**: Lucide React & React Icons
- **Charts**: Recharts for data visualization

## 📋 Prerequisites

- Docker & Docker Compose
- Node.js (v18+) and npm
- Python 3.11+
- PostgreSQL (handled via Docker)

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Task-manager
   ```

2. **Backend Setup**
   ```bash
   cd backend
   cp .env.example .env  # Configure your environment variables
   docker-compose up --build
   ```

3. **Frontend Setup**
   ```bash
   cd ../frontend
   npm install
   npm run dev
   ```

4. **Database Migration**
   ```bash
   # In backend container or with proper env
   alembic upgrade head
   ```

## 🚀 Usage

### Development
- **Backend API**: Runs on `http://localhost:8000`
- **Frontend App**: Runs on `http://localhost:5173` (Vite dev server)
- **Database**: PostgreSQL on `localhost:5433`

### API Endpoints
- `POST /auth/login` - User authentication
- `GET /tasks` - Retrieve user tasks
- `POST /tasks` - Create new task
- `GET /dayplans` - Get day plans
- `POST /dayplans/{id}/times` - Add time slots to day plan

### Key Workflows
1. **Register/Login**: Create account or authenticate
2. **Create Tasks**: Add tasks with descriptions, deadlines, and estimates
3. **Plan Your Day**: Schedule tasks into time slots
4. **Track Progress**: Log time spent and mark tasks complete
5. **Get AI Insights**: Review AI feedback and recommendations

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm run test  # If configured
```

## 📚 API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation powered by Swagger UI.

## 🚢 Deployment

### Backend Deployment
```bash
cd backend
docker-compose -f docker-compose.prod.yml up --build
```

### Frontend Deployment
```bash
cd frontend
npm run build
# Deploy dist/ folder to your hosting service (Vercel, Netlify, etc.)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For questions or support, please open an issue in the GitHub repository.

---

**Built with ❤️ using FastAPI, React, and modern web technologies.**