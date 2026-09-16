import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import dictionaries, integers, tuples, just
from typing import Dict, Tuple, Optional, Any

# Import the function under test
from dataset.python_programs.token_expiry_check import token_expiry_check


class TestTokenExpiryCheck:
    """Test suite for token_expiry_check function using Hypothesis."""

    @given(
        tokens=dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=tuples(
                st.text(min_size=1, max_size=10),
                integers(min_value=0, max_value=1000000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=integers(min_value=0, max_value=1000000)
    )
    def test_no_token_found(self, tokens: Dict[str, Tuple[str, int]], key: str, now: int):
        """Test that function returns None when token key is not found."""
        assume(key not in tokens)
        
        result = token_expiry_check(tokens, key, now)
        assert result is None, f"Expected None for missing key '{key}', got {result}"

    @given(
        tokens=dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=tuples(
                st.text(min_size=1, max_size=10),
                integers(min_value=0, max_value=1000000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=integers(min_value=0, max_value=1000000)
    )
    def test_expired_token(self, tokens: Dict[str, Tuple[str, int]], key: str, now: int):
        """Test that function returns None when token has expired."""
        assume(key in tokens)
        value, expires_at = tokens[key]
        assume(now > expires_at)
        
        result = token_expiry_check(tokens, key, now)
        assert result is None, f"Expected None for expired token, got {result}"

    @given(
        tokens=dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=tuples(
                st.text(min_size=1, max_size=10),
                integers(min_value=0, max_value=1000000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=integers(min_value=0, max_value=1000000)
    )
    def test_valid_token_return(self, tokens: Dict[str, Tuple[str, int]], key: str, now: int):
        """Test that function returns correct value for valid, non-expired tokens."""
        assume(key in tokens)
        value, expires_at = tokens[key]
        assume(now <= expires_at)
        
        result = token_expiry_check(tokens, key, now)
        assert result == value, f"Expected value '{value}' for valid token, got {result}"

    @given(
        tokens=dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=tuples(
                st.text(min_size=1, max_size=10),
                integers(min_value=0, max_value=1000000)
            )
        ),
        key=st.text(min_size=1, max_size=10)
    )
    def test_token_expiry_boundary(self, tokens: Dict[str, Tuple[str, int]], key: str):
        """Test that function returns value at exact expiry time."""
        assume(key in tokens)
        value, expires_at = tokens[key]
        
        result = token_expiry_check(tokens, key, expires_at)
        assert result == value, f"Expected value '{value}' at expiry time, got {result}"

    @given(
        tokens=dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=tuples(
                st.text(min_size=1, max_size=10),
                integers(min_value=0, max_value=1000000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now1=integers(min_value=0, max_value=1000000),
        now2=integers(min_value=0, max_value=1000000)
    )
    def test_monotonic_expiry(self, tokens: Dict[str, Tuple[str, int]], key: str, now1: int, now2: int):
        """Test that if token is valid at time t1, it remains valid at any time t2 >= t1."""
        assume(key in tokens)
        assume(now1 <= now2)
        
        result1 = token_expiry_check(tokens, key, now1)
        result2 = token_expiry_check(tokens, key, now2)
        
        # If token is valid at now1, it should also be valid at now2 (monotonic property)
        if result1 is not None:
            assert result2 is not None, f"Token valid at time {now1} but expired at later time {now2}"
            assert result1 == result2, f"Token value changed from {result1} to {result2} over time"

    @given(
        tokens=dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=tuples(
                st.text(min_size=1, max_size=10),
                integers(min_value=0, max_value=1000000)
            )
        ),
        key1=st.text(min_size=1, max_size=10),
        key2=st.text(min_size=1, max_size=10),
        now=integers(min_value=0, max_value=1000000)
    )
    def test_key_independence(self, tokens: Dict[str, Tuple[str, int]], key1: str, key2: str, now: int):
        """Test that function behavior is independent of key when token records are identical."""
        assume(key1 != key2)
        assume(key1 in tokens and key2 in tokens)
        assume(tokens[key1] == tokens[key2])
        
        result1 = token_expiry_check(tokens, key1, now)
        result2 = token_expiry_check(tokens, key2, now)
        
        assert result1 == result2, f"Identical token records should produce identical results: {result1} != {result2}"

    @given(
        tokens=dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=tuples(
                st.text(min_size=1, max_size=10),
                integers(min_value=0, max_value=1000000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=integers(min_value=0, max_value=1000000)
    )
    def test_deterministic(self, tokens: Dict[str, Tuple[str, int]], key: str, now: int):
        """Test that function produces deterministic results for same inputs."""
        result1 = token_expiry_check(tokens, key, now)
        result2 = token_expiry_check(tokens, key, now)
        
        assert result1 == result2, f"Function should be deterministic: {result1} != {result2}"

    @given(
        tokens=dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=tuples(
                st.text(min_size=1, max_size=10),
                integers(min_value=0, max_value=1000000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=integers(min_value=0, max_value=1000000)
    )
    def test_empty_tokens_dict(self, tokens: Dict[str, Tuple[str, int]], key: str, now: int):
        """Test behavior with empty tokens dictionary."""
        assume(len(tokens) == 0)
        
        result = token_expiry_check(tokens, key, now)
        assert result is None, f"Expected None for empty tokens dict, got {result}"

    @given(
        tokens=dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=tuples(
                st.text(min_size=1, max_size=10),
                integers(min_value=0, max_value=1000000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=integers(min_value=0, max_value=1000000)
    )
    def test_future_expiry(self, tokens: Dict[str, Tuple[str, int]], key: str, now: int):
        """Test that tokens with future expiry times are valid."""
        assume(key in tokens)
        value, expires_at = tokens[key]
        assume(expires_at > now)
        
        result = token_expiry_check(tokens, key, now)
        assert result == value, f"Token with future expiry should be valid, got {result}"

    @given(
        tokens=dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=tuples(
                st.text(min_size=1, max_size=10),
                integers(min_value=0, max_value=1000000)
            )
        ),
        key=st.text(min_size=1, max_size=10),
        now=integers(min_value=0, max_value=1000000)
    )
    def test_past_expiry(self, tokens: Dict[str, Tuple[str, int]], key: str, now: int):
        """Test that tokens with past expiry times are invalid."""
        assume(key in tokens)
        value, expires_at = tokens[key]
        assume(expires_at < now)
        
        result = token_expiry_check(tokens, key, now)
        assert result is None, f"Token with past expiry should be invalid, got {result}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])