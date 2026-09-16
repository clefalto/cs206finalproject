"""
Hypothesis-based property tests for normalize().

Properties are drawn from:
  - branch_properties.json  (branch-level, 4 properties)
  - function_properties.json (function-level, 4 properties)
"""

import pytest
from hypothesis import given, assume
from hypothesis import strategies as st
from normalize import normalize

# ---------------------------------------------------------------------------
# Shared strategies
# ---------------------------------------------------------------------------

# A list of floats that are finite and not NaN, so arithmetic is well-behaved.
finite_floats = st.floats(allow_nan=False, allow_infinity=False)

nonempty_list = st.lists(finite_floats, min_size=1)
any_list      = st.lists(finite_floats, min_size=0)

nonneg_floats    = st.floats(min_value=0.0, allow_nan=False, allow_infinity=False)
nonempty_nonneg  = st.lists(nonneg_floats, min_size=1)


# ===========================================================================
# BRANCH-LEVEL PROPERTIES
# ===========================================================================

# ---------------------------------------------------------------------------
# Branch: len(xs) == 0
# Property: identity_on_empty
# Formal:   normalize(xs) == xs
# ---------------------------------------------------------------------------
@given(st.just([]))
def test_branch_identity_on_empty(xs):
    """When the input list is empty, normalize returns the same empty list."""
    assert normalize(xs) == xs


# ---------------------------------------------------------------------------
# Branch: not (len(xs) == 0) and sum(xs) != 0
# Property: unit_sum_on_nonempty
# Formal:   sum(normalize(xs)) == 1
# ---------------------------------------------------------------------------
@given(nonempty_list)
def test_branch_unit_sum_on_nonempty(xs):
    """On a non-empty list whose elements sum to a non-zero value,
    the output elements sum to 1."""
    assume(sum(xs) != 0)
    result = normalize(xs)
    assert abs(sum(result) - 1.0) < 1e-9


# ---------------------------------------------------------------------------
# Branch: not (len(xs) == 0)
# Property: length_preserved_on_nonempty
# Formal:   len(normalize(xs)) == len(xs)
# ---------------------------------------------------------------------------
@given(nonempty_list)
def test_branch_length_preserved_on_nonempty(xs):
    """On a non-empty list, normalize returns a list of the same length."""
    assert len(normalize(xs)) == len(xs)


# ---------------------------------------------------------------------------
# Branch: not (len(xs) == 0) and all(x >= 0 for x in xs) and sum(xs) != 0
# Property: nonnegative_outputs_on_nonnegative_inputs
# Formal:   all(y >= 0 for y in normalize(xs))
# ---------------------------------------------------------------------------
@given(nonempty_nonneg)
def test_branch_nonnegative_outputs_on_nonnegative_inputs(xs):
    """On a non-empty list of non-negative values with a non-zero sum,
    every output element is non-negative."""
    assume(sum(xs) != 0)
    assert all(y >= 0 for y in normalize(xs))


# ===========================================================================
# FUNCTION-LEVEL PROPERTIES
# ===========================================================================

# ---------------------------------------------------------------------------
# Property: length_preserved
# Precondition: True  (holds for all inputs)
# Formal:   len(normalize(xs)) == len(xs)
# ---------------------------------------------------------------------------
@given(any_list)
def test_function_length_preserved(xs):
    """normalize always returns a list of the same length as the input."""
    assert len(normalize(xs)) == len(xs)


# ---------------------------------------------------------------------------
# Property: unit_sum
# Precondition: sum(xs) != 0
# Formal:   sum(normalize(xs)) == 1
# ---------------------------------------------------------------------------
@given(any_list)
def test_function_unit_sum(xs):
    """When the input elements have a non-zero sum, the output sums to 1."""
    assume(len(xs) > 0)
    assume(sum(xs) != 0)
    assert abs(sum(normalize(xs)) - 1.0) < 1e-9


# ---------------------------------------------------------------------------
# Property: nonnegative_outputs
# Precondition: all(x >= 0 for x in xs) and sum(xs) != 0
# Formal:   all(y >= 0 for y in normalize(xs))
# ---------------------------------------------------------------------------
@given(any_list)
def test_function_nonnegative_outputs(xs):
    """When all inputs are non-negative and their sum is non-zero,
    all outputs are non-negative."""
    assume(all(x >= 0 for x in xs))
    assume(sum(xs) != 0)
    assert all(y >= 0 for y in normalize(xs))


# ---------------------------------------------------------------------------
# Property: idempotent
# Precondition: sum(xs) != 0
# Formal:   normalize(normalize(xs)) == normalize(xs)
# ---------------------------------------------------------------------------
@given(any_list)
def test_function_idempotent(xs):
    """Applying normalize twice yields the same result as applying it once:
    a list that already sums to 1 is unchanged by a second normalization."""
    assume(len(xs) > 0)
    assume(sum(xs) != 0)
    once  = normalize(xs)
    twice = normalize(once)
    assert len(once) == len(twice)
    for a, b in zip(once, twice):
        assert abs(a - b) < 1e-9
