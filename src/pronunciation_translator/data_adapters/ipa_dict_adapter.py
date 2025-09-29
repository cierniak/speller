"""
IPA Dict Adapter

Data adapter for the ipa-dict dataset format.
Handles tab-separated files with word->IPA mappings.
"""

import re
from pathlib import Path
import polars as pl

from .base import BaseDataAdapter


class IPADictAdapter(BaseDataAdapter):
    """
    Data adapter for ipa-dict format datasets.
    
    The ipa-dict format consists of tab-separated files where each line contains:
    word<TAB>ipa_pronunciation(s)
    
    Multiple pronunciations are separated by commas and enclosed in forward slashes.
    Example: "hello	/həˈloʊ/, /hɛˈloʊ/"
    """
    
    def __init__(self, data_path: Path, language_code: str | None = None):
        """
        Initialize the IPA Dict adapter.
        
        Args:
            data_path: Path to the .txt file or directory containing language files
            language_code: Language code if loading a single file (auto-detected from filename if None)
        """
        super().__init__(data_path)
        self.language_code = language_code
        
    def _extract_language_code(self, file_path: Path) -> str:
        """
        Extract language code from filename.
        
        Args:
            file_path: Path to the data file
            
        Returns:
            Language code (e.g., 'de', 'en_US', 'es_ES')
        """
        if self.language_code:
            return self.language_code
        
        # Extract from filename (e.g., 'de.txt' -> 'de', 'en_US.txt' -> 'en_US')
        stem = file_path.stem
        return stem
    
    def _parse_ipa_pronunciations(self, ipa_string: str) -> list[str]:
        """
        Parse IPA pronunciation string and extract individual pronunciations.
        
        Args:
            ipa_string: Raw IPA string from the file (e.g., "/həˈloʊ/, /hɛˈloʊ/")
            
        Returns:
            List of individual IPA pronunciations without slashes
        """
        # Remove whitespace and split by commas
        pronunciations = []
        
        # Find all IPA pronunciations enclosed in forward slashes
        ipa_pattern = r'/([^/]+)/'
        matches = re.findall(ipa_pattern, ipa_string.strip())
        
        for match in matches:
            # Clean up the pronunciation
            clean_ipa = match.strip()
            if clean_ipa:
                pronunciations.append(clean_ipa)
        
        return pronunciations
    
    def load_data(self) -> pl.DataFrame:
        """
        Load and parse the ipa-dict dataset.
        
        Returns:
            Polars DataFrame with columns: word, ipa, language
        """
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data path does not exist: {self.data_path}")
        
        data_rows = []
        
        if self.data_path.is_file():
            # Single file
            files_to_process = [self.data_path]
        else:
            # Directory with multiple language files
            files_to_process = list(self.data_path.glob("*.txt"))
            if not files_to_process:
                raise ValueError(f"No .txt files found in directory: {self.data_path}")
        
        for file_path in files_to_process:
            language = self._extract_language_code(file_path)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Split by tab
                    parts = line.split('\t')
                    if len(parts) != 2:
                        print(f"Warning: Skipping malformed line {line_num} in {file_path}: {line}")
                        continue
                    
                    word, ipa_string = parts
                    word = word.strip()
                    
                    # Parse multiple pronunciations
                    pronunciations = self._parse_ipa_pronunciations(ipa_string)
                    
                    if not pronunciations:
                        print(f"Warning: No valid IPA pronunciations found in line {line_num} of {file_path}: {line}")
                        continue
                    
                    # Create a row for each pronunciation variant
                    for ipa in pronunciations:
                        data_rows.append({
                            'word': word,
                            'ipa': ipa,
                            'language': language
                        })
        
        if not data_rows:
            raise ValueError("No valid data rows found in the dataset")
        
        return pl.DataFrame(data_rows)
    
    def validate_data(self, data: pl.DataFrame) -> dict[str, any]:
        """
        Validate the loaded ipa-dict data.
        
        Args:
            data: The loaded DataFrame
            
        Returns:
            Dictionary with validation results and statistics
        """
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'stats': {}
        }
        
        # Check required columns
        required_columns = {'word', 'ipa', 'language'}
        missing_columns = required_columns - set(data.columns)
        if missing_columns:
            validation_results['is_valid'] = False
            validation_results['errors'].append(f"Missing required columns: {missing_columns}")
        
        if not validation_results['is_valid']:
            return validation_results
        
        # Basic statistics
        validation_results['stats'] = {
            'total_entries': len(data),
            'unique_words': data['word'].n_unique(),
            'unique_languages': data['language'].n_unique(),
            'languages': data['language'].unique().to_list(),
            'avg_word_length': data['word'].str.len_chars().mean(),
            'avg_ipa_length': data['ipa'].str.len_chars().mean()
        }
        
        # Check for empty values
        empty_words = data.filter(pl.col('word').str.strip_chars() == "").height
        empty_ipa = data.filter(pl.col('ipa').str.strip_chars() == "").height
        
        if empty_words > 0:
            validation_results['warnings'].append(f"{empty_words} entries have empty words")
        if empty_ipa > 0:
            validation_results['warnings'].append(f"{empty_ipa} entries have empty IPA")
        
        # Check IPA character validity (basic check for common IPA characters)
        ipa_chars = set(''.join(data['ipa'].to_list()))
        common_ipa_chars = set('abcdefghijklmnopqrstuvwxyzɑæɒɔəɛɪɯɵʉʊʌʏaeiouɐɜɞɘɚɤɞɨʉʊyøœɶɑɒɓɗɖɢɠɡɦɥɧʜɲɴŋɳɸɥɰɹʀʁɬɭʃʧʤʒʑʐʝʎʟʢʡʘǀǃǁǂɱɸβfvθðszʃʒʂʐçʝɣχħʜʕɦʔʡʢˈˌːˑ̟̠̥̤̰̯̮̪̺̻̼̃̊̄̀́̂̌̊̃')
        unusual_chars = ipa_chars - common_ipa_chars
        if unusual_chars:
            validation_results['warnings'].append(f"Found unusual characters in IPA: {unusual_chars}")
        
        return validation_results
    
    def get_language_files(self) -> list[Path]:
        """
        Get list of available language files in the data directory.
        
        Returns:
            List of .txt file paths
        """
        if self.data_path.is_file():
            return [self.data_path]
        else:
            return list(self.data_path.glob("*.txt"))
    
    def get_available_languages(self) -> list[str]:
        """
        Get list of available language codes.
        
        Returns:
            List of language codes based on filenames
        """
        files = self.get_language_files()
        return [self._extract_language_code(f) for f in files]