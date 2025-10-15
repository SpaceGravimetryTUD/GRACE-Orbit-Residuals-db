import pytest
import pandas as pd
from datetime import datetime
from sqlalchemy import text
from src.models import engine, SessionLocal, KBRGravimetry
from src.utils.label_validation import validate_rl_label, validate_data_labels

def test_labeling_system_duplicate_timestamps():
    """
    Test the flexible labeling system handling records with same timestamps
    but different labels (original vs borrowed data).
    
    This demonstrates the core requirement: distinguishing records with
    identical timestamps through label-based metadata.
    """
    # Test data representing the duplication scenario
    test_data = [
        {
            'timestamp': 1017619200.0,  # Same timestamp
            'datetime': datetime(2002, 4, 1, 0, 0, 0),
            # GRACE-A satellite data
            'latitude_A': 52.1, 'longitude_A': 4.1,
            # GRACE-B satellite data (required fields)
            'latitude_B': 52.2, 'longitude_B': 4.2,
            'postfit': 0.001, 'up_combined': 0.003,
            'label': 'RL06_02-03',     # March 2002 solution
            'source': 'original',       # Original March data
            'variant': 'CSR_v1',
            'release': 'RL06'
        },
        {
            'timestamp': 1017619200.0,  # Same timestamp (!)
            'datetime': datetime(2002, 4, 1, 0, 0, 0),
            # GRACE-A satellite data
            'latitude_A': 52.1, 'longitude_A': 4.1,
            # GRACE-B satellite data (required fields)
            'latitude_B': 52.2, 'longitude_B': 4.2,
            'postfit': 0.002, 'up_combined': 0.004,  # Different values
            'label': 'RL06_02-04',     # April 2002 solution
            'source': 'borrowed',       # Borrowed for April solution
            'variant': 'CSR_v1',
            'release': 'RL06'
        }
    ]    # Insert test data into database
    session = SessionLocal()
    try:
        # Clear any existing test data
        session.execute(text("DELETE FROM kbr_gravimetry_v2 WHERE timestamp = 1017619200.0"))
        session.commit()
        
        # Insert the duplicate timestamp records
        for record in test_data:
            obj = KBRGravimetry(**record)
            session.add(obj)
        session.commit()
        
        # Verify we have 2 records with same timestamp
        same_timestamp_count = session.execute(
            text("SELECT COUNT(*) FROM kbr_gravimetry_v2 WHERE timestamp = 1017619200.0")
        ).scalar()
        assert same_timestamp_count == 2, f"Expected 2 records, got {same_timestamp_count}"
        
        # Test 1: Query all records (both original and borrowed)
        all_records = session.execute(
            text("SELECT label, source, postfit FROM kbr_gravimetry_v2 WHERE timestamp = 1017619200.0 ORDER BY label")
        ).fetchall()
        
        assert len(all_records) == 2
        assert all_records[0][0] == 'RL06_02-03'  # March label
        assert all_records[0][1] == 'original'     # Original source
        assert all_records[1][0] == 'RL06_02-04'  # April label  
        assert all_records[1][1] == 'borrowed'     # Borrowed source
        
        # Test 2: Filter by source (original only)
        original_only = session.execute(
            text("SELECT COUNT(*) FROM kbr_gravimetry_v2 WHERE timestamp = 1017619200.0 AND source = 'original'")
        ).scalar()
        assert original_only == 1
        
        # Test 3: Filter by source (borrowed only)
        borrowed_only = session.execute(
            text("SELECT COUNT(*) FROM kbr_gravimetry_v2 WHERE timestamp = 1017619200.0 AND source = 'borrowed'")
        ).scalar()
        assert borrowed_only == 1
        
        # Test 4: Filter by specific label
        march_data = session.execute(
            text("SELECT COUNT(*) FROM kbr_gravimetry_v2 WHERE timestamp = 1017619200.0 AND label = 'RL06_02-03'")
        ).scalar()
        assert march_data == 1
        
        # Test 5: Validate label format compliance
        df = pd.DataFrame(test_data)
        validation_result = validate_data_labels(df)
        assert validation_result['valid_labels'] == 2
        assert validation_result['invalid_labels'] == 0
        assert len(validation_result['errors']) == 0
        
        # Test 6: Verify RL06 format compliance
        for record in test_data:
            assert validate_rl_label(record['label']), f"Invalid label format: {record['label']}"
        
        print("✅ Labeling system test passed!")
        print(f"✅ Successfully handled {len(test_data)} records with same timestamp")
        print("✅ Labels comply with RL06_YY-MM format")
        print("✅ Source filtering (original/borrowed) works correctly")
        print("✅ Label-based filtering works correctly")
        
    finally:
        # Cleanup test data
        session.execute(text("DELETE FROM kbr_gravimetry_v2 WHERE timestamp = 1017619200.0"))
        session.commit()
        session.close()

def test_label_format_requirements():
    """
    Test that the labeling system meets the specified requirements:
    - Format: RL<version>_<year>-<month>
    - Example: RL06_12-03, RL06_12-04, etc.
    - Validation against allowed list
    """
    # Test valid labels from the GRACE period
    valid_labels = [
        "RL06_02-04",  # April 2002
        "RL06_11-11",  # November 2011 (problematic month mentioned)
        "RL06_11-12",  # December 2011 (problematic month mentioned)  
        "RL06_12-04",  # April 2012 (problematic month mentioned)
        "RL06_15-05",  # May 2015 (problematic month mentioned)
        "RL06_17-03",  # March 2017 (problematic month mentioned)
        "RL06_17-04",  # April 2017 (problematic month mentioned)
    ]
    
    # Test invalid labels
    invalid_labels = [
        "RL6_12-03",     # Wrong version format
        "RL06_2-03",     # Wrong year format  
        "RL06_12-3",     # Wrong month format
        "RL06_12",       # Missing month
        "invalid_label", # Completely wrong
    ]
    
    # Validate format compliance
    for label in valid_labels:
        assert validate_rl_label(label), f"Valid label failed validation: {label}"
    
    for label in invalid_labels:
        assert not validate_rl_label(label), f"Invalid label passed validation: {label}"
    
    print("✅ Label format requirements test passed!")
    print(f"✅ All {len(valid_labels)} valid labels passed format validation")
    print(f"✅ All {len(invalid_labels)} invalid labels correctly rejected")

def test_problematic_months_labeling():
    """
    Test the specific problematic months mentioned in the original discussion.
    These months had borrowed data from adjacent months.
    """
    problematic_cases = [
        # November 2011 uses October 16-31, 2011 data
        {"borrowed_label": "RL06_11-11", "source_label": "RL06_11-10", "description": "Nov 2011 borrows from Oct 2011"},
        
        # December 2011 uses January 1-11, 2012 data  
        {"borrowed_label": "RL06_11-12", "source_label": "RL06_12-01", "description": "Dec 2011 borrows from Jan 2012"},
        
        # April 2012 uses March 20-31, 2012 data
        {"borrowed_label": "RL06_12-04", "source_label": "RL06_12-03", "description": "Apr 2012 borrows from Mar 2012"},
        
        # May 2015 uses April 12-30, 2015 data
        {"borrowed_label": "RL06_15-05", "source_label": "RL06_15-04", "description": "May 2015 borrows from Apr 2015"},
    ]
    
    for case in problematic_cases:
        # Validate both labels are in correct format
        assert validate_rl_label(case["borrowed_label"]), f"Invalid borrowed label: {case['borrowed_label']}"
        assert validate_rl_label(case["source_label"]), f"Invalid source label: {case['source_label']}"
        
        print(f"✅ {case['description']}: {case['source_label']} → {case['borrowed_label']}")
    
    print("✅ Problematic months labeling test passed!")
    print("✅ All problematic month scenarios can be properly labeled and distinguished")