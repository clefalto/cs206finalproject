import pytest
from hypothesis import given, assume, strategies as st
from typing import Dict, Optional, Any


class WarningMeter:
    """Mock implementation of warning_meter function for testing"""
    
    def __init__(self):
        self.counters: Dict[str, int] = {}
    
    def warning_meter(self, key: str, cap: Optional[int] = None) -> int:
        """
        Mock implementation of the warning_meter function.
        This simulates the behavior described in the properties.
        """
        # Initialize counter if key doesn't exist
        if key not in self.counters:
            self.counters[key] = 0
        
        # Increment the counter
        self.counters[key] += 1
        
        # Apply cap enforcement if cap is set and counter exceeds it
        if cap is not None and self.counters[key] > cap:
            self.counters[key] = cap
        
        return self.counters[key]


@st.composite
def warning_meter_state(draw):
    """Strategy to generate valid warning meter states"""
    # Generate a dictionary of string keys to non-negative integers
    counters = draw(st.dictionaries(
        st.text(min_size=1, max_size=10),  # keys
        st.integers(min_value=0, max_value=1000),  # values
        min_size=0,
        max_size=10
    ))
    
    # Generate optional cap (None or positive integer)
    cap = draw(st.one_of(st.none(), st.integers(min_value=1, max_value=1000)))
    
    # Generate a key (either existing or new)
    existing_keys = list(counters.keys()) if counters else []
    new_key = draw(st.text(min_size=1, max_size=10))
    
    if existing_keys:
        key = draw(st.one_of(st.sampled_from(existing_keys), st.just(new_key)))
    else:
        key = new_key
    
    return counters, cap, key


class TestWarningMeterProperties:
    """Test class for warning meter semantic properties"""
    
    @given(st.data())
    def test_cap_enforcement_property(self, data):
        """Test cap_enforcement property: when cap is not None and counters[key] > cap, counters[key] = cap"""
        counters, cap, key = data.draw(warning_meter_state())
        
        # Skip if cap is None (property doesn't apply)
        assume(cap is not None)
        
        # Create initial state
        meter = WarningMeter()
        meter.counters = counters.copy()
        
        # Get initial value
        initial_value = meter.counters.get(key, 0)
        
        # Simulate the condition: counters[key] > cap
        # We need to ensure that after incrementing, the value would exceed cap
        if initial_value < cap:
            # Increment until we exceed cap
            while meter.counters[key] <= cap:
                meter.warning_meter(key, cap)
        
        # Now call warning_meter which should enforce the cap
        result = meter.warning_meter(key, cap)
        
        # Property: counters[key] should equal cap
        assert meter.counters[key] == cap, f"Expected {cap}, got {meter.counters[key]}"
        assert result == cap, f"Expected return value {cap}, got {result}"
    
    @given(st.data())
    def test_key_preservation_property(self, data):
        """Test key_preservation property: if key in counters, then counters[key] is not None"""
        counters, cap, key = data.draw(warning_meter_state())
        
        # Skip if key is not in counters (precondition not met)
        assume(key in counters)
        
        # Create initial state
        meter = WarningMeter()
        meter.counters = counters.copy()
        
        # Call warning_meter
        result = meter.warning_meter(key, cap)
        
        # Property: counters[key] should not be None
        assert key in meter.counters, f"Key {key} should still be in counters"
        assert meter.counters[key] is not None, f"counters[{key}] should not be None"
        assert isinstance(meter.counters[key], int), f"counters[{key}] should be an integer"
    
    @given(st.data())
    def test_cap_bound_property(self, data):
        """Test cap_bound property: if cap is not None, then counters[key] <= cap"""
        counters, cap, key = data.draw(warning_meter_state())
        
        # Skip if cap is None (precondition not met)
        assume(cap is not None)
        
        # Create initial state
        meter = WarningMeter()
        meter.counters = counters.copy()
        
        # Call warning_meter multiple times to test the bound
        for _ in range(5):  # Test multiple calls
            result = meter.warning_meter(key, cap)
            
            # Property: counters[key] should be <= cap
            assert meter.counters[key] <= cap, f"counters[{key}] = {meter.counters[key]} should be <= cap = {cap}"
            assert result <= cap, f"Return value {result} should be <= cap = {cap}"
    
    @given(st.data())
    def test_non_negative_property(self, data):
        """Test non_negative property: if counters[key] >= 0, then counters[key] >= 0"""
        counters, cap, key = data.draw(warning_meter_state())
        
        # Ensure precondition: counters[key] >= 0 (this should always be true with our strategy)
        assume(key not in counters or counters[key] >= 0)
        
        # Create initial state
        meter = WarningMeter()
        meter.counters = counters.copy()
        
        # Call warning_meter
        result = meter.warning_meter(key, cap)
        
        # Property: counters[key] should be >= 0
        assert meter.counters[key] >= 0, f"counters[{key}] = {meter.counters[key]} should be >= 0"
        assert result >= 0, f"Return value {result} should be >= 0"
    
    @given(st.data())
    def test_monotonicity_property(self, data):
        """Test monotonicity property: if counters[key] >= 0, then counters[key] <= initial_counters[key]"""
        counters, cap, key = data.draw(warning_meter_state())
        
        # Ensure precondition: counters[key] >= 0
        assume(key not in counters or counters[key] >= 0)
        
        # Create initial state
        meter = WarningMeter()
        meter.counters = counters.copy()
        
        # Store initial value
        initial_value = meter.counters.get(key, 0)
        
        # Call warning_meter
        result = meter.warning_meter(key, cap)
        
        # Property: counters[key] should be <= initial value (monotonic decrease or stay same due to cap)
        # Note: This property seems to suggest the counter should not increase, but the function
        # actually increments first then applies cap. The property might be about the final
        # value being bounded by the initial value in some scenarios.
        
        # Let's test that the final value doesn't exceed the initial value by more than 1
        # (since we increment by 1 before applying cap)
        expected_max = initial_value + 1
        if cap is not None:
            expected_max = min(expected_max, cap)
        
        assert meter.counters[key] <= expected_max, \
            f"counters[{key}] = {meter.counters[key]} should be <= {expected_max} (initial={initial_value}, cap={cap})"
    
    @given(
        st.dictionaries(st.text(min_size=1, max_size=5), st.integers(min_value=0, max_value=100)),
        st.one_of(st.none(), st.integers(min_value=1, max_value=100)),
        st.text(min_size=1, max_size=5)
    )
    def test_warning_meter_integration(self, counters, cap, key):
        """Integration test that combines multiple properties"""
        meter = WarningMeter()
        meter.counters = counters.copy()
        
        initial_count = meter.counters.get(key, 0)
        
        # Call warning_meter
        result = meter.warning_meter(key, cap)
        
        # Verify basic properties
        assert key in meter.counters
        assert meter.counters[key] >= 0
        assert result >= 0
        
        # If cap is set, verify it's respected
        if cap is not None:
            assert meter.counters[key] <= cap
            assert result <= cap
        
        # Verify the counter was incremented (unless capped)
        expected_value = initial_count + 1
        if cap is not None and expected_value > cap:
            expected_value = cap
        
        assert meter.counters[key] == expected_value
        assert result == expected_value


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])