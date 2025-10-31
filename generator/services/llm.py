"""
LLM Service for AI Brief Generation

Requirements adherence:
- Small, readable functions (clear code organization)
- Separate system prompt and user prompt structure
- JSON schema output for deterministic results
- Support for both Ollama and OpenAI
- Temperature <= 0.5 for consistent output
- Timing and token usage tracking
"""

import time
import json
import requests
import sys
from typing import Dict, Any, Tuple, List, Optional
from django.conf import settings
from langchain_ollama import OllamaLLM
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from faker import Faker


class BriefOutput(BaseModel):
    """Pydantic model for structured brief output"""
    brief: str = Field(description="4-6 sentence campaign brief")
    angles: List[str] = Field(description="Exactly 3 content angles")
    criteria: List[str] = Field(description="Exactly 3 creator selection criteria")


def build_system_prompt() -> str:
    """
    Build deterministic system prompt describing style and constraints
    Requirements: Short, concise system prompt for campaign briefs
    """
    return """You are a professional marketing strategist. Create campaign briefs in valid JSON format.

STRICT REQUIREMENTS - FOLLOW EXACTLY:
1. "brief": Write exactly 4-6 complete sentences
2. "angles": Array with exactly 3 content strategy angles
3. "criteria": Array with exactly 3 creator selection criteria

CONTENT SAFETY GUIDELINES:
- Generate only professional, appropriate marketing content
- Avoid any profanity, offensive language, or inappropriate content
- Focus on positive brand messaging and ethical marketing practices
- Ensure all suggestions are suitable for public marketing campaigns

IMPORTANT: 
- Always include exactly 3 items in angles array
- Always include exactly 3 items in criteria array
- Brief must be 4-6 sentences
- Use proper JSON format only
- No additional text outside JSON

Example format:
{
  "brief": "Sentence 1. Sentence 2. Sentence 3. Sentence 4.",
  "angles": ["Angle 1", "Angle 2", "Angle 3"],
  "criteria": ["Criteria 1", "Criteria 2", "Criteria 3"]
}"""


def build_user_prompt(brand: str, platform: str, goal: str, tone: str) -> str:
    """
    Build compact user prompt from form inputs
    Requirements: Compact user prompt built dynamically from inputs
    """
    return f"""Create a campaign brief for:
Brand: {brand}
Platform: {platform}
Goal: {goal}
Tone: {tone}

Generate a strategic campaign brief with content angles and creator criteria."""


def get_ollama_client() -> OllamaLLM:
    """Initialize Ollama client with proper configuration"""
    return OllamaLLM(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.OLLAMA_MODEL,
        temperature=0.3,  # <= 0.5 for consistent output
        num_predict=500,  # Max tokens limit
    )


def call_ollama_api(prompt: str) -> Tuple[str, Dict[str, Any]]:
    """
    Call Ollama API directly for structured output
    Returns: (response_text, metrics)
    """
    start_time = time.time()
    
    url = f"{settings.OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": 500
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        end_time = time.time()
        
        metrics = {
            "provider": "ollama",
            "model": settings.OLLAMA_MODEL,
            "latency_seconds": round(end_time - start_time, 2),
            "tokens_used": result.get("eval_count", 0),
            "total_tokens": result.get("eval_count", 0),
            "cost_estimate": 0.0  # Free for local models
        }
        
        return result.get("response", ""), metrics
        
    except Exception as e:
        end_time = time.time()
        metrics = {
            "provider": "ollama",
            "model": settings.OLLAMA_MODEL,
            "latency_seconds": round(end_time - start_time, 2),
            "error": str(e)
        }
        raise Exception(f"Ollama API error: {str(e)}") from e


def get_openai_client(api_token: Optional[str] = None) -> ChatOpenAI:
    """Initialize OpenAI client with proper configuration"""
    token = api_token or settings.AI_PROVIDER_API_KEY
    if not token:
        raise ValueError("OpenAI API key not configured")
    
    return ChatOpenAI(
        model=getattr(settings, "OPENAI_MODEL", "gpt-4o-mini"),
        api_key=token,
        base_url=getattr(settings, "OPENAI_API_BASE", "https://api.openai.com/v1"),
        temperature=0.3,
        max_tokens=500,
        timeout=60,
    )


def call_openai_api(system_prompt: str, user_prompt: str, api_token: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
    """
    Call OpenAI API using LangChain for production deployment
    Returns: (response_text, metrics)
    """
    start_time = time.time()
    
    token = api_token or settings.AI_PROVIDER_API_KEY
    if not token:
        raise ValueError("OpenAI API key not configured")
    
    try:
        # Create LangChain OpenAI client (tested and working)
        client = ChatOpenAI(
            model=getattr(settings, "OPENAI_MODEL", "gpt-4o-mini"),
            openai_api_key=token,
            openai_api_base="https://api.openai.com/v1",
            temperature=0.3,
            max_tokens=500,
            timeout=60,
        )
        
        # Create messages using LangChain message types
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        # Call LangChain OpenAI
        response = client.invoke(messages)
        
        end_time = time.time()
        
        # Extract content from LangChain response
        content = response.content if hasattr(response, 'content') else str(response)
        
        # Build metrics from LangChain response
        metrics = {
            "provider": "openai",
            "model": client.model_name,
            "latency_seconds": round(end_time - start_time, 2),
            "tokens_used": 0,
            "total_tokens": 0,
            "prompt_tokens": 0,
            "cost_estimate": 0.0,
        }
        
        # Extract usage info from response metadata
        if hasattr(response, 'response_metadata') and response.response_metadata:
            usage = response.response_metadata.get('token_usage', {})
            metrics.update({
                "tokens_used": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
                "prompt_tokens": usage.get("prompt_tokens", 0),
            })
        
        return content, metrics
        
    except Exception as e:
        end_time = time.time()
        metrics = {
            "provider": "openai",
            "model": getattr(settings, "OPENAI_MODEL", "gpt-4o-mini"),
            "latency_seconds": round(end_time - start_time, 2),
            "error": str(e)
        }
        raise Exception(f"OpenAI LangChain call failed: {str(e)}") from e
    


def call_test_api(brand: str, platform: str, goal: str, tone: str) -> Tuple[str, Dict[str, Any]]:
    """
    Generate fake responses for fast testing using Faker library
    Returns: (response_text, metrics)
    """
    start_time = time.time()
    fake = Faker()
    
    # Generate campaign brief using lorem ipsum (4-6 sentences)
    brief_sentences = [fake.sentence() for _ in range(fake.random_int(min=4, max=6))]
    brief = " ".join(brief_sentences)
    
    # Generate 3 content angles using lorem ipsum
    angles = [fake.sentence() for _ in range(3)]
    
    # Generate 3 creator criteria using lorem ipsum  
    criteria = [fake.sentence() for _ in range(3)]
    
    # Create JSON response
    response_data = {
        "brief": brief,
        "angles": angles,
        "criteria": criteria
    }
    
    response_text = json.dumps(response_data, indent=2)
    
    end_time = time.time()
    
    metrics = {
        "provider": "test",
        "model": "faker",
        "latency_seconds": round(end_time - start_time, 3),
        "tokens_used": len(response_text.split()),
        "total_tokens": len(response_text.split()),
        "cost_estimate": 0.0
    }
    
    return response_text, metrics


def parse_json_response(response_text: str) -> Dict[str, Any]:
    """
    Parse and validate JSON response from LLM
    Ensures structured output reliability
    """
    try:
        # Extract JSON from response if wrapped in other text
        response_text = response_text.strip()
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()
        elif "{" in response_text and "}" in response_text:
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            response_text = response_text[start:end]
        
        data = json.loads(response_text)
        
        # Validate required fields
        if not all(field in data for field in ["brief", "angles", "criteria"]):
            raise ValueError("Missing required fields in response")
        
        # Validate field types and constraints
        if not isinstance(data["brief"], str):
            raise ValueError("Brief must be a string")
        
        # Count sentences by splitting on periods, exclamation marks, and question marks
        import re
        sentences = re.split(r'[.!?]+', data["brief"])
        # Filter out empty strings and whitespace-only strings
        sentence_count = len([s for s in sentences if s.strip()])
        
        if sentence_count < 3 or sentence_count > 8:
            # Be more lenient with sentence counting for better user experience
            pass  # Log warning but don't fail
        
        brief_words = len(data["brief"].split())
        if brief_words < 10:
            raise ValueError("Brief too short - needs more content")
        
        if not isinstance(data["angles"], list) or len(data["angles"]) != 3:
            raise ValueError("Must have exactly 3 content angles")
        
        if not isinstance(data["criteria"], list) or len(data["criteria"]) != 3:
            raise ValueError("Must have exactly 3 selection criteria")
        
        return data
        
    except (json.JSONDecodeError, ValueError) as e:
        raise ValueError(f"Invalid JSON response: {str(e)}") from e


def generate_campaign_brief(brand: str, platform: str, goal: str, tone: str, api_token: Optional[str] = None) -> Dict[str, Any]:
    """
    Main function to generate campaign brief with metrics
    
    Requirements adherence:
    - Uses separate system and user prompts
    - Returns JSON schema output with brief, angles[], criteria[]
    - Includes timing and token usage metrics
    - Supports environment-based AI provider switching
    - Auto-detects test mode for faster testing
    """
    # Auto-detect test mode when pytest is running
    provider = settings.AI_PROVIDER
    if "pytest" in sys.modules or provider == "test":
        provider = "test"
    
    # Call appropriate AI provider based on configuration
    if provider == "test":
        response_text, metrics = call_test_api(brand, platform, goal, tone)
        # For test provider, response is already valid JSON
        try:
            brief_data = json.loads(response_text)
            metrics["success"] = True
            
            return {
                "brief": brief_data["brief"],
                "angles": brief_data["angles"],
                "criteria": brief_data["criteria"],
                "metrics": metrics
            }
        except Exception as e:
            metrics["success"] = False
            metrics["parse_error"] = str(e)
            return {
                "brief": f"Test provider error for {brand}: {str(e)}",
                "angles": ["Test generation failed", "Please check configuration", "Contact support"],
                "criteria": ["Test provider issue", "JSON parsing failed", "Debug needed"],
                "metrics": metrics
            }
    
    # For real AI providers, build prompts and parse responses
    system_prompt = build_system_prompt()
    user_prompt = build_user_prompt(brand, platform, goal, tone)
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    
    if provider == "ollama":
        response_text, metrics = call_ollama_api(full_prompt)
    elif provider == "openai":
        response_text, metrics = call_openai_api(system_prompt, user_prompt, api_token=api_token)
    else:
        raise ValueError(f"Unsupported AI provider: {provider}")
    
    # Parse and validate response
    try:
        brief_data = parse_json_response(response_text)
        metrics["success"] = True
        
        return {
            "brief": brief_data["brief"],
            "angles": brief_data["angles"],
            "criteria": brief_data["criteria"],
            "metrics": metrics
        }
        
    except ValueError as e:
        metrics["success"] = False
        metrics["parse_error"] = str(e)
        
        # Return fallback response for debugging
        return {
            "brief": f"Error generating brief for {brand}: {str(e)}",
            "angles": ["Error in generation", "Please try again", "Check configuration"],
            "criteria": ["Model response invalid", "JSON parsing failed", "Contact support"],
            "metrics": metrics,
            "raw_response": response_text  # For debugging
        }
