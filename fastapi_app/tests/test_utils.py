"""
Tests for utility functions and patterns.
"""

import pytest
from services.utils import CircuitBreaker, retry_with_backoff, CircuitBreakerState


class TestCircuitBreaker:
    """Tests for CircuitBreaker pattern."""

    def test_circuit_breaker_closed_state(self):
        """Test circuit breaker in CLOSED state."""
        cb = CircuitBreaker(failure_threshold=3)
        assert cb.state == CircuitBreakerState.CLOSED

    def test_circuit_breaker_call_success(self):
        """Test successful call through circuit breaker."""
        cb = CircuitBreaker()

        def success_func():
            return "success"

        result = cb.call(success_func)
        assert result == "success"

    def test_circuit_breaker_call_failure(self):
        """Test failed call through circuit breaker."""
        cb = CircuitBreaker(failure_threshold=2)

        def failing_func():
            raise ValueError("Test error")

        # First failure
        with pytest.raises(ValueError):
            cb.call(failing_func)
        assert cb.failure_count == 1

        # Second failure - opens circuit
        with pytest.raises(ValueError):
            cb.call(failing_func)
        assert cb.state == CircuitBreakerState.OPEN

    def test_circuit_breaker_open_blocks_requests(self):
        """Test that OPEN circuit breaker blocks requests."""
        cb = CircuitBreaker(failure_threshold=1)

        def failing_func():
            raise ValueError("Test error")

        # First call fails and opens circuit
        with pytest.raises(ValueError):
            cb.call(failing_func)

        assert cb.state == CircuitBreakerState.OPEN

        # Second call is blocked
        with pytest.raises(Exception, match="Circuit breaker is OPEN"):
            cb.call(lambda: "success")


class TestRetryDecorator:
    """Tests for retry_with_backoff decorator."""

    def test_retry_sync_success_first_attempt(self):
        """Test successful function call on first attempt."""
        call_count = 0

        @retry_with_backoff(max_retries=3)
        def success_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = success_func()
        assert result == "success"
        assert call_count == 1

    def test_retry_sync_success_after_failures(self):
        """Test successful call after some failures."""
        call_count = 0

        @retry_with_backoff(max_retries=3, backoff_factor=0.01)
        def eventually_success():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"

        result = eventually_success()
        assert result == "success"
        assert call_count == 3

    def test_retry_sync_exhausts_retries(self):
        """Test that retry exhausts all attempts."""
        call_count = 0

        @retry_with_backoff(max_retries=3, backoff_factor=0.01)
        def always_fails():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")

        with pytest.raises(ValueError):
            always_fails()

        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_async_success(self):
        """Test async function with retry."""
        call_count = 0

        @retry_with_backoff(max_retries=3)
        async def async_success():
            nonlocal call_count
            call_count += 1
            return "async_success"

        result = await async_success()
        assert result == "async_success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_async_with_failures(self):
        """Test async function with retries after failures."""
        call_count = 0

        @retry_with_backoff(max_retries=3, backoff_factor=0.01)
        async def async_eventually_success():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Temporary failure")
            return "async_success"

        result = await async_eventually_success()
        assert result == "async_success"
        assert call_count == 2


class TestRagService:
    """Tests for RAG service singleton."""

    def test_rag_singleton_pattern(self):
        """Test that RAG service uses singleton pattern."""
        from services.rag_service import RagService

        rag1 = RagService.get_instance("theme1")
        rag2 = RagService.get_instance("theme1")

        assert rag1 is rag2  # Same instance

    def test_rag_different_themes(self):
        """Test RAG service with different themes."""
        from services.rag_service import RagService

        RagService.cleanup()
        rag1 = RagService.get_instance("theme1")
        rag2 = RagService.get_instance("theme2")

        assert rag1 is not rag2  # Different instances
        assert rag1.theme == "theme1"
        assert rag2.theme == "theme2"
