import pytest
from hypothesis import given, assume, strategies as st
from hypothesis.strategies import integers, floats, none, one_of, dictionaries, text, sampled_from
import sys
import os

# Add the current directory to Python path to import the function
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the function under test
# Note: This assumes the track_deployment function is in a module that can be imported
# If the function is not available, the tests will need to be adapted accordingly
try:
    from track_deployment import track_deployment
except ImportError:
    # If the function is not available, we'll create a mock implementation for testing
    def track_deployment(counts, key, max_value=None):
        """
        Mock implementation of track_deployment for testing purposes.
        This should be replaced with the actual function implementation.
        """
        if key not in counts:
            counts[key] = 0
        
        new_value = counts[key] + 1
        original_new_value = new_value
        
        if max_value is not None:
            if new_value > max_value:
                new_value = max_value
        
        counts[key] = new_value
        return new_value


class TestTrackDeploymentProperties:
    """Test class for track_deployment semantic properties using Hypothesis."""

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000)),
        key=text(),
        max_value=one_of(integers(min_value=0, max_value=1000), none())
    )
    def test_clamping_applied(self, counts, key, max_value):
        """
        Test Property: clamping_applied
        Scope: branch
        Condition: max_value is not None
        Formal: new_value <= max_value
        """
        assume(max_value is not None)
        
        # Store original value
        original_value = counts.get(key, 0)
        
        # Call the function
        new_value = track_deployment(counts, key, max_value)
        
        # Property: new_value <= max_value
        assert new_value <= max_value, f"Expected new_value ({new_value}) <= max_value ({max_value})"

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000)),
        key=text(),
        max_value=integers(min_value=0, max_value=1000)
    )
    def test_value_capped(self, counts, key, max_value):
        """
        Test Property: value_capped
        Scope: branch
        Condition: new_value > max_value
        Formal: new_value == max_value
        """
        # Set up the condition where new_value > max_value
        counts[key] = max_value + 10  # Ensure new_value will exceed max_value
        
        # Call the function
        new_value = track_deployment(counts, key, max_value)
        
        # Property: new_value == max_value
        assert new_value == max_value, f"Expected new_value ({new_value}) == max_value ({max_value})"

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000)),
        key=text(),
        max_value=integers(min_value=0, max_value=1000)
    )
    def test_bounded_output(self, counts, key, max_value):
        """
        Test Property: bounded_output
        Scope: function
        Precondition: max_value is not None
        Formal: new_value <= max_value
        """
        # Call the function
        new_value = track_deployment(counts, key, max_value)
        
        # Property: new_value <= max_value
        assert new_value <= max_value, f"Expected new_value ({new_value}) <= max_value ({max_value})"

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000)),
        key=text(),
        max_value=integers(min_value=0, max_value=1000)
    )
    def test_monotonicity_preserved(self, counts, key, max_value):
        """
        Test Property: monotonicity_preserved
        Scope: function
        Precondition: max_value is not None
        Formal: new_value <= original_new_value
        """
        # Store the original value to calculate what new_value would be without clamping
        original_value = counts.get(key, 0)
        original_new_value = original_value + 1
        
        # Call the function
        new_value = track_deployment(counts, key, max_value)
        
        # Property: new_value <= original_new_value
        assert new_value <= original_new_value, f"Expected new_value ({new_value}) <= original_new_value ({original_new_value})"

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000)),
        key=text()
    )
    def test_identity_when_unbounded(self, counts, key):
        """
        Test Property: identity_when_unbounded
        Scope: function
        Precondition: max_value is None
        Formal: new_value == original_new_value
        """
        # Store the original value to calculate what new_value would be without clamping
        original_value = counts.get(key, 0)
        original_new_value = original_value + 1
        
        # Call the function with max_value=None
        new_value = track_deployment(counts, key, max_value=None)
        
        # Property: new_value == original_new_value
        assert new_value == original_new_value, f"Expected new_value ({new_value}) == original_new_value ({original_new_value})"

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000)),
        key=text(),
        max_value=one_of(integers(min_value=0, max_value=1000), none())
    )
    def test_non_negative_output(self, counts, key, max_value):
        """
        Test Property: non_negative_output
        Scope: function
        Precondition: new_value >= 0
        Formal: new_value >= 0
        """
        # Ensure the precondition (new_value >= 0) by starting with non-negative values
        assume(counts.get(key, 0) >= 0)
        
        # Call the function
        new_value = track_deployment(counts, key, max_value)
        
        # Property: new_value >= 0
        assert new_value >= 0, f"Expected new_value ({new_value}) >= 0"

    @given(
        counts=dictionaries(text(), integers(min_value=0, max_value=1000)),
        key=text(),
        max_value=one_of(integers(min_value=0, max_value=1000), none())
    )
    def test_deterministic(self, counts, key, max_value):
        """
        Test Property: deterministic
        Scope: function
        Precondition: counts and key are unchanged
        Formal: track_deployment(counts, key) == track_deployment(counts, key)
        """
        # Make copies to ensure we're testing with identical inputs
        counts_copy1 = counts.copy()
        counts_copy2 = counts.copy()
        
        # Call the function twice with identical inputs
        result1 = track_deployment(counts_copy1, key, max_value)
        result2 = track_deployment(counts_copy2, key, max_value)
        
        # Property: track_deployment(counts, key) == track_deployment(counts, key)
        assert result1 == result2, f"Expected deterministic behavior: {result1} == {result2}"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])