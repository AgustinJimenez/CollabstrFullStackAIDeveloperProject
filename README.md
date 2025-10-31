# AI Brief Generator

A professional campaign brief generator powered by AI, built with Django and local AI models (Ollama + phi4-mini) with OpenAI fallback support.

## Live Demo

**Live Application**: https://collabstrfullstackaideveloperproject.onrender.com/

**Local Development**: `http://localhost:8000` (after local setup)

## Project Overview

This application generates professional marketing campaign briefs for brands using AI. It provides:

- **Campaign Brief**: 4-6 sentence strategic overview
- **Content Angles**: 3 specific content strategy directions  
- **Creator Criteria**: 3 selection criteria for influencer partnerships

### Input Parameters
- **Brand Name**: Target brand (1-50 characters)
- **Platform**: Instagram, TikTok, or UGC
- **Goal**: Awareness, Conversions, or Content Assets
- **Tone**: Professional, Friendly, or Playful

## Technical Architecture

### Backend (Django + Python)
- **Framework**: Django 5.1+ with PostgreSQL (production) / SQLite (development)
- **AI Integration**: LangChain framework with multiple providers
  - **Ollama** (phi4-mini) for local development
  - **OpenAI** (LangChain ChatOpenAI) for production
  - **Test provider** (Faker lorem ipsum) for E2E testing
- **API Endpoint**: `/api/generate-brief/` (POST)
- **Code Organization**: 
  - `generator/views.py` - API endpoints and validation
  - `generator/services/llm.py` - LangChain AI integration
- **Safeguards**: Rate limiting, input validation, profanity filtering

### Frontend (HTML/CSS/JavaScript/jQuery)
- **Design**: Clean, modern single-page application
- **Technology**: Vanilla HTML/CSS + jQuery for AJAX
- **Features**: Loading states, error handling, responsive design
- **Results Display**: Structured format with brief, numbered angles, bulleted criteria

### AI Integration
- **Framework**: LangChain for unified AI provider interface
- **Local Development**: Docker + Ollama + phi4-mini:latest  
- **Production**: OpenAI GPT models via LangChain ChatOpenAI
- **Testing**: Faker library generates lorem ipsum for fast E2E tests
- **Model Configuration**: Temperature ≤ 0.5, max tokens limit
- **Output Format**: Structured JSON with validation

## Quick Start

### Prerequisites
- Docker Desktop
- Git

### Containerized Development Setup (Recommended)

1. **Clone Repository**
```bash
git clone <repository-url>
cd CollabstrFullStackAIDeveloperProject
```

2. **Configure Environment**
```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your preferred settings
# For Docker development, default settings work out of the box
# For OpenAI, add your API key to AI_PROVIDER_API_KEY
```

3. **Start Complete Application Stack**
```bash
# Start all services (Ollama + Django)
docker compose up -d

# Pull phi4-mini model (takes 5-10 minutes)
docker exec ollama ollama pull phi4-mini:latest

# Verify model is ready
docker exec ollama ollama list
```

3. **Access Application**
- **Frontend**: http://localhost:8000
- **API**: http://localhost:8000/api/generate-brief/
- **Health Check**: http://localhost:8000/api/health/

### Alternative: Local Python Development

If you prefer local Python development:

1. **Set up Python Environment**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

2. **Configure Environment for Local Development**
```bash
# Copy example environment file
cp .env.example .env

# Edit .env for local development:
# - Set OLLAMA_BASE_URL=http://localhost:11434
# - Set AI_PROVIDER=ollama
# - For OpenAI, set AI_PROVIDER=openai and add your API key
```

3. **Start Only Ollama**
```bash
# Start Ollama container only
docker compose up -d ollama

# Pull model
docker exec ollama ollama pull phi4-mini:latest
```

3. **Configure Environment**
```bash
# Create .env file
echo "AI_PROVIDER=ollama" > .env
echo "OLLAMA_BASE_URL=http://localhost:11434" >> .env
echo "OLLAMA_MODEL=phi4-mini:latest" >> .env
```

4. **Run Django Locally**
```bash
# Run database migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

6. **Access Application**
- **Frontend**: http://localhost:8000
- **API**: http://localhost:8000/api/generate-brief/
- **Health Check**: http://localhost:8000/api/health/

### Production Deployment (Free Hosting)

This project is production-ready with LangChain integration and deployed on Render.com. Users enter their OpenAI API key directly in the web interface - no environment variables needed!

**Live Application**: https://collabstrfullstackaideveloperproject.onrender.com/

**Quick Deploy Options:**

1. **Render.com** (Currently deployed)
   ```bash
   # Just push to GitHub and connect to Render
   # render.yaml is already configured
   ```

2. **Railway.app**
   ```bash
   # Push to GitHub and connect to Railway
   # railway.json is already configured
   ```

3. **Fly.io**
   ```bash
   # Install flyctl and run:
   fly launch
   # fly.toml is already configured
   ```

**Deployment automatically sets:**
- `AI_PROVIDER=openai` (users enter API key in web UI)
- `DEBUG=False` (production mode)
- PostgreSQL database (free tier)
- LangChain OpenAI integration
- Proper security settings

## API Documentation

### Generate Brief Endpoint

**POST** `/api/generate-brief/`

**Request Body:**
```json
{
  "brand_name": "Nike",
  "platform": "Instagram", 
  "goal": "Awareness",
  "tone": "Professional"
}
```

**Response:**
```json
{
  "brief": "Nike's Instagram awareness campaign should focus on authentic athlete stories...",
  "angles": [
    "Behind-the-scenes athlete training content",
    "User-generated content from Nike community", 
    "Product innovation storytelling"
  ],
  "criteria": [
    "Sports and fitness content expertise",
    "High engagement rate with target demographic",
    "Brand alignment with Nike's values"
  ],
  "metrics": {
    "provider": "ollama",
    "model": "phi4-mini:latest", 
    "latency_seconds": 12.3,
    "tokens_used": 145,
    "request_duration": 12.8
  },
  "success": true
}
```

## AI Model Details

### Prompt Design Choices

**System Prompt Strategy:**
- **Concise and Deterministic**: Short prompt defining output format and constraints
- **Structured Output**: Enforces exact JSON schema with required fields
- **Professional Tone**: Focuses on strategic campaign planning vs creator outreach
- **Validation Rules**: Explicit requirements for sentence count and array lengths

**User Prompt Construction:**
- **Compact Format**: Built dynamically from form inputs
- **Context-Aware**: Tailors content to platform, goal, and tone
- **Input Integration**: Seamlessly incorporates all user parameters

### Guardrails Implemented

1. **Input Validation**
   - Brand name: 1-50 characters, alphanumeric + common business chars
   - Platform/Goal/Tone: Must match predefined options exactly
   - Profanity filtering: Basic content filtering implementation
   - Server-side validation: All inputs validated before AI processing

2. **Rate Limiting**
   - **Limit**: 10 requests per minute per IP address
   - **Implementation**: Django cache-based with automatic cleanup
   - **Response**: HTTP 429 with clear error message when exceeded

3. **AI Model Safeguards**
   - **Temperature**: Set to 0.3 (≤ 0.5 requirement)
   - **Max Tokens**: Limited to 500 to control costs
   - **Timeout**: 60-second request timeout
   - **Error Handling**: Graceful fallback with error reporting

4. **Output Validation**
   - **JSON Schema**: Strict validation of response structure
   - **Field Requirements**: Ensures exactly 3 angles and 3 criteria
   - **Content Validation**: Checks brief length and quality
   - **Parse Error Handling**: Robust JSON parsing with fallbacks

### Token and Latency Measurement

**Metrics Captured:**
- **Request Duration**: Total API call time (start to finish)
- **Model Latency**: AI processing time specifically  
- **Token Usage**: Input + output token counts
- **Provider Info**: Model name and provider identification
- **Cost Estimation**: Per-request cost calculation (free for Ollama)

**Implementation:**
- **Timing**: Python `time.time()` measurements around AI calls
- **Token Counting**: Native Ollama API response metrics
- **Visibility**: All metrics returned in API response and displayed in UI
- **Logging**: Performance data available for monitoring

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `AI_PROVIDER` | AI provider: `ollama`, `openai`, or `test` | `ollama` | No |
| `AI_PROVIDER_API_KEY` | OpenAI API key | None | No (entered via web UI) |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` | No |
| `OLLAMA_MODEL` | Ollama model name | `phi4-mini:latest` | No |
| `DEBUG` | Django debug mode | `True` | No |
| `SECRET_KEY` | Django secret key | Auto-generated | No |
| `DATABASE_URL` | PostgreSQL connection string | None | No (SQLite fallback) |

### Docker Development Commands

```bash
# Start all services in background
docker compose up -d

# View logs (real-time)
docker compose logs -f django
docker compose logs -f ollama

# View logs (static)
docker compose logs django
docker compose logs ollama

# Restart services (after code/config changes)
docker compose restart django
docker compose restart ollama

# Run Django management commands in container
docker compose exec django python manage.py migrate
docker compose exec django python manage.py test
docker compose exec django python manage.py shell
docker compose exec django python manage.py createsuperuser

# Run tests in containerized environment
docker compose exec django python manage.py test generator.tests --verbosity=2

# Access Django shell for debugging
docker compose exec django python manage.py shell

# Check Django configuration
docker compose exec django python manage.py check

# Stop all services
docker compose down

# Stop and remove volumes (complete reset)
docker compose down -v

# Rebuild Django image (after requirements.txt changes)
docker compose build django
docker compose up -d

# Pull new Ollama models
docker compose exec ollama ollama pull llama3.2:3b
docker compose exec ollama ollama list

# Monitor resource usage
docker compose exec django top
docker stats
```

### Docker Configuration

**docker-compose.yml** provides:
- Django service with volume mounting for live code reloading
- Ollama service with persistent volume storage
- Network configuration for service communication  
- Automatic migrations on startup
- Development-friendly environment variables

## Performance Metrics

### Local Development (Ollama + phi4-mini)
- **Model Size**: ~2.5GB
- **Average Latency**: 10-15 seconds  
- **Token Usage**: 100-200 tokens per request
- **Cost**: Free (local processing)
- **Reliability**: High consistency with structured prompts

### Production (OpenAI)
- **Average Latency**: 2-5 seconds
- **Token Usage**: Similar range
- **Cost**: ~$0.01-0.03 per request (estimated)
- **Reliability**: Very high consistency

## Testing

### Unit Tests
```bash
# Local development (if Python environment setup)
source venv/bin/activate
python manage.py test generator.tests --verbosity=2

# Docker development (recommended)
docker compose exec django python manage.py test generator.tests --verbosity=2

# Tests cover:
# - Prompt building functions
# - JSON response parsing
# - Input validation logic
# - Error handling
```

### End-to-End Tests

**Option 1: Local Development (Recommended)**
```bash
# Local development (Django server must be running)
pip install pytest-playwright
playwright install
python -m pytest tests/test_e2e.py --tb=short

# Generate HTML report
python -m pytest tests/test_e2e.py --html=test-report.html --self-contained-html

# Generate JUnit XML report  
python -m pytest tests/test_e2e.py --junitxml=test-results.xml

# Generate multiple report formats
python -m pytest tests/test_e2e.py --html=test-report.html --junitxml=test-results.xml --tb=short
```

**Option 2: Docker with Playwright Support**
```bash
# Use Playwright-enabled Docker setup
docker compose -f docker-compose.yml -f docker-compose.playwright.yml build
docker compose -f docker-compose.yml -f docker-compose.playwright.yml up -d

# Run E2E tests in container
docker compose -f docker-compose.yml -f docker-compose.playwright.yml exec django python -m pytest tests/test_e2e.py --tb=short --browser chromium

# Run specific test
docker compose -f docker-compose.yml -f docker-compose.playwright.yml exec django python -m pytest tests/test_e2e.py::TestAIBriefGenerator::test_page_loads_correctly --browser chromium -v

# Generate HTML report
docker compose -f docker-compose.yml -f docker-compose.playwright.yml exec django python -m pytest tests/test_e2e.py --browser chromium --html=test-report.html --self-contained-html

# Generate JUnit XML report
docker compose -f docker-compose.yml -f docker-compose.playwright.yml exec django python -m pytest tests/test_e2e.py --browser chromium --junitxml=test-results.xml

# Generate multiple report formats
docker compose -f docker-compose.yml -f docker-compose.playwright.yml exec django python -m pytest tests/test_e2e.py --browser chromium --html=test-report.html --junitxml=test-results.xml --tb=short
```

**Option 3: Test Script with Provider Selection (Recommended)**
```bash
# Fast testing with test provider (recommended for development)
./test-e2e.sh test

# Realistic testing with Ollama
./test-e2e.sh ollama

# Production-like testing with OpenAI
./test-e2e.sh openai

# Run specific test with fast provider
./test-e2e.sh test test_health_endpoint
```

**AI Provider Configuration**
```bash
# E2E tests automatically detect pytest and use test provider
# No manual configuration needed - tests use Faker lorem ipsum

# Manual provider testing:
# AI_PROVIDER=test    # Ultra-fast lorem ipsum (auto-detected in pytest)
# AI_PROVIDER=ollama  # Local realistic responses (6s)  
# AI_PROVIDER=openai # Production responses (requires API key)
```

**E2E tests cover complete user journey:**
- Form validation and submission
- Loading states and error handling  
- Results display and formatting
- Accessibility and responsive design

### Manual Testing
```bash
# Test health endpoint
curl http://localhost:8000/api/health/

# Test brief generation
curl -X POST http://localhost:8000/api/generate-brief/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "brand_name": "TestBrand",
    "platform": "Instagram", 
    "goal": "Awareness",
    "tone": "Professional"
  }'
```

### Test Coverage
- **Unit Tests**: Core functionality, prompt building, JSON parsing
- **E2E Tests**: Complete user workflow, form validation, API integration
- **Manual Tests**: Health checks, rate limiting, edge cases

## Deployment Options

### Recommended Free Hosting Platforms

1. **Railway.app** (Recommended)
   - Easy Django deployment
   - PostgreSQL included
   - GitHub integration
   - Free tier available

2. **Render.com**
   - Supports Docker deployment
   - Auto-deploy from GitHub
   - Free tier with limitations

3. **Fly.io**
   - Excellent for containerized apps
   - Global edge deployment
   - Free tier available

4. **PythonAnywhere**
   - Simple Django hosting
   - Good for small applications
   - Free tier available

### Deployment Steps (Railway Example)
1. Push code to GitHub repository
2. Connect Railway to GitHub repo
3. Set environment variables in Railway dashboard
4. Deploy automatically on push

## Project Structure

```
CollabstrFullStackAIDeveloperProject/
├── aibrief/                 # Django project
│   ├── settings.py         # Configuration
│   └── urls.py             # URL routing
├── generator/              # Main Django app
│   ├── services/
│   │   └── llm.py          # AI integration
│   ├── templates/
│   │   └── generator/
│   │       └── index.html  # Frontend
│   ├── views.py            # API endpoints
│   └── urls.py             # App URL routing
├── docker-compose.yml      # Docker setup
├── requirements.txt        # Python dependencies
├── .env                    # Environment config
└── README.md              # This file
```

## Development Notes

### Code Organization Principles
- **Small, Readable Functions**: Each function has single responsibility
- **Clear Separation**: Views handle HTTP, services handle AI logic  
- **Error Handling**: Comprehensive error management throughout
- **Documentation**: Inline comments explaining requirements compliance

### Requirements Compliance
- All backend requirements implemented
- All frontend requirements met
- Proper code organization (views.py + services/llm.py)
- Deterministic output with JSON schema
- Complete safeguards and metrics
- Simple, easy-to-follow jQuery AJAX

### Future Enhancements
- Additional AI model support (Llama, Mistral, etc.)
- Enhanced profanity filtering
- User authentication and request history
- A/B testing for different prompt strategies
- Enhanced analytics and monitoring

## Contributing

This project was built as a technical demonstration. For production use:

1. Enhance security measures
2. Add comprehensive testing suite  
3. Implement proper logging and monitoring
4. Add user authentication
5. Optimize for scale

## License

Built for technical evaluation purposes. Please follow appropriate licensing for production use.

---

**Project Goal**: Demonstrate full-stack AI integration with local models, production-ready code organization, and modern web development practices.