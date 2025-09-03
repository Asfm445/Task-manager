# 📝 Task Manager (Full Stack)

A **full-stack Task Manager application** with:  
- **Backend**: FastAPI + SQLAlchemy (clean architecture, JWT auth)  
- **Frontend**: React + Tailwind(with modern UI components, API integration)  
- **Database**: PostgreSQL   
- **Testing**: Pytest + Testify for backend  

---

## 📖 Project Description

The **Task Manager** is a full-stack productivity application that allows users to efficiently plan, track, and complete tasks with advanced features beyond simple CRUD.  

### 🔹 Task Management Logic
- **Task Types**  
  - **Fixed tasks** – one-time tasks with defined `estimated_hours` and `done_hours`.  
  - **Repetitive tasks** – tasks that reset progress at every interval (`start → end` period).  

- **Completion Rules**  
  - A task is **completed** when `done_hours >= estimated_hours`.  
  - Tasks can have **subtasks**.  
    - If all subtasks are complete and their combined `estimated_hours` ≥ parent task’s `estimated_hours`, the parent task is marked as **completed**.  
  - For **repetitive tasks**, `done_hours` resets at the end of each interval, but progress history is tracked.  

### 🔹 Daily Planning & Time Tracking
- Users create a **Daily Plan**.  
- Each plan contains **Time Logs**, which represent actual working sessions:  
  - Attributes: `start_time`, `end_time`, `done`, `task_id`.  
  - **No overlapping logs** are allowed.  
  - When a user marks a task as *done* for that time period, the system:  
    - Creates a **Time Log**.  
    - Increases `done_hours` by `(end_time - start_time)`.  
    - If a task is completed, its contribution (`estimated_hours`) is rolled up to its parent task, continuing recursively until the **main task** is updated.  

This design makes the Task Manager suitable for **personal productivity, project planning, and tracking recurring tasks**.  

---

## 🚀 Features
- 👤 User registration, login, and profile management  
- ✅ Task CRUD (create, update, delete, mark complete)  
- 🔁 Support for repetitive and fixed tasks  
- 📊 Task hierarchy with subtasks and roll-up completion  
- ⏱️ Daily plan with non-overlapping time logs  
- 🔒 JWT authentication with protected routes  
- 🧪 Unit & integration tests (backend + frontend)  
- 📖 API docs with Swagger & ReDoc  

---

## 🛠️ Tech Stack
### Backend
- FastAPI  
- SQLAlchemy ORM  
- PostgreSQL / SQLite  
- JWT Authentication  
- Pytest + Testify  

### Frontend
- React + Vite  
- Axios (API calls)  
- TailwindCSS   
- React Router  
- React Query (optional)  

### DevOps
- Docker + docker-compose  
- GitHub Actions (CI/CD ready)  

---

## 📂 Project Structure
```
task-manager/
│── backend/
│   ├── app/
│   │   ├── controllers/
│   │   ├── usecases/
│   │   ├── infrastructure/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── main.py
│   └── tests/
│
│── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── App.jsx
│   └── package.json
│
│── docker-compose.yml
│── README.md
```

---

## ⚡ Setup & Installation

### 1️⃣ Clone Repository
```bash
git clone https://github.com/your-username/task-manager.git
cd task-manager
```

---

### 2️⃣ Backend Setup (FastAPI)
```bash
cd backend
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API available at: [http://localhost:8000](http://localhost:8000)  

Docs:  
- Swagger: `/docs`  
- ReDoc: `/redoc`  

---

### 3️⃣ Frontend Setup (React)
```bash
cd frontend
npm install
npm run dev
```

Frontend available at: [http://localhost:5173](http://localhost:5173)  

---

### 4️⃣ Docker Setup (Optional)
```bash
docker-compose up --build
```

---

## 🧪 Running Tests

### Backend
```bash
pytest
```

### Frontend
```bash
npm test
```

---

## 🔑 Example API Calls

### Register User
```http
POST /users/
{
  "username": "awel",
  "email": "awel@example.com",
  "password": "securepass"
}
```

### Create Task
```http
POST /tasks/
{
  "title": "Finish project",
  "description": "Complete full-stack task manager",
  "assignees": [1, 2]
}
```

---

## 📌 Roadmap
- [ ] Add role-based permissions  
- [ ] Implement notifications and reminders  
- [ ] Add file attachments for tasks  
- [ ] Deploy to AWS/DigitalOcean  

---

## 🤝 Contributing
Contributions are welcome:  
1. Fork repo  
2. Create feature branch  
3. Commit changes  
4. Open PR  

---

## 📜 License
MIT License  
