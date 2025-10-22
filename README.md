# **Smart Resume Screener**

An AI-powered application designed to streamline the recruitment process by automatically parsing, analyzing, and ranking candidate resumes against job descriptions.

*(Replace the placeholder URL above with an actual screenshot of your application)*

## **Overview**

Finding the right candidate can be time-consuming. Smart Resume Screener helps recruiters and hiring managers quickly identify the most relevant candidates from a pool of applicants. By leveraging natural language processing and vector embeddings, it compares the semantic content of resumes against a given job description, providing a ranked list based on relevance.

## **✨ Features**

* **Resume Upload:** Supports uploading multiple resumes in PDF and DOCX formats.  
* **Automatic Parsing:** Extracts text and intelligently splits resumes into key sections (Contact Info, Summary, Skills, Experience, Education).  
* **Semantic Analysis:** Generates vector embeddings for resume sections and job descriptions using Sentence Transformers (all-MiniLM-L6-v2 by default).  
* **Efficient Indexing:** Uses FAISS (Facebook AI Similarity Search) for fast vector similarity searches.  
* **Candidate Ranking:** Ranks uploaded resumes against a provided job title and description based on semantic similarity scores.  
* **Web Interface:** User-friendly interface built with React, Vite, shadcn/ui, and Tailwind CSS for uploading resumes and viewing ranked results.  
* **Data Management:** Allows resetting the candidate database and search index.  
* **Dockerized:** Easily deployable using Docker and Docker Compose for consistent environments.

## **🛠️ Tech Stack**

**Backend (backend/):**

* **Framework:** FastAPI  
* **Language:** Python 3.9  
* **Database:** SQLAlchemy with SQLite (default, persistent via Docker volume)  
* **Embeddings:** Sentence Transformers (sentence-transformers)  
* **Vector Index:** FAISS (faiss-cpu)  
* **Parsing:** PyMuPDF (fitz), python-docx  
* **Server:** Uvicorn

**Frontend (frontened/):** *(Note: Correct folder name is typically "frontend")*

* **Framework:** React 18 with Vite  
* **Language:** TypeScript  
* **UI Library:** shadcn/ui  
* **Styling:** Tailwind CSS  
* **State Management/Fetching:** Tanstack Query (@tanstack/react-query)  
* **Routing:** React Router DOM (react-router-dom)

**Containerization:**

* Docker  
* Docker Compose

## **📁 Project Structure**

Smart\_resume\_screener/  
├── backend/            \# FastAPI application  
│   ├── Dockerfile      \# Backend Docker instructions  
│   ├── .dockerignore   \# Files to ignore in backend Docker build  
│   ├── embeddings.py   \# Embedding generation logic  
│   ├── indexer.py      \# FAISS index management  
│   ├── main.py         \# FastAPI endpoints  
│   ├── models.py       \# SQLAlchemy database models  
│   ├── parser.py       \# Resume parsing logic  
│   └── requirements.txt\# Python dependencies  
├── frontened/          \# React frontend application (Vite)  
│   ├── Dockerfile      \# Frontend Docker instructions (multi-stage build)  
│   ├── .dockerignore   \# Files to ignore in frontend Docker build  
│   ├── public/         \# Static assets  
│   ├── src/            \# Frontend source code (components, pages, styles)  
│   ├── index.html      \# Entry point for Vite  
│   ├── package.json    \# Node.js dependencies & scripts  
│   └── vite.config.ts  \# Vite configuration  
├── docker-compose.yml  \# Docker Compose configuration to run both services  
└── README.md           \# This file

## **🚀 Getting Started**

### **Prerequisites**

* [Docker](https://docs.docker.com/get-docker/) installed and running.  
* [Docker Compose](https://docs.docker.com/compose/install/) (usually included with Docker Desktop).  
* Git (for cloning the repository).

### **Running with Docker Compose (Recommended)**

1. **Clone the repository:**  
   git clone \<your-repository-url\>  
   cd Smart\_resume\_screener

2. Build and Run:  
   Navigate to the Smart\_resume\_screener directory (where docker-compose.yml is located) and run:  
   docker-compose up \--build \-d

   * \--build: Forces Docker to rebuild the images based on the Dockerfiles.  
   * \-d: Runs the containers in detached mode (in the background).  
3. **Access the Application:**  
   * The **Frontend** should be accessible in your browser at: http://localhost:8080  
   * The **Backend** API is running at http://localhost:8000, but the frontend is configured to communicate with it directly through Docker's network.  
4. **Stopping the Application:**  
   docker-compose down

   * To remove the persistent data (database, index files), use: docker-compose down \-v

### **Running Locally (Without Docker)**

Refer to the individual README files within the backend/ and frontened/ directories for instructions on setting up and running each part natively.

* [Backend README](http://docs.google.com/backend/README.md)  
* [Frontend README](http://docs.google.com/frontened/README.md)

## **📖 Usage**

1. **Navigate** to http://localhost:8080 in your web browser.  
2. **Upload Resumes:**  
   * Go to the "Upload" tab.  
   * Drag and drop PDF or DOCX resume files onto the drop zone, or click to browse your file system.  
   * Click the "Upload Resumes" button. You'll see confirmation messages upon successful upload.  
3. **Rank Candidates:**  
   * Go to the "Rank" tab.  
   * Enter the "Job Title" for the position you are hiring for.  
   * Paste the full "Job Description" into the text area.  
   * Click the "Rank Candidates" button.  
4. **View Results:**  
   * The system will process the job description and compare it against the indexed resumes.  
   * A ranked list of candidates will appear below the form, ordered by their match score (percentage).  
   * Each candidate card shows key information (name, contact, score) and allows expanding for more details (summary, skills, experience, education).  
5. **Reset Data (Optional):**  
   * On the "Upload" tab, click the "Reset Database" button to clear all uploaded candidate data and the search index. **Use with caution\!**

## **⚙️ Configuration**

### **Frontend**

* VITE\_API\_URL: Set during the Docker build process via the docker-compose.yml file's args. It points the built frontend code to the correct backend URL (http://localhost:8000 when accessed via the host). For local development, you might create a .env file in the frontened directory (see .env.example).

### **Backend**

* DATABASE\_URL: Defines the path to the SQLite database file. Defaults to sqlite:////app/candidates.db inside the container. This path is mapped to a Docker volume for persistence.  
* OPENAI\_API\_KEY (Optional): If set as an environment variable (e.g., in docker-compose.yml), the backend will attempt to use OpenAI for embeddings instead of Sentence Transformers.

## **💾 Data Persistence**

The docker-compose.yml file defines a named volume called backend\_data. This volume is mounted into the /app directory inside the backend container. This ensures that the SQLite database (candidates.db) and the FAISS index files (faiss\_index.idx, faiss\_index.ids) persist even if the backend container is stopped and restarted.

To completely remove this data, run docker-compose down \-v.

## **🤝 Contributing**

Contributions are welcome\! Please feel free to submit a Pull Request.

1. Fork the repository.  
2. Create your feature branch (git checkout \-b feature/AmazingFeature).  
3. Commit your changes (git commit \-m 'Add some AmazingFeature').  
4. Push to the branch (git push origin feature/AmazingFeature).  
5. Open a Pull Request.

## **📄 License**

This project is licensed under the MIT License \- see the [LICENSE](http://docs.google.com/LICENSE) file for details (or add a LICENSE file if you don't have one).