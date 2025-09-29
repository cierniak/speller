"""
Base Data Adapter

Abstract base class for different dataset format adapters.
"""

from abc import ABC, abstractmethod
from pathlib import Path
import polars as pl


class BaseDataAdapter(ABC):
    """
    Abstract base class for data adapters that handle different dataset formats.
    
    Data adapters are responsible for:
    - Loading datasets from various formats
    - Standardizing data into a consistent format
    - Providing data validation and statistics
    - Creating train/validation/test splits
    """
    
    def __init__(self, data_path: Path):
        """
        Initialize the adapter with a data path.
        
        Args:
            data_path: Path to the dataset file or directory
        """
        self.data_path = Path(data_path)
        self._data: pl.DataFrame | None = None
    
    @abstractmethod
    def load_data(self) -> pl.DataFrame:
        """
        Load and parse the dataset from the source format.
        
        Returns:
            Polars DataFrame with standardized columns:
            - word: The source word/text
            - ipa: The IPA pronunciation(s)
            - language: Language code (e.g., 'de', 'en_US')
        """
        pass
    
    @abstractmethod
    def validate_data(self, data: pl.DataFrame) -> dict[str, any]:
        """
        Validate the loaded data and return statistics.
        
        Args:
            data: The loaded DataFrame
            
        Returns:
            Dictionary containing validation results and statistics
        """
        pass
    
    def get_data(self, force_reload: bool = False) -> pl.DataFrame:
        """
        Get the loaded data, loading it if necessary.
        
        Args:
            force_reload: If True, reload data even if already loaded
            
        Returns:
            The loaded and validated DataFrame
        """
        if self._data is None or force_reload:
            self._data = self.load_data()
            validation_results = self.validate_data(self._data)
            if not validation_results.get('is_valid', False):
                raise ValueError(f"Data validation failed: {validation_results}")
        return self._data
    
    def create_splits(self, 
                     train_ratio: float = 0.8, 
                     val_ratio: float = 0.1,
                     test_ratio: float = 0.1,
                     seed: int = 42) -> tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame]:
        """
        Create train/validation/test splits from the data.
        
        Args:
            train_ratio: Proportion of data for training
            val_ratio: Proportion of data for validation  
            test_ratio: Proportion of data for testing
            seed: Random seed for reproducibility
            
        Returns:
            Tuple of (train_df, val_df, test_df)
        """
        if abs(train_ratio + val_ratio + test_ratio - 1.0) > 1e-6:
            raise ValueError("Split ratios must sum to 1.0")
        
        data = self.get_data()
        shuffled = data.sample(fraction=1.0, seed=seed)
        
        n_total = len(shuffled)
        n_train = int(n_total * train_ratio)
        n_val = int(n_total * val_ratio)
        
        train_df = shuffled[:n_train]
        val_df = shuffled[n_train:n_train + n_val]
        test_df = shuffled[n_train + n_val:]
        
        return train_df, val_df, test_df
    
    def get_language_stats(self) -> dict[str, int]:
        """
        Get statistics about languages in the dataset.
        
        Returns:
            Dictionary mapping language codes to word counts
        """
        data = self.get_data()
        return data.group_by("language").agg(pl.count()).to_dict(as_series=False)
    
    def get_word_pairs(self, language: str) -> list[tuple[str, str]]:
        """
        Extract word-IPA pairs for a specific language.
        
        Args:
            language: Language code to filter by
            
        Returns:
            List of (word, ipa) tuples for the specified language
        """
        data = self.get_data()
        filtered = data.filter(pl.col("language") == language)
        return list(zip(filtered["word"].to_list(), filtered["ipa"].to_list()))