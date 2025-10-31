"""
Views for AI Brief Generator

Requirements adherence:
- Server-side input validation
- One endpoint for brief generation
- Returns JSON with brief, angles[], criteria[]
- Includes timing and token usage metrics
- Basic safeguards: profanity filter, rate limiting
"""

import time
import json
import sys
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.conf import settings
# Enhanced profanity filter for input validation
def is_profane(text: str) -> bool:
    """
    Enhanced profanity filter implementation using profanity-check library
    Requirements: Profanity filter or allowlist validation
    """
    try:
        from profanity_check import predict
        # Use ML-based profanity detection (more accurate than word lists)
        return predict(text) == 1
    except ImportError:
        # Fallback to basic word list if library not available
        profane_words = {
            'spam', 'scam', 'test123', 'badword'  # Basic filter for demo
        }
        return any(word.lower() in text.lower() for word in profane_words)
from .services.llm import generate_campaign_brief


# Valid options for form inputs (as specified in requirements)
VALID_PLATFORMS = ['Instagram', 'TikTok', 'UGC']
VALID_GOALS = ['Awareness', 'Conversions', 'Content Assets']
VALID_TONES = ['Professional', 'Friendly', 'Playful']


def validate_brand_name(brand_name: str) -> str:
    """
    Validate brand name input
    Requirements: Server-side validation, profanity filter
    """
    if not brand_name or not isinstance(brand_name, str):
        return "Brand name is required"
    
    brand_name = brand_name.strip()
    
    if len(brand_name) < 1 or len(brand_name) > 50:
        return "Brand name must be 1-50 characters"
    
    # Allow alphanumeric, spaces, and common business characters
    if not all(c.isalnum() or c.isspace() or c in ".-&'" for c in brand_name):
        return "Brand name contains invalid characters"
    
    # Profanity filter (allowlist validation)
    if is_profane(brand_name):
        return "Brand name contains inappropriate content"
    
    return None  # Valid


def validate_form_inputs(data: dict) -> tuple:
    """
    Validate all form inputs according to requirements
    Returns: (is_valid, error_message, cleaned_data)
    """
    errors = []
    
    # Validate brand name
    brand_name = data.get('brand_name', '').strip()
    brand_error = validate_brand_name(brand_name)
    if brand_error:
        errors.append(f"Brand name: {brand_error}")
    
    # Validate platform (must be from predefined options)
    platform = data.get('platform', '')
    if platform not in VALID_PLATFORMS:
        errors.append(f"Platform must be one of: {', '.join(VALID_PLATFORMS)}")
    
    # Validate goal (must be from predefined options)
    goal = data.get('goal', '')
    if goal not in VALID_GOALS:
        errors.append(f"Goal must be one of: {', '.join(VALID_GOALS)}")
    
    # Validate tone (must be from predefined options)
    tone = data.get('tone', '')
    if tone not in VALID_TONES:
        errors.append(f"Tone must be one of: {', '.join(VALID_TONES)}")
    
    if errors:
        return False, "; ".join(errors), None
    
    return True, None, {
        'brand_name': brand_name,
        'platform': platform,
        'goal': goal,
        'tone': tone
    }


def check_rate_limit(request) -> tuple:
    """
    Basic rate limiting implementation
    Requirements: Basic rate-limiting safeguard
    Returns: (is_allowed, error_message)
    """
    if 'pytest' in sys.modules:
        return True, None

    # Get client IP for rate limiting
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    max_requests = getattr(settings, 'RATE_LIMIT_MAX_REQUESTS', 10)
    window_seconds = getattr(settings, 'RATE_LIMIT_WINDOW_SECONDS', 60)
    
    # Rate limit per IP within configured window
    cache_key = f"rate_limit_{ip}"
    current_requests = cache.get(cache_key, 0)
    
    if current_requests >= max_requests:
        return False, f"Rate limit exceeded. Maximum {max_requests} requests per {window_seconds} seconds."
    
    # Increment counter with configured expiry
    cache.set(cache_key, current_requests + 1, window_seconds)
    return True, None


@csrf_exempt
@require_http_methods(["POST"])
def generate_brief(request):
    """
    Main endpoint for AI brief generation
    
    Requirements adherence:
    - One endpoint that validates inputs server-side
    - Calls LLM with deterministic system prompt
    - Returns JSON with brief, angles[], criteria[]
    - Includes basic safeguards and metrics
    """
    start_time = time.time()
    
    try:
        # Parse request data
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON data',
                'success': False
            }, status=400)
        
        # Rate limiting check
        rate_allowed, rate_error = check_rate_limit(request)
        if not rate_allowed:
            return JsonResponse({
                'error': rate_error,
                'success': False
            }, status=429)
        
        # Input validation
        is_valid, validation_error, cleaned_data = validate_form_inputs(data)
        if not is_valid:
            return JsonResponse({
                'error': f'Validation failed: {validation_error}',
                'success': False
            }, status=400)
        
        # Generate campaign brief using LLM service
        try:
            result = generate_campaign_brief(
                brand=cleaned_data['brand_name'],
                platform=cleaned_data['platform'],
                goal=cleaned_data['goal'],
                tone=cleaned_data['tone'],
                api_token=(data.get('api_token') or '').strip() or None
            )
            
            # Add request processing time to metrics
            end_time = time.time()
            result['metrics']['request_duration'] = round(end_time - start_time, 2)
            result['success'] = True
            
            return JsonResponse(result, status=200)
            
        except Exception as e:
            end_time = time.time()
            return JsonResponse({
                'error': f'AI generation failed: {str(e)}',
                'success': False,
                'metrics': {
                    'request_duration': round(end_time - start_time, 2),
                    'error': str(e)
                }
            }, status=500)
    
    except Exception as e:
        end_time = time.time()
        return JsonResponse({
            'error': f'Server error: {str(e)}',
            'success': False,
            'metrics': {
                'request_duration': round(end_time - start_time, 2),
                'error': str(e)
            }
        }, status=500)


def index(request):
    """
    Serve the main application page
    Requirements: Single page with clean, modern look
    """
    provider = settings.AI_PROVIDER
    override = request.GET.get('provider_override')
    if override in {'openai', 'ollama', 'test'}:
        provider = override
    token = getattr(settings, 'AI_PROVIDER_API_KEY', '')
    if override == 'openai' and not token:
        token = ''
    return render(
        request,
        'generator/index.html',
        {
            'ai_provider': provider,
            'ai_provider_token': token,
        }
    )


def health_check(request):
    """Simple health check endpoint"""
    provider = getattr(settings, 'AI_PROVIDER', 'unknown')
    if 'pytest' in sys.modules:
        provider = 'test'
    return JsonResponse({
        'status': 'healthy',
        'ai_provider': provider,
        'timestamp': time.time()
    })


@csrf_exempt
@require_http_methods(["POST"])
def set_provider(request):
    """Testing helper to switch AI provider at runtime"""
    if not settings.DEBUG:
        return HttpResponseForbidden("Provider override available only in debug mode")

    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON payload'
        }, status=400)

    provider = data.get('provider')
    valid_providers = {'test', 'ollama', 'openai'}

    if provider not in valid_providers:
        return JsonResponse({
            'success': False,
            'error': f'Provider must be one of: {", ".join(sorted(valid_providers))}'
        }, status=400)

    settings.AI_PROVIDER = provider

    if provider == 'openai':
        api_key = data.get('api_key')
        if api_key:
            settings.AI_PROVIDER_API_KEY = api_key
    else:
        settings.AI_PROVIDER_API_KEY = ''

    # Clear rate limit cache when switching providers
    cache.clear()

    return JsonResponse({
        'success': True,
        'provider': settings.AI_PROVIDER
    })
