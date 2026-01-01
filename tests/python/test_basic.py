import pytest
from nanogpt_chat.exceptions import NanoGPTError, APIError

def test_exceptions():
    with pytest.raises(APIError):
        raise APIError("Test API error")
    
    with pytest.raises(NanoGPTError):
        raise APIError("Test API error")

def test_credentials_logic(mocker):
    # Mocking keyring to avoid system dependency in tests
    mock_keyring = mocker.patch("keyring.get_password")
    mock_keyring.return_value = "test-key"
    
    from nanogpt_chat.utils.credentials import SecureCredentialManager
    assert SecureCredentialManager.get_api_key() == "test-key"
