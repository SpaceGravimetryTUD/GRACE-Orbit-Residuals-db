import pytest
import pandas as pd
from src.utils.label_validation import (
    validate_rl_label, 
    validate_label_list, 
    get_default_allowed_labels,
    validate_data_labels
)

def test_validate_rl_label():
    """Test RL label format validation."""
    # Valid labels
    assert validate_rl_label("RL06_12-03") == True
    assert validate_rl_label("RL05_02-11") == True
    assert validate_rl_label("RL99_00-01") == True
    
    # Invalid labels
    assert validate_rl_label("RL6_12-03") == False    # Wrong version format
    assert validate_rl_label("RL06_2-03") == False    # Wrong year format
    assert validate_rl_label("RL06_12-3") == False    # Wrong month format
    assert validate_rl_label("RL06_12") == False      # Missing month
    assert validate_rl_label("invalid") == False      # Completely wrong

def test_validate_label_list():
    """Test label list validation."""
    valid_labels = ["RL06_12-03", "RL06_12-04"]
    invalid_labels = ["RL06_12-03", "invalid_label"]
    allowed = ["RL06_12-03", "RL06_12-04", "RL06_12-05"]
    
    # All valid
    errors = validate_label_list(valid_labels, allowed)
    assert len(errors) == 0
    
    # Some invalid
    errors = validate_label_list(invalid_labels, allowed)
    assert len(errors) > 0
    assert any("invalid_label" in error for error in errors)

def test_get_default_allowed_labels():
    """Test default allowed labels generation."""
    labels = get_default_allowed_labels()
    assert len(labels) == 16 * 12  # 16 years * 12 months
    assert "RL06_02-01" in labels  # 2002 January
    assert "RL06_17-12" in labels  # 2017 December
    
def test_validate_data_labels():
    """Test DataFrame label validation."""
    # Valid data
    df_valid = pd.DataFrame({
        "label": ["RL06_12-03", "RL06_12-04", "RL06_12-03"],
        "data": [1, 2, 3]
    })
    
    result = validate_data_labels(df_valid)
    assert result["total_unique_labels"] == 2
    assert result["valid_labels"] == 2
    assert result["invalid_labels"] == 0
    assert len(result["errors"]) == 0
    
    # Invalid data
    df_invalid = pd.DataFrame({
        "label": ["RL06_12-03", "invalid", "RL06_12-04"],
        "data": [1, 2, 3]
    })
    
    result = validate_data_labels(df_invalid)
    assert result["total_unique_labels"] == 3
    assert result["valid_labels"] == 2
    assert result["invalid_labels"] == 1
    assert len(result["errors"]) > 0