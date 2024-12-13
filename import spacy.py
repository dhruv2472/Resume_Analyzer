import spacy
import spacy.util

# Print current data path
print("Current spaCy data path:", spacy.util.get_data_path())

# Set a default data path if not set
default_data_path = spacy.util.get_data_path()
print("Default data path:", default_data_path)