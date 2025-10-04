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
    
    def _parse_ipa_pronunciations(self, ipa_string: str) -> str:
        """
        Parse IPA pronunciation string and extract the last pronunciation.

        Args:
            ipa_string: Raw IPA string from the file (e.g., "/həˈloʊ/, /hɛˈloʊ/")

        Returns:
            The last IPA pronunciation without slashes, or empty string if none found
        """
        # Find all IPA pronunciations enclosed in forward slashes
        ipa_pattern = r'/([^/]+)/'
        matches = re.findall(ipa_pattern, ipa_string.strip())

        if matches:
            # Return the last pronunciation, cleaned up
            return matches[-1].strip()

        return ""
    
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

                    # Parse pronunciation (last one if multiple)
                    ipa = self._parse_ipa_pronunciations(ipa_string)

                    if not ipa:
                        print(f"Warning: No valid IPA pronunciation found in line {line_num} of {file_path}: {line}")
                        continue

                    # Create a row for the pronunciation
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
        
        # Check IPA character validity (comprehensive check for IPA characters)
        ipa_chars = set(''.join(data['ipa'].to_list()))
        common_ipa_chars = set(
            # Basic Latin alphabet
            'abcdefghijklmnopqrstuvwxyz'
            # Vowels
            '\u0251\u00e6\u0252\u0254\u0259\u025b\u026a\u026f\u0275\u0289\u028a\u028c\u028f'  # ɑæɒɔəɛɪɯɵʉʊʌʏ
            'aeiou'
            '\u0250\u025c\u025e\u0258\u025a\u0264\u0268y\u00f8\u0153\u0276'  # ɐɜɞɘɚɤɨyøœɶ
            # Consonants (pulmonic)
            '\u0253\u0257\u0256\u0262\u0260\u0261\u0266\u0265\u0267\u029c\u0272\u0274\u014b\u0273\u0278\u0270\u0279\u0280\u0281\u026c\u026d\u0283\u02a7\u02a4\u0292\u0291\u0290\u029d\u028e\u029f\u02a2\u02a1\u0271\u03b2fv\u03b8\u00f0sz\u0282\u00e7\u0263\u03c7\u0127\u0295\u0294'  # ɓɗɖɢɠɡɦɥɧʜɲɴŋɳɸɰɹʀʁɬɭʃʧʤʒʑʐʝʎʟʢʡɱβfvθðszʂçɣχħʕʔ
            # Consonants (additional)
            '\u026b'  # ɫ velarized l
            '\u027a'  # ɺ alveolar lateral flap
            '\u027e'  # ɾ alveolar tap
            '\u0288'  # ʈ retroflex stop
            '\u0299'  # ʙ bilabial trill
            '\u0255'  # ɕ alveolo-palatal fricative
            '\u028b'  # ʋ labiodental approximant
            # Vowels (nasalized and modified)
            '\u00e3\u00f5\u0129\u0169\u1ebd'  # ãõĩũẽ nasalized vowels
            '\u012d'  # ĭ non-syllabic
            # Clicks
            '\u0298\u01c0\u01c3\u01c1\u01c2'  # ʘǀǃǁǂ
            # Suprasegmentals and stress
            '\u02c8\u02cc'  # ˈˌ primary and secondary stress
            '\u02d0\u02d1'  # ːˑ length marks (long, half-long)
            # Diacritics (combining characters)
            '\u0329'  # ̩ syllabic
            '\u0306'  # ̆ extra-short
            '\u031d'  # ̝ raised
            '\u031e'  # ̞ lowered
            '\u031a'  # ̚ no audible release
            '\u030d'  # ̍ syllabic (alternative)
            '\u031f\u0320'  # ̟̠ advanced, retracted
            '\u0325\u0324'  # ̥̤ voiceless, breathy voiced
            '\u0330'  # ̰ creaky voiced
            '\u032f'  # ̯ non-syllabic
            '\u032e'  # ̮ derhoticized
            '\u032a'  # ̪ dental
            '\u033a\u033b\u033c'  # ̺̻̼ apical, laminal, linguolabial
            '\u0303'  # ̃ nasalized
            '\u030a'  # ̊ voiceless (ring above)
            '\u0304'  # ̄ mid-level tone
            '\u0300\u0301\u0302'  # ̀́̂ tone marks (grave, acute, circumflex)
            '\u030c'  # ̌ rising tone
            '\u0311'  # ̑ stress/tone mark
            # Suprasegmental modifiers
            '\u02e0'  # ˠ velarized
            '\u02b0'  # ʰ aspirated
            '\u02b2'  # ʲ palatalized
            '\u02b6'  # ʶ pharyngealized
            '\u02b7'  # ʷ labialized
            '\u0361'  # ͡ tie bar (for affricates and double articulation)
            # Prosodic marks
            '.'  # syllable break
            '|\u2016'  # |‖ minor and major prosodic breaks
            '\u2197\u2198'  # ↗↘ rising and falling intonation
            '\u203f\u2040'  # ‿⁀ linking marks
            # Spacing
            ' '  # space
            ','  # pause/separator
        )
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