# 💰 CebimdekiVeri - Personal Budget Management & Prediction System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.1.0-green?logo=fastapi)
![React](https://img.shields.io/badge/React-18.2.0-blue?logo=react)
![Firebase](https://img.shields.io/badge/Firebase-11.0.0-orange?logo=firebase)
![License](https://img.shields.io/badge/License-MIT-yellow)

**An intelligent personal finance management system with AI-powered predictions and real-time analytics**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Architecture](#-architecture) • [Contributing](#-contributing)

</div>

---

## 📖 About

**CebimdekiVeri** (Data in My Pocket) is a comprehensive full-stack personal budget management application that helps users track income and expenses, analyze spending patterns, and predict future financial situations using statistical algorithms and AI-powered insights.

This project was developed as part of a **System Analysis and Design** course, implementing Object-Oriented Programming (OOP) principles and Software Design Patterns to create a robust, scalable, and maintainable financial management system.

### 🎯 Purpose

The application aims to:
- **Simplify Budget Tracking**: Provide an intuitive interface for recording income and expenses
- **Enable Data-Driven Decisions**: Analyze historical spending patterns to generate actionable insights
- **Predict Future Finances**: Use statistical methods (Moving Average) to forecast upcoming month expenses
- **Offer AI-Powered Advice**: Leverage AI services (Gemini/OpenAI) to provide personalized financial recommendations
- **Visualize Financial Health**: Create comprehensive charts and reports for better understanding

---

## ✨ Features

### Core Functionality
- 📊 **Transaction Management**: Add, edit, and categorize income and expenses with detailed metadata
- 💳 **Multi-User Support**: Firebase authentication enables secure multi-user access
- 📅 **Date-Based Tracking**: Record transactions with custom dates for historical accuracy
- 🏷️ **Categorization**: Organize expenses by categories (e.g., Food, Transportation, Entertainment)
- 📈 **Real-Time Balance**: Automatic calculation of current balance based on all transactions

### Analytics & Predictions
- 🔮 **Future Prediction**: Forecast next month's expenses using Moving Average method
- 📊 **Visual Analytics**: Interactive charts showing income-expense trends and category distribution
- 📉 **Trend Analysis**: Identify spending patterns over time with line and pie charts
- 📄 **Report Generation**: Export financial reports in multiple formats (PDF/Excel simulation)

### AI & Intelligence
- 🤖 **AI Financial Assistant**: Get personalized financial advice using Gemini or OpenAI APIs
- 💬 **Chat Interface**: Interactive chat system for financial queries and recommendations
- 🧠 **Smart Notifications**: Observer pattern-based alert system for low balance or negative balance warnings

### Technical Excellence
- 🏗️ **Design Patterns**: Singleton, Observer, Factory, and Strategy patterns for clean architecture
- 🔒 **Secure Backend**: FastAPI with Firebase Admin SDK for secure data management
- 🎨 **Modern Frontend**: React with Vite, Tailwind CSS for responsive and beautiful UI
- ☁️ **Cloud Database**: Firebase Firestore for scalable, real-time data storage

---

## 🛠️ Tech Stack

### Backend
- **Python 3.x** - Core programming language
- **FastAPI** - Modern, fast web framework for building APIs
- **Firebase Admin SDK** - Server-side Firebase integration
- **Pandas** - Data analysis and manipulation
- **Matplotlib & Seaborn** - Data visualization
- **Uvicorn** - ASGI server for FastAPI

### Frontend
- **React 18** - UI library
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **Recharts** - Chart library for React
- **Axios** - HTTP client
- **Firebase SDK** - Client-side Firebase integration

### Infrastructure
- **Firebase/Firestore** - NoSQL cloud database
- **Firebase Authentication** - User authentication
- **Firebase Hosting** - Static site hosting (optional)

### AI Services
- **Google Gemini API** - Primary AI service
- **OpenAI API** - Fallback AI service
- **Local Heuristics** - Fallback when APIs unavailable

---

## 🏗️ Architecture

### Design Patterns

The project implements several software design patterns to ensure maintainability and scalability:

1. **Singleton Pattern** (Budget Manager)
   - Ensures a single instance of the budget manager across the application
   - Maintains data consistency and centralized state management

2. **Observer Pattern** (User)
   - Implements event-driven notifications for budget state changes
   - Users are automatically notified when balance reaches critical levels

3. **Factory Pattern** (Report Factory, Transaction Factory)
   - Dynamically creates report objects (PDF/Excel) based on user preferences
   - Creates transaction objects (Income/Expense) with appropriate configurations

4. **Strategy/Template Pattern**
   - Abstract base class with Income and Expense implementations
   - Enables extensible transaction types through inheritance

### Project Structure

```
CebimdekiVeri/
├── backend/                 # Backend API and services
│   ├── main.py             # FastAPI application entry point
│   ├── sistem_modelleri.py # Core domain models (OOP classes)
│   ├── grafik_analiz.py    # Data analysis and visualization
│   ├── ai_service.py       # AI integration (Gemini/OpenAI)
│   └── firebase_config.py  # Firebase Admin SDK configuration
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── pages/         # Page components (Dashboard, Transactions, etc.)
│   │   ├── components/    # Reusable UI components
│   │   ├── layouts/       # Layout components
│   │   └── api.js         # API client
│   └── package.json
├── docs/                   # Documentation
│   └── README_UML.md      # UML class diagrams
├── requirements.txt        # Python dependencies
├── firebase.json          # Firebase project configuration
├── firestore.rules        # Firestore security rules
└── README.md              # This file
```

---

## 🚀 Installation

### Prerequisites

- **Python 3.8+**
- **Node.js 20+** and npm
- **Firebase Account** (for cloud features)
- **Git**

### Step 1: Clone the Repository

```bash
git clone https://github.com/KoiosTR/CebimdekiVeri.git
cd CebimdekiVeri
```

### Step 2: Backend Setup

1. Create a virtual environment (recommended):

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

3. Configure Firebase:

   - Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
   - Download your `serviceAccountKey.json` file
   - Place it in the project root directory
   - **Important**: This file is in `.gitignore` and should never be committed to version control

4. Set up environment variables (optional):

```bash
# Create a .env file
FIREBASE_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=./serviceAccountKey.json
GEMINI_API_KEY=your-gemini-api-key  # Optional
OPENAI_API_KEY=your-openai-api-key  # Optional
```

### Step 3: Frontend Setup

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Configure Firebase for frontend:

   - Create a `.env` file in the `frontend/` directory:

```env
VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
VITE_FIREBASE_APP_ID=your-app-id
```

### Step 4: Run the Application

1. **Start the Backend Server** (from project root):

```bash
# Activate virtual environment if not already active
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # macOS/Linux

# Run FastAPI server
uvicorn backend.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

2. **Start the Frontend Development Server** (from `frontend/` directory):

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

---

## 💻 Usage

### Terminal Application (Legacy)

The project includes a terminal-based interface for quick testing:

```bash
python main.py
```

This will launch an interactive menu where you can:
1. Add income transactions
2. Add expense transactions
3. View current balance
4. Generate charts and analysis
5. Export reports

### Web Application

1. Open `http://localhost:5173` in your browser
2. Sign in with Firebase Authentication
3. Navigate through:
   - **Dashboard**: Overview of financial status
   - **Transactions**: Add and manage income/expenses
   - **Chat**: Interact with AI financial assistant
   - **Settings**: Configure preferences

### API Endpoints

The FastAPI backend provides RESTful endpoints:

- `GET /api/transactions` - Get all transactions
- `POST /api/transactions` - Create a new transaction
- `GET /api/balance` - Get current balance
- `GET /api/analysis` - Get financial analysis summary
- `POST /api/chat` - Chat with AI assistant
- `POST /api/ai-analysis` - Get AI-powered financial insights

Full API documentation available at `/docs` when the server is running.

---

## 📊 Features in Detail

### Transaction Management

Transactions support:
- **Income**: Regular/irregular income sources with tax estimation
- **Expenses**: Categorized expenses with optional/recurring flags
- **Installments**: Support for installment-based payments
- **Custom Dates**: Record transactions for any date (past or future)

### Predictive Analytics

The system uses a **Moving Average** method to predict next month's expenses:
- Analyzes last 3 months of spending data
- Calculates weighted averages
- Provides confidence intervals
- Generates visual trend lines

### AI Integration

The AI service attempts multiple providers in order:
1. **Google Gemini API** (primary)
2. **OpenAI API** (fallback)
3. **Local Heuristics** (if APIs unavailable)

AI features include:
- Financial advice generation
- Spending pattern analysis
- Budget recommendations
- Chat-based Q&A

---

## 🔒 Security

### Important Security Notes

- **Never commit `serviceAccountKey.json`** - This file contains sensitive Firebase credentials
- **Review `firestore.rules`** - Current rules are date-based and public; tighten for production
- **Use environment variables** - Store API keys in `.env` files (not in version control)
- **Enable Firebase Authentication** - Implement proper user authentication for production

### Recommended Production Setup

1. Use Firebase App Check for API protection
2. Implement role-based access control (RBAC)
3. Add rate limiting to API endpoints
4. Enable Firebase Security Rules with authentication
5. Use HTTPS for all connections
6. Regularly rotate service account keys

---

## 🧪 Development

### Running Tests

```bash
# Backend tests (when available)
pytest

# Frontend tests (when available)
cd frontend
npm test
```

### Code Style

- **Python**: Follow PEP 8 guidelines
- **JavaScript**: Use ESLint configuration (when added)
- **Type Safety**: Consider adding type hints (Python) and TypeScript (frontend)

---

## 📝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Contribution Guidelines

- Write clear commit messages
- Follow existing code style
- Add comments for complex logic
- Update documentation as needed
- Test your changes thoroughly

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Firebase** - For providing excellent backend infrastructure
- **FastAPI** - For the modern Python web framework
- **React Team** - For the amazing UI library
- **Design Patterns Community** - For architectural inspiration

---

## 📧 Contact

**Project Maintainer**: [Arda Gonca]

- GitHub: [@KoiosTR](https://github.com/KoiosTR)
- Email: [ardagonca14@gmail.com]

---

<div align="center">

**Made with ❤️ for better financial management**

⭐ Star this repo if you find it helpful!

</div>
