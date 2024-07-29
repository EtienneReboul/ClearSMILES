""" Test the function for the generate clearSMiles function 
"""
from pathlib import Path
import sys
import re
import pytest
import numpy as np

# make the relative import properly
parent_path = Path(__file__).resolve().parents[1]
print(parent_path)
sys.path.insert(0, f"{parent_path}/")
from features.generate_clearsmiles import find_biggest_digits, get_semantic_mem_map


def test_a_find_biggest_digits():
    """test if the function output int as it should
    """


    # acetic acid
    smiles_no_digits = "CC(=O)O"  # No digits in the string
    assert isinstance(find_biggest_digits(smiles_no_digits),int)

    # aspirin
    smiles_1_digit = "CC(=O)OC1=CC=CC=C1C(=O)O"
    assert isinstance(find_biggest_digits(smiles_1_digit),int)

def test_b_find_biggest_digits():
    """test if the function that find the max digit function properly 
    """
    # imatinib
    smiles = "CC1=C(C=C(C=C1)NC(=O)C2=CC=C(C=C2)CN3CCN(CC3)C)NC4=NC=CC(=N4)C5=CN=CC=C5"
    assert find_biggest_digits(smiles) == 5

    # acetic acid
    smiles_no_digits = "CC(=O)O"  # No digits in the string
    assert find_biggest_digits(smiles_no_digits) == 0

    # aspirin
    smiles_1_digit = "CC(=O)OC1=CC=CC=C1C(=O)O"
    assert find_biggest_digits(smiles_1_digit) == 1


def test_semantic_mem_map():
    """
    test semantic map 
    """
    # declare local variables
    smiles_tokens_regex = r"(\[[^\]]+]|Br?|Cl?|N|O|S|P|F|I|b|c|n|o|s|p|\(|\)|\.|=|#|"
    smiles_tokens_regex += r"-|\+|\\\\|\/|_|:|~|@|\?|>|\*|\$|\%[0-9]{2}|[0-9])"
    smiles_regex = re.compile(smiles_tokens_regex)

    # imatinib
    smiles = "CC1=C(C=C(C=C1)NC(=O)C2=CC=C(C=C2)CN3CCN(CC3)C)NC4=NC=CC(=N4)C5=CN=CC=C5"
    excepted_array = np.array([0, 0, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 2, 1, 1, 1, 2, 2, 2, 1, 1,
                              2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 2, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 2,
                              1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 1, 0, 0, 1, 1, 1, 1,
                              1, 1, 1, 1, 1, 0])
    test_array = get_semantic_mem_map(smiles, smiles_regex)
    assert np.array_equal(
        test_array, excepted_array), "failed to generate semantic memmap for imatinib smiles"

    # acetic acid
    smiles_no_digits = "CC(=O)O"  # No digits in the string
    excepted_array = np.array([0, 0, 1, 1, 1,0,0])
    test_array= get_semantic_mem_map(smiles_no_digits, smiles_regex)
    assert np.array_equal(
        test_array, excepted_array), "failed to generate semantic memmap for acetic acid smiles"

    # aspirin
    smiles_1_digit = "CC(=O)OC1=CC=CC=C1C(=O)O"
    excepted_array= np.array([0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1,
       0, 0])
    test_array=get_semantic_mem_map(smiles_1_digit,smiles_regex)
    assert np.array_equal(
        test_array, excepted_array), "failed to generate semantic memmap for aspirin smiles"


if __name__ == "__main__":
    pytest.main()
