class NanoGPTError(Exception):
    """Base exception for all NanoGPT Chat errors."""
    pass

class APIError(NanoGPTError):
    """Raised when an API request fails."""
    pass

class DatabaseError(NanoGPTError):
    """Raised when a database operation fails."""
    pass

class ConfigurationError(NanoGPTError):
    """Raised when there is a configuration issue (e.g., missing API key)."""
    pass

class ValidationError(NanoGPTError):
    """Raised when input validation fails."""
    pass
