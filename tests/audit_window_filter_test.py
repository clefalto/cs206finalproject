"""
Tests for audit_window_filter function using Hypothesis testing framework.
Tests all semantic properties identified in properties/audit_window_filter_properties.json.
"""

import pytest
from hypothesis import given, strategies as st, assume
from hypothesis.strategies import floats, lists, integers
from hypothesis.extra.numpy import arrays
import numpy as np

# Import the function under test
from dataset.python_programs.audit_window_filter import audit_window_filter


class TestAuditWindowFilter:
    """Test class for audit_window_filter function semantic properties."""

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000000), min_size=0),
        now=integers(min_value=0, max_value=1000000),
        window=integers(min_value=1, max_value=1000)
    )
    def test_monotonic_filter(self, timestamps, now, window):
        """Test that result is sorted in ascending order when input is sorted."""
        assume(sorted(timestamps) == timestamps)  # timestamps is sorted in ascending order
        
        result = audit_window_filter(timestamps, now, window=window)
        
        # Check that result is monotonic (non-decreasing)
        assert all(t1 <= t2 for t1, t2 in zip(result, result[1:])), \
            f"Result {result} is not monotonic"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000000), min_size=0),
        now=integers(min_value=0, max_value=1000000),
        window=integers(min_value=1, max_value=1000)
    )
    def test_subset_preservation(self, timestamps, now, window):
        """Test that result is a subset of input timestamps."""
        result = audit_window_filter(timestamps, now, window=window)
        
        # Check that all elements in result are in original timestamps
        assert all(t in timestamps for t in result), \
            f"Result {result} contains elements not in original timestamps {timestamps}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000000), min_size=0),
        now=integers(min_value=0, max_value=1000000),
        window=integers(min_value=1, max_value=1000)
    )
    def test_cutoff_filtering(self, timestamps, now, window):
        """Test that all timestamps in result are >= cutoff."""
        result = audit_window_filter(timestamps, now, window=window)
        cutoff = now - window
        
        # Check that all elements in result are >= cutoff
        assert all(t >= cutoff for t in result), \
            f"Result {result} contains elements < cutoff {cutoff}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000000), min_size=0),
        now=integers(min_value=0, max_value=1000000),
        window=integers(min_value=1, max_value=1000)
    )
    def test_completeness(self, timestamps, now, window):
        """Test that all timestamps >= cutoff are included in result."""
        result = audit_window_filter(timestamps, now, window=window)
        cutoff = now - window
        
        # Check that all timestamps >= cutoff are in result
        expected_in_result = [t for t in timestamps if t >= cutoff]
        assert all(t in result for t in expected_in_result), \
            f"Result {result} is missing elements from {expected_in_result}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000000), min_size=0),
        now=integers(min_value=0, max_value=1000000),
        window=integers(min_value=1, max_value=1000)
    )
    def test_order_preservation(self, timestamps, now, window):
        """Test that relative order of timestamps is preserved."""
        assume(len(timestamps) > 1)  # Need at least 2 elements to test order
        
        result = audit_window_filter(timestamps, now, window=window)
        
        # Check that order is preserved (indices in original list should be increasing)
        if len(result) > 1:
            for i in range(len(result) - 1):
                t1, t2 = result[i], result[i + 1]
                assert timestamps.index(t1) < timestamps.index(t2), \
                    f"Order not preserved: {t1} at index {timestamps.index(t1)} should come before {t2} at index {timestamps.index(t2)}"

    @given(
        now=integers(min_value=0, max_value=1000000),
        window=integers(min_value=1, max_value=1000)
    )
    def test_empty_input(self, now, window):
        """Test that empty input produces empty result."""
        timestamps = []
        
        result = audit_window_filter(timestamps, now, window=window)
        
        # Check that result is empty
        assert len(result) == 0, f"Empty input should produce empty result, got {result}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000000), min_size=1),
        now=integers(min_value=0, max_value=1000000),
        window=integers(min_value=1, max_value=1000)
    )
    def test_all_below_cutoff(self, timestamps, now, window):
        """Test that when all timestamps are below cutoff, result is empty."""
        assume(all(t < (now - window) for t in timestamps))  # all(t < cutoff for t in timestamps)
        
        result = audit_window_filter(timestamps, now, window=window)
        
        # Check that result is empty
        assert len(result) == 0, f"All timestamps below cutoff should produce empty result, got {result}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000000), min_size=1),
        now=integers(min_value=0, max_value=1000000),
        window=integers(min_value=1, max_value=1000)
    )
    def test_all_above_cutoff(self, timestamps, now, window):
        """Test that when all timestamps are >= cutoff, result equals input."""
        assume(all(t >= (now - window) for t in timestamps))  # all(t >= cutoff for t in timestamps)
        
        result = audit_window_filter(timestamps, now, window=window)
        
        # Check that result equals input
        assert result == timestamps, f"All timestamps above cutoff should produce identical result, got {result} vs {timestamps}"

    @given(
        timestamps=lists(integers(min_value=0, max_value=1000000), min_size=0),
        now=integers(min_value=0, max_value=1000000),
        window=integers(min_value=1, max_value=1000)
    )
    def test_size_bound(self, timestamps, now, window):
        """Test that result length is <= input length."""
        result = audit_window_filter(timestamps, now, window=window)
        
        # Check that result length is bounded by input length
        assert len(result) <= len(timestamps), \
            f"Result length {len(result)} should be <= input length {len(timestamps)}"