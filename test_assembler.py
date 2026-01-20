import pytest
import os
import subprocess

INPUT_DIR = './input'
OUTPUT_DIR = './output'
GOLDEN_DIR = './golden'

def get_test_files():
    if not os.path.exists(INPUT_DIR):
        return []
    return [f for f in os.listdir(INPUT_DIR) if f.endswith('.txt')]

@pytest.fixture(scope="session", autouse=True)
def setup_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def preprocess_lines(file_path, mode='text'):
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'r', encoding='utf-8') as f:
        if mode == 'text':
            return [" ".join(l.split()).upper() for l in f.readlines() if l.strip()]
        else:
            return [l.strip().upper() for l in f.readlines() if l.strip()]

# ---------------------------------------------------------
# Main test case
# ---------------------------------------------------------
@pytest.mark.parametrize("file_name", get_test_files())
def test_assembler_regression(file_name):
    file_basename = os.path.splitext(file_name)[0]
    input_path = os.path.join(INPUT_DIR, file_name)
    
    result = subprocess.run(['python', './assembler.py', input_path, OUTPUT_DIR], capture_output=True, text=True)
    
    assert result.returncode == 0, f"Assembler execution failed: {result.stderr}"

    # compare intermediate
    actual_int_path = os.path.join(OUTPUT_DIR, f"{file_basename}_intermediate.txt")
    golden_int_path = os.path.join(GOLDEN_DIR, f"{file_basename}_intermediate.golden")
    
    golden_int = preprocess_lines(golden_int_path, mode='text')
    actual_int = preprocess_lines(actual_int_path, mode='text')

    if golden_int is not None:
        assert actual_int == golden_int, f"Intermediate file different ({file_name})"

    # compare object
    actual_obj_path = os.path.join(OUTPUT_DIR, f"{file_basename}_object.txt")
    golden_obj_path = os.path.join(GOLDEN_DIR, f"{file_basename}_object.golden")
    
    golden_obj = preprocess_lines(golden_obj_path, mode='object')
    actual_obj = preprocess_lines(actual_obj_path, mode='object')

    if golden_obj is not None:
        assert actual_obj == golden_obj, f"Object file different ({file_name})"