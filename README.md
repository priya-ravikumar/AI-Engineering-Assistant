# AI Engineering Assistant

An AI-powered web application for equipment troubleshooting and maintenance ticket management.

## Project Overview

The AI Engineering Assistant helps users describe equipment problems, receive preliminary troubleshooting guidance, create maintenance tickets, and track issue status through a dashboard.

## Features

- AI-assisted equipment troubleshooting
- Optional Google Gemini API integration
- Rule-based fallback responses
- Maintenance ticket creation
- Ticket priority management: Low, Medium, High
- Ticket status tracking: Open, In Progress, Resolved
- Dashboard with ticket statistics
- SQLite database for persistent storage
- Responsive web interface

## Technologies Used

- Python
- Flask
- HTML
- CSS
- JavaScript
- SQLite
- Google Gemini API
- Git and GitHub

## Project Structure

```text
AI-Engineering-Assistant/
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Installation

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd AI-Engineering-Assistant
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the environment on Windows

```powershell
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure the Gemini API (Optional)

Set your API key as an environment variable in PowerShell:

```powershell
$env:GEMINI_API_KEY="YOUR_API_KEY"
```

Keep your API key private. Do not upload it to GitHub.

The application also supports fallback troubleshooting responses when Gemini is unavailable.

### 6. Run the application

```bash
python app.py
```

Open this address in your browser:

http://127.0.0.1:5000

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Open the application |
| POST | `/api/chat` | Get troubleshooting guidance |
| GET | `/api/tickets` | Retrieve maintenance tickets |
| POST | `/api/tickets` | Create a maintenance ticket |
| PATCH | `/api/tickets/<ticket_id>` | Update ticket status |

## Safety Notice

This application is a portfolio demonstration. Troubleshooting suggestions are preliminary and must be verified by a qualified engineer.

## Author

Priya Ravikumar

GitHub: https://github.com/priya-ravikumar
