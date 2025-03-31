# Summit SEO Web Application

This directory contains the web application components for the Summit SEO project, including both the user interface (UI) and REST API.

## Directory Structure

```
summit_seo/web/
├── api/              # Backend REST API built with FastAPI
│   ├── main.py       # Main FastAPI application entry point
│   ├── models/       # Pydantic data models
│   ├── routers/      # API route handlers organized by resource
│   └── tests/        # API tests
├── ui/               # Frontend user interface built with React
│   ├── components/   # Reusable UI components
│   ├── pages/        # Page components for different routes
│   ├── styles/       # CSS styles and utilities
│   └── responsive-design-guidelines.md  # Guidelines for responsive design
└── README.md         # This file
```

## Components

### REST API (Backend)

The backend API is built with FastAPI, providing a high-performance, easy-to-use, and standards-compliant REST API. Key features include:

- **Authentication**: JWT-based authentication with token refresh and revocation
- **Resource Management**: Endpoints for users, projects, and analyses
- **Analysis Operations**: Start, monitor, and retrieve results from SEO analyses
- **Standardized Responses**: Consistent response format with proper error handling
- **OpenAPI Documentation**: Automatically generated API documentation

### User Interface (Frontend)

The frontend UI is built with modern web technologies and follows a component-based architecture. Features include:

- **Responsive Design**: Mobile-first approach with responsive components
- **Accessibility**: WCAG 2.1 Level AA compliance for all components
- **Component Library**: Reusable UI components with consistent styling
- **Design System**: Standardized colors, typography, and spacing

## Communication Between UI and API

The UI communicates with the API through standard HTTP requests. Authentication is handled via JWT tokens that are:

1. Obtained through the login process
2. Stored securely in the client
3. Sent with each request in the Authorization header
4. Refreshed automatically when needed
5. Revoked on logout

## Development

### API Development

```bash
# Navigate to the API directory
cd summit_seo/web/api

# Install dependencies
pip install -r requirements.txt

# Run the API server with hot reloading
uvicorn main:app --reload

# Access API documentation
# Open http://localhost:8000/docs in your browser
```

### UI Development

```bash
# Navigate to the UI directory
cd summit_seo/web/ui

# Install dependencies
npm install

# Run the development server
npm run dev

# Build for production
npm run build
```

## Integration

In production, both the UI and API components are deployed together:

1. The UI is built as a static site
2. The API server serves the UI files
3. API requests are sent to the same domain, eliminating CORS issues
4. Both components share the same authentication system

## Roadmap

- Database integration with SQLAlchemy and PostgreSQL
- Cloud deployment with containerization
- Enhanced security features
- Multi-user collaboration features 