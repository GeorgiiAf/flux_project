"""Compliance checking component for vehicle watchlist database.

This module provides the ComplianceChecker class for querying
license plates against a compliance database.
"""

import logging
import pandas as pd
from typing import Optional, Dict
from pathlib import Path
from models import ViolationInfo


logger = logging.getLogger(__name__)


class ComplianceChecker:
    """Checks license plates against a compliance database.
    
    This class loads and queries a watchlist database containing
    vehicles with compliance violations (expired inspection, stolen,
    blacklisted, wanted).
    
    Attributes:
        database_path: Path to the CSV database file
        database: Pandas DataFrame containing the watchlist
    """
    
    def __init__(self, database_path: str):
        """Initialize ComplianceChecker with database file.
        
        Args:
            database_path: Path to CSV file containing watchlist data
                          Expected columns: plate_number, category, details, date_added
            
        Raises:
            FileNotFoundError: If database file does not exist
            ValueError: If database file is malformed
        """
        self.database_path = Path(database_path)
        
        if not self.database_path.exists():
            raise FileNotFoundError(f"Database file not found: {database_path}")
        
        logger.info(f"Loading compliance database from: {database_path}")
        self.database = self._load_database()
        logger.info(f"Loaded {len(self.database)} entries from compliance database")
    
    def _load_database(self) -> pd.DataFrame:
        """Load the compliance database from CSV file.
        
        Returns:
            DataFrame containing the watchlist data
            
        Raises:
            ValueError: If database file is malformed or missing required columns
        """
        try:
            # Load CSV file
            df = pd.read_csv(self.database_path)
            
            # Validate required columns
            required_columns = ['plate_number', 'category', 'details', 'date_added']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Database missing required columns: {missing_columns}")
            
            # Normalize plate numbers (uppercase, no spaces)
            df['plate_number'] = df['plate_number'].str.upper().str.replace(' ', '', regex=False)
            
            # Remove any duplicate plate numbers (keep first occurrence)
            original_count = len(df)
            df = df.drop_duplicates(subset=['plate_number'], keep='first')
            
            if len(df) < original_count:
                logger.warning(f"Removed {original_count - len(df)} duplicate entries from database")
            
            return df
            
        except pd.errors.EmptyDataError:
            logger.warning("Database file is empty, creating empty DataFrame")
            return pd.DataFrame(columns=['plate_number', 'category', 'details', 'date_added'])
        except Exception as e:
            logger.error(f"Error loading database: {e}")
            raise ValueError(f"Failed to load database: {e}")
    
    def check_plate(self, plate_number: str) -> Optional[ViolationInfo]:
        """Check if a plate number is in the compliance database.
        
        Args:
            plate_number: License plate number to check (will be normalized)
            
        Returns:
            ViolationInfo object if plate is in database, None otherwise
        """
        if not plate_number or not plate_number.strip():
            logger.warning("Empty plate number provided to check_plate")
            return None
        
        try:
            # Normalize plate number for comparison
            normalized_plate = plate_number.upper().replace(' ', '')
            
            # Query database
            matches = self.database[self.database['plate_number'] == normalized_plate]
            
            if matches.empty:
                logger.debug(f"Plate {normalized_plate} not found in database")
                return None
            
            # Get first match (should only be one due to deduplication)
            match = matches.iloc[0]
            
            # Create ViolationInfo object
            violation_info = ViolationInfo(
                plate_number=match['plate_number'],
                category=match['category'],
                details=match['details'],
                date_added=match['date_added']
            )
            
            logger.info(f"Match found for plate {normalized_plate}: {match['category']}")
            return violation_info
            
        except Exception as e:
            logger.error(f"Error checking plate {plate_number}: {e}")
            return None
    
    def reload_database(self):
        """Reload the database from file without restarting.
        
        This allows hot-reloading of the database when it's updated.
        """
        logger.info("Reloading compliance database...")
        try:
            self.database = self._load_database()
            logger.info(f"Database reloaded successfully: {len(self.database)} entries")
        except Exception as e:
            logger.error(f"Failed to reload database: {e}")
            raise
    
    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about the database contents.
        
        Returns:
            Dictionary with counts by violation category
        """
        if self.database.empty:
            return {}
        
        # Count entries by category
        stats = self.database['category'].value_counts().to_dict()
        
        # Add total count
        stats['total'] = len(self.database)
        
        return stats
    
    def add_entry(self, plate_number: str, category: str, details: str, date_added: str):
        """Add a new entry to the database (in-memory only).
        
        Note: This does not persist to the CSV file. Use this for testing
        or temporary additions. To persist, write the database back to CSV.
        
        Args:
            plate_number: License plate number
            category: Violation category
            details: Additional details
            date_added: Date entry was added
        """
        # Normalize plate number
        normalized_plate = plate_number.upper().replace(' ', '')
        
        # Create new entry
        new_entry = pd.DataFrame([{
            'plate_number': normalized_plate,
            'category': category,
            'details': details,
            'date_added': date_added
        }])
        
        # Append to database
        self.database = pd.concat([self.database, new_entry], ignore_index=True)
        
        logger.info(f"Added entry for plate {normalized_plate}: {category}")
    
    def save_database(self):
        """Save the current database back to CSV file.
        
        This persists any in-memory changes made via add_entry().
        """
        try:
            self.database.to_csv(self.database_path, index=False)
            logger.info(f"Database saved to {self.database_path}")
        except Exception as e:
            logger.error(f"Failed to save database: {e}")
            raise


def main():
    """Test the ComplianceChecker with sample data."""
    import sys
    from datetime import datetime
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Use command line argument or default database
    if len(sys.argv) > 1:
        database_path = sys.argv[1]
    else:
        database_path = "data/watchlist.csv"
    
    try:
        print("\n=== Testing ComplianceChecker ===\n")
        
        # Check if database exists
        if not Path(database_path).exists():
            print(f"Database not found: {database_path}")
            print("Creating sample database for testing...")
            
            # Create sample database
            sample_data = pd.DataFrame([
                {'plate_number': 'ABC123', 'category': 'expired_inspection', 
                 'details': 'Inspection expired 2023-06-15', 'date_added': '2024-01-01'},
                {'plate_number': 'XYZ789', 'category': 'stolen', 
                 'details': 'Reported stolen 2023-12-20', 'date_added': '2023-12-21'},
                {'plate_number': 'DEF456', 'category': 'blacklisted', 
                 'details': 'Multiple unpaid fines', 'date_added': '2024-02-15'},
                {'plate_number': 'GHI789', 'category': 'wanted', 
                 'details': 'Connected to criminal investigation', 'date_added': '2024-03-01'},
            ])
            
            Path(database_path).parent.mkdir(parents=True, exist_ok=True)
            sample_data.to_csv(database_path, index=False)
            print(f"✅ Sample database created at: {database_path}\n")
        
        # Initialize checker
        print(f"Loading database from: {database_path}")
        checker = ComplianceChecker(database_path)
        
        # Get statistics
        print("\n=== Database Statistics ===")
        stats = checker.get_statistics()
        for category, count in sorted(stats.items()):
            print(f"{category}: {count}")
        
        # Test plate checks
        print("\n=== Testing Plate Checks ===")
        test_plates = [
            'ABC123',      # Should match
            'abc 123',     # Should match (normalized)
            'XYZ789',      # Should match
            'NOTFOUND',    # Should not match
            'DEF456',      # Should match
        ]
        
        for plate in test_plates:
            result = checker.check_plate(plate)
            if result:
                print(f"✅ {plate:12} → MATCH: {result.category}")
                print(f"   Details: {result.details}")
            else:
                print(f"❌ {plate:12} → No match (compliant)")
        
        # Test adding entry
        print("\n=== Testing Add Entry ===")
        checker.add_entry(
            plate_number='TEST999',
            category='expired_inspection',
            details='Test entry',
            date_added=datetime.now().strftime('%Y-%m-%d')
        )
        
        result = checker.check_plate('TEST999')
        if result:
            print(f"✅ Successfully added and retrieved TEST999")
        
        print("\n✅ ComplianceChecker test completed!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
