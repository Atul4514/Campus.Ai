# CampusAI 🎓

A college management system with an integrated AI chatbot, built with Django and a RAG-based (Retrieval-Augmented Generation) AI pipeline. CampusAI lets students and faculty manage academic data — attendance, timetables, notices, notes — and get instant, grounded answers from an AI chatbot that only responds using the college's own uploaded notes and structured data (no hallucinated or off-topic answers).

---

## ✨ Features

- 🔐 **Secure, college-restricted registration** — only pre-approved college IDs (managed via an admin allowlist) can create an account
- 👥 **Role-based access** — separate experiences and permissions for Students, Faculty, and Admins
- 📊 **Role-specific dashboards** — modern glassmorphism UI with dark mode
- 🔑 **Full authentication flow** — registration, login, logout, and email-based forgot-password
- 🤖 **AI Chatbot Engine** *(in progress)* — hybrid query router that answers structured questions (attendance, timetable) directly from the database, and content questions from uploaded faculty notes via a RAG pipeline — strictly grounded, no hallucination
- 📄 **Notes management** — faculty-uploaded PDFs/DOCX are automatically parsed and text-extracted for the AI pipeline
- ✅ **Attendance tracking** *(in progress)*
- 🗓️ **Timetable management** *(planned)*
- 📢 **Notice board** *(planned)*
- 📈 **Analytics dashboard** *(planned)*
- 🔔 **Notification system** *(planned)*

---

## 🛠️ Tech Stack

**Backend**
- Python 3.10+
- Django 5.2
- Django REST Framework

**Database**
- SQLite (development)
- PostgreSQL (production-ready)

**AI / Chatbot**
- LangChain — RAG orchestration
- FAISS — vector similarity search
- Sentence Transformers — local embedding generation
- OpenAI API — LLM for grounded response generation
- pypdf / python-docx — document text extraction

**Frontend**
- Django Templates
- Bootstrap 5
- Vanilla JavaScript
- Custom CSS (glassmorphism, dark mode)

**Auth & Security**
- Django's built-in auth system, extended with a custom `User` model
- College ID allowlist validation
- Role-based DRF permission classes

**Other**
- python-decouple — environment variable management
- django-cors-headers — CORS handling
- Git & GitHub — version control

---

## 📦 Project Modules

| # | Module | Status |
|---|--------|--------|
| 1 | Authentication & College ID Validation | ✅ Complete |
| 2 | Role & Access Management | ✅ Complete |
| 3 | Student Management | 🚧 In Progress |
| 4 | Faculty Management | ⏳ Planned |
| 5 | Attendance Management | 🚧 Minimal model in place |
| 6 | Timetable Management | ⏳ Planned |
| 7 | Notice Board | ⏳ Planned |
| 8 | Notes & Document Management | 🚧 Minimal model in place |
| 9 | AI Chatbot Engine | ⏳ Planned |
| 10 | Chat History & Session Management | ⏳ Planned |
| 11 | Analytics & Reports Dashboard | ⏳ Planned |
| 12 | Notification System | ⏳ Planned |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher
- pip
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Atul4514/CampusAi.git
   cd CampusAi
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   ```
   Windows:
   ```bash
   venv\Scripts\activate
   ```
   Mac/Linux:
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   Create a `.env` file in the project root (see `.env.example` for reference) with:
   ```
   SECRET_KEY=your-django-secret-key
   DEBUG=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-gmail-app-password
   OPENAI_API_KEY=your-openai-api-key
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. Visit `http://127.0.0.1:8000/` in your browser.

---

## 📁 Project Structure

```
CampusAi/
├── accounts/           # Authentication, custom User model, college ID allowlist
├── core/                # Shared utilities, reusable DRF permission classes
├── academics/           # Attendance (and future timetable/notices) models
├── documents/            # Notes upload & text extraction for RAG pipeline
├── students/              # Student academic profiles
├── collegemgmt/            # Project settings, root URLs
├── templates/               # HTML templates (Bootstrap-styled, dark mode support)
├── manage.py
├── requirements.txt
└── .env                       # Environment variables (not committed)
```

---

## 🔒 Security Notes

- Only college IDs pre-approved by an admin (via the `CollegeIDAllowlist`) can register — this prevents outside users from creating accounts
- Role (`student` / `faculty` / `admin`) is assigned from the allowlist entry, never chosen by the user at registration
- Sensitive credentials are stored in `.env`, excluded from version control via `.gitignore`

---

## 🗺️ Roadmap

- [ ] Complete Student & Faculty management modules
- [ ] Build out full Attendance, Timetable, and Notice Board UI
- [ ] Implement the AI Chatbot Engine with LangChain + FAISS + OpenAI
- [ ] Add chat history and session management
- [ ] Build the analytics dashboard for admins
- [ ] Add in-app and email notifications
- [ ] Deploy to production (Render/Railway + managed PostgreSQL)

---

## 👤 Author

**Atul Yadav**
Third-year Computer Science student, focused on software engineering and data engineering.

---

## 📄 License

This project is for educational/portfolio purposes.
