"""
LLM client for Synthaia.
Provides a unified interface to call local (Ollama) or cloud (OpenAI/Anthropic) models.
"""

from typing import Optional
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

try:
    from langchain_openai import ChatOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

from scripts.utils import cfg


class TokenLimitExceeded(Exception):
    """Raised when token limit is exceeded."""
    pass


def call_llm(
    prompt: str,
    system_prompt: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
) -> str:
    """
    Call the configured LLM with a prompt.
    
    Args:
        prompt: The user prompt/question
        system_prompt: Optional system prompt to set context
        model: Override the default model from config
        temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative)
        max_tokens: Maximum tokens in response (uses cfg.MAX_TOKENS_PER_REQUEST if not set)
    
    Returns:
        The LLM's response as a string
    
    Raises:
        TokenLimitExceeded: If max_tokens exceeds configured limit
        ValueError: If cloud is enabled but no API key is set
        Exception: For other LLM errors
    """
    # Determine max tokens
    if max_tokens is None:
        max_tokens = cfg.MAX_TOKENS_PER_REQUEST
    
    # Check token limit
    if max_tokens > cfg.MAX_TOKENS_PER_DAY:
        raise TokenLimitExceeded(
            f"Requested {max_tokens} tokens exceeds daily limit of {cfg.MAX_TOKENS_PER_DAY}"
        )
    
    # Determine provider and model
    provider = cfg.get_active_provider()
    if model is None:
        model = cfg.get_active_model()
    
    # Build messages
    messages = []
    if system_prompt:
        messages.append(SystemMessage(content=system_prompt))
    messages.append(HumanMessage(content=prompt))
    
    try:
        # Route to appropriate provider
        if provider == "ollama":
            llm = ChatOllama(
                model=model,
                temperature=temperature,
            )
            response = llm.invoke(messages)
            return response.content
        
        elif provider == "google":
            if not GOOGLE_AVAILABLE:
                raise ImportError("langchain-google-genai not installed. Run: pip install langchain-google-genai")
            if not cfg.GOOGLE_API_KEY:
                raise ValueError("GOOGLE_API_KEY not set in .env")
            
            llm = ChatGoogleGenerativeAI(
                model=model,
                temperature=temperature,
                max_output_tokens=max_tokens,
                google_api_key=cfg.GOOGLE_API_KEY,
            )
            response = llm.invoke(messages)
            return response.content
        
        elif provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError("langchain-openai not installed. Run: pip install langchain-openai")
            if not cfg.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not set in .env")
            
            llm = ChatOpenAI(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=cfg.OPENAI_API_KEY,
            )
            response = llm.invoke(messages)
            return response.content
        
        elif provider == "anthropic":
            # TODO: Add Anthropic support
            raise NotImplementedError("Anthropic support coming soon")
        
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    except Exception as e:
        raise Exception(f"LLM call failed: {str(e)}")


def test_connection() -> bool:
    """
    Test if the LLM connection is working.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        response = call_llm("Say hello", max_tokens=50)
        print(f"Test response: {response}")
        return len(response) > 0
    except Exception as e:
        import traceback
        print(f"Connection test failed: {e}")
        print("\nFull error:")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Quick test
    print("Testing LLM connection...")
    print(f"Provider: {cfg.get_active_provider()}")
    print(f"Model: {cfg.get_active_model()}")
    
    if test_connection():
        print("✓ Connection successful!")
        
        # Try a real query
        print("\nGenerating song idea...")
        response = call_llm(
            "Generate one creative song title about robots dreaming.",
            system_prompt="You are a creative music producer.",
        )
        print(f"Response: {response}")
    else:
        print("✗ Connection failed")

