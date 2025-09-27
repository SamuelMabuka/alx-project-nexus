# Nexus Movie Recommendation API

**A production-ready movie recommendation system with JWT authentication, personalized features, and comprehensive API documentation.**

**Live API:** https://movie-api-etrv.onrender.com/  
**Documentation:** https://movie-api-etrv.onrender.com/api/docs/

---

## Features

• **JWT Authentication** - Secure user registration, login, and profile management  
• **Movie Discovery** - Search, popular, trending movies with TMDb integration  
• **User Ratings** - Rate movies (1-5 stars) with reviews  
• **Favorites & Watchlist** - Personal movie collections with priorities  
• **Recommendations** - Personalized suggestions based on user preferences  
• **User Statistics** - Track viewing habits and preferences  
• **Interactive API Docs** - Complete Swagger UI documentation  

---

## Quick Start

### Local Development
```bash
# Clone and setup
git clone https://github.com/SamuelMabuka/nexus-movie-api.git
cd nexus-movie-api
python -m venv nex_env
source nex_env/bin/activate  # Windows: nex_env\Scripts\activate
pip install -r requirements.txt

# Configure database
python manage.py migrate
python manage.py createsuperuser

# Run server
python manage.py runserver
```

Visit: http://127.0.0.1:8000/api/docs/

### Environment Configuration
```env
SECRET_KEY=your-unique-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
TMDB_API_KEY=get-from-themoviedb-org
ALLOWED_HOSTS=localhost,127.0.0.1
```

**Security Note:** Never commit real credentials to version control. Use environment variables for all sensitive information.

---

## API Endpoints

| Category | Endpoint | Description |
|----------|----------|-------------|
| **Authentication** | POST /api/auth/register/ | User registration |
| | POST /api/auth/login/ | Login with JWT tokens |
| | GET/PUT /api/auth/profile/ | User profile management |
| **Movies** | GET /api/movies/popular/ | Popular movies |
| | GET /api/movies/search/ | Search movies |
| | GET /api/movies/{id}/ | Movie details |
| **User Features** | POST /api/movies/{id}/rate/ | Rate a movie |
| | GET /api/movies/favorites/ | User favorites |
| | GET /api/movies/recommendations/ | Personalized suggestions |

**Complete documentation:** https://movie-api-etrv.onrender.com/api/docs/

---

## Usage Examples

### User Registration & Authentication
```bash
# Register new user
curl -X POST https://movie-api-etrv.onrender.com/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "password2": "securepassword123",
    "first_name": "John",
    "last_name": "Doe"
  }'

# User login
curl -X POST https://movie-api-etrv.onrender.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### Movie Operations
```bash
# Search movies
curl "https://movie-api-etrv.onrender.com/api/movies/search/?query=avengers"

# Rate a movie (authentication required)
curl -X POST https://movie-api-etrv.onrender.com/api/movies/550/rate/ \
  -H "Authorization: Bearer YOUR_JWT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"rating": 5, "review": "Excellent movie!"}'
```

---

## Technology Stack

**Backend Framework:**
- Django 5.0+ - High-level Python web framework
- Django REST Framework - Powerful API toolkit
- djangorestframework-simplejwt - JWT authentication

**Database & Storage:**
- PostgreSQL - Production database
- SQLite - Development database
- Redis - Caching (optional)

**API & Documentation:**
- OpenAPI 3.0 specification
- Swagger UI - Interactive documentation
- drf-spectacular - Schema generation

**Deployment & Security:**
- Render - Cloud deployment platform
- Gunicorn - WSGI HTTP Server
- WhiteNoise - Static file serving
- CORS headers for frontend integration

---

## Deployment

### Production Deployment on Render

1. **Repository Setup**
   - Connect GitHub repository to Render
   - Select main branch for deployment

2. **Service Configuration**
   - **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start Command:** `gunicorn movie_backend.wsgi:application --bind 0.0.0.0:$PORT`

3. **Environment Variables** (Production)
   ```
   DEBUG=False
   SECRET_KEY=[generate-strong-random-key]
   DATABASE_URL=[provided-by-render-postgresql]
   ALLOWED_HOSTS=your-app-name.onrender.com
   TMDB_API_KEY=[your-api-key]
   ```

4. **Database Setup**
   - Create PostgreSQL database on Render
   - Connect database to web service
   - Migrations run automatically

### Security Considerations
- All sensitive data stored in environment variables
- HTTPS enforced in production (automatic with Render)
- CORS properly configured for frontend access
- JWT tokens with secure expiration times

---

## Project Structure

```
nexus-movie-api/
├── accounts/              # User authentication app
│   ├── models.py         # User model
│   ├── serializers.py    # API serializers
│   ├── views.py          # Authentication views
│   └── urls.py           # Auth URL patterns
├── movies/               # Movie management app
│   ├── models.py         # Movie, Rating, Favorite models
│   ├── serializers.py    # Movie API serializers
│   ├── views.py          # Movie views
│   └── urls.py           # Movie URL patterns
├── movie_backend/        # Django project configuration
│   ├── settings.py       # Django settings
│   ├── urls.py           # Main URL configuration
│   └── wsgi.py           # WSGI application
├── requirements.txt      # Python dependencies
├── schema.yml           # OpenAPI 3.0 specification
└── README.md            # Project documentation
```

---

## Testing

### Run Tests
```bash
# Run all tests
python manage.py test

# Test specific app
python manage.py test accounts
python manage.py test movies

# Test with coverage
pip install coverage
coverage run manage.py test
coverage report
```

### API Health Check
```bash
# Check API status
curl https://movie-api-etrv.onrender.com/health/

# Expected response:
# {"status": "healthy", "service": "Nexus Movie API", "version": "1.0.0"}
```

---

## Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork the Repository**
   - Create your own fork of the project

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes**
   - Follow PEP 8 Python style guidelines
   - Add tests for new functionality
   - Update documentation as needed

4. **Commit and Push**
   ```bash
   git commit -m "Add: brief description of changes"
   git push origin feature/your-feature-name
   ```

5. **Submit Pull Request**
   - Provide clear description of changes
   - Reference any related issues

### Development Guidelines
- Write comprehensive tests for new features
- Update API documentation for new endpoints
- Follow existing code patterns and conventions
- Include detailed commit messages

---

## License

This project is licensed under the MIT License. See LICENSE file for details.

---

## Support & Contact

**Developer:** Nexus Development Team  
**GitHub:** [Project Repository]  
**API Documentation:** https://movie-api-etrv.onrender.com/api/docs/  
**Live Demo:** https://movie-api-etrv.onrender.com/

For questions, issues, or contributions, please use the GitHub repository issue tracker.

---

## Acknowledgments

- **The Movie Database (TMDb)** - Movie data provider
- **Django & Django REST Framework** - Backend framework
- **Render** - Deployment platform
- **Swagger UI** - API documentation interface
