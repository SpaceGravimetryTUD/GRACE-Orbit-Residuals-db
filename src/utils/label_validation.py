# src/utils/label_validation.py
import re
from typing import List, Optional

def validate_rl_label(label: str) -> bool:
    """
    Validate RL<version>_<year>-<month> format label.
    
    Args:
        label: Label string to validate (e.g., "RL06_12-03")
        
    Returns:
        bool: True if label matches RL format pattern
        
    Examples:
        >>> validate_rl_label("RL06_12-03")
        True
        >>> validate_rl_label("RL06_invalid")
        False
    """
    pattern = r'^RL\d{2}_\d{2}-\d{2}$'
    return bool(re.match(pattern, label))

def validate_label_list(labels: List[str], allowed_labels: Optional[List[str]] = None) -> List[str]:
    """
    Validate a list of labels against format and optional allowed list.
    
    Args:
        labels: List of labels to validate
        allowed_labels: Optional list of allowed labels for validation
        
    Returns:
        List of validation errors (empty if all valid)
    """
    errors = []
    
    for label in labels:
        # Check format
        if not validate_rl_label(label):
            errors.append(f"Invalid label format: '{label}' (expected RL##_##-##)")
        
        # Check against allowed list if provided
        if allowed_labels and label not in allowed_labels:
            errors.append(f"Label '{label}' not in allowed list")
    
    return errors

def get_default_allowed_labels() -> List[str]:
    """
    Generate default allowed labels for 2002-2017 GRACE period.
    
    Returns:
        List of valid RL06 labels for the GRACE mission period
    """
    labels = []
    for year in range(2, 18):  # 2002-2017 -> 02-17
        for month in range(1, 13):  # 01-12
            labels.append(f"RL06_{year:02d}-{month:02d}")
    return labels

def validate_data_labels(df, label_column: str = "label") -> dict:
    """
    Validate labels in a DataFrame.
    
    Args:
        df: DataFrame containing label column
        label_column: Name of the label column
        
    Returns:
        dict: Validation report with errors and statistics
    """
    if label_column not in df.columns:
        return {"error": f"Column '{label_column}' not found in DataFrame"}
    
    labels = df[label_column].dropna().unique()
    allowed = get_default_allowed_labels()
    errors = validate_label_list(labels, allowed)
    
    return {
        "total_unique_labels": len(labels),
        "valid_labels": len([l for l in labels if validate_rl_label(l)]),
        "invalid_labels": len([l for l in labels if not validate_rl_label(l)]),
        "errors": errors,
        "labels_found": sorted(labels.tolist())
    }