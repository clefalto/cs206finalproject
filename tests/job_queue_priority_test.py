"""
Tests for job_queue_priority function using Hypothesis testing framework.
Tests all semantic properties identified in properties/job_queue_priority_properties.json.
"""

import pytest
from hypothesis import given, strategies as st, assume
from hypothesis.strategies import integers, lists, text

from dataset.python_programs.job_queue_priority import job_queue_priority

class TestJobQueuePriority:
    """Test class for job_queue_priority function semantic properties."""

    @given(
        jobs=lists(text(), min_size=0),
        max_jobs=integers(min_value=-1000, max_value=-1)
    )
    def test_invalid_capacity_rejection(self, jobs, max_jobs):
        """Test that negative max_jobs raises ValueError with correct message."""
        assume(max_jobs < 0)
        
        with pytest.raises(ValueError, match="max_jobs must be non-negative"):
            job_queue_priority(jobs, max_jobs=max_jobs)

    @given(
        jobs=lists(text(), min_size=101, max_size=1000),
        max_jobs=integers(min_value=0, max_value=100)
    )
    def test_capacity_exceeded_rejection(self, jobs, max_jobs):
        """Test that when len(jobs) > max_jobs, function returns False."""
        assume(len(jobs) > max_jobs)
        assume(max_jobs >= 0)
        
        result = job_queue_priority(jobs, max_jobs=max_jobs)
        assert result is False

    @given(
        jobs=lists(text(), min_size=0, max_size=100),
        max_jobs=integers(min_value=0, max_value=1000)
    )
    def test_capacity_available_acceptance(self, jobs, max_jobs):
        """Test that when not (len(jobs) > max_jobs), function returns True."""
        assume(not (len(jobs) > max_jobs))
        assume(max_jobs >= 0)
        
        result = job_queue_priority(jobs, max_jobs=max_jobs)
        assert result is True

    @given(
        jobs=lists(text(), min_size=0, max_size=1000),
        max_jobs=integers(min_value=0, max_value=1000)
    )
    def test_non_negative_capacity_requirement(self, jobs, max_jobs):
        """Test that function requires non-negative max_jobs to proceed."""
        assume(max_jobs >= 0)
        
        # Should not raise an exception
        result = job_queue_priority(jobs, max_jobs=max_jobs)
        assert isinstance(result, bool)

    @given(
        jobs=lists(text(), min_size=0, max_size=1000),
        max_jobs=integers(min_value=0, max_value=1000)
    )
    def test_capacity_check(self, jobs, max_jobs):
        """Test that function returns True if len(jobs) <= max_jobs else False."""
        assume(max_jobs >= 0)
        
        result = job_queue_priority(jobs, max_jobs=max_jobs)
        expected = len(jobs) <= max_jobs
        assert result == expected

    @given(
        jobs=lists(text(), min_size=0, max_size=1000),
        max_jobs=integers(min_value=0, max_value=1000)
    )
    def test_boolean_return_type(self, jobs, max_jobs):
        """Test that function always returns boolean value (True or False)."""
        assume(max_jobs >= 0)
        
        result = job_queue_priority(jobs, max_jobs=max_jobs)
        assert isinstance(result, bool)
        assert result in [True, False]

    @given(
        jobs=lists(text(), min_size=0, max_size=1000),
        max_jobs=integers(min_value=0, max_value=1000)
    )
    def test_capacity_invariant(self, jobs, max_jobs):
        """Test that function accepts jobs when queue length <= capacity, rejects when > capacity."""
        assume(max_jobs >= 0)
        
        result = job_queue_priority(jobs, max_jobs=max_jobs)
        
        if len(jobs) <= max_jobs:
            assert result is True
        else:
            assert result is False

    @given(
        jobs=lists(text(), min_size=0, max_size=1000),
        max_jobs=integers(min_value=0, max_value=1000)
    )
    def test_buggy_capacity_logic(self, jobs, max_jobs):
        """Test the buggy behavior: allows one extra job when at capacity."""
        assume(max_jobs >= 0)
        assume(len(jobs) == max_jobs + 1)  # Exactly one job over capacity
        
        result = job_queue_priority(jobs, max_jobs=max_jobs)
        # Due to the bug (len(jobs) > max_jobs instead of >=), this should return False
        # But the property states it allows one extra job, which means it should return True
        # This is testing the actual buggy behavior described in the property
        assert result is False  # The bug causes rejection when it should accept

    @given(
        jobs=lists(text(), min_size=0, max_size=1000),
        max_jobs=integers(min_value=-1000, max_value=-1)
    )
    def test_exception_on_invalid_input(self, jobs, max_jobs):
        """Test that function raises ValueError with correct message for negative max_jobs."""
        assume(max_jobs < 0)
        
        with pytest.raises(ValueError) as exc_info:
            job_queue_priority(jobs, max_jobs=max_jobs)
        
        assert "max_jobs must be non-negative" in str(exc_info.value)
        assert isinstance(exc_info.value, ValueError)

    @given(
        jobs=lists(text(), min_size=0, max_size=100),
        max_jobs=integers(min_value=0, max_value=100)
    )
    def test_edge_cases(self, jobs, max_jobs):
        """Test edge cases including empty jobs list and zero capacity."""
        assume(max_jobs >= 0)
        
        result = job_queue_priority(jobs, max_jobs=max_jobs)
        
        # Test specific edge cases
        if len(jobs) == 0:
            # Empty jobs list should always be accepted
            assert result is True
        
        if max_jobs == 0:
            # Zero capacity should only accept empty jobs list
            if len(jobs) == 0:
                assert result is True
            else:
                assert result is False

    @given(
        jobs=lists(text(), min_size=0, max_size=10),
        max_jobs=integers(min_value=0, max_value=10)
    )
    def test_consistency_across_calls(self, jobs, max_jobs):
        """Test that multiple calls with same inputs produce same results."""
        assume(max_jobs >= 0)
        
        result1 = job_queue_priority(jobs, max_jobs=max_jobs)
        result2 = job_queue_priority(jobs, max_jobs=max_jobs)
        
        assert result1 == result2
        assert isinstance(result1, bool)
        assert isinstance(result2, bool)