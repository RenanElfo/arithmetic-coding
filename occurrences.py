import numpy as np


def _cut_and_reshape(array: np.ndarray, index: int, markov_order: int) -> np.ndarray:
    """
    Cut the array and reshape it.
    
    Given an index, cut the array at that index such that
    the cut array has a length that is a multiple of one plus
    the order of Markov used in the algorithm. Then reshape
    the array such that each row has the number of elements equal
    to the order plus one.
    """
    order_plus_one = markov_order + 1
    remainder = (array.size%order_plus_one)
    if index - remainder < 0:
        bit_array_cut = array[index:index-remainder]
    elif index - remainder == 0:
        bit_array_cut = array[index:]
    else:
        bit_array_cut = array[index:index-remainder-order_plus_one]
    bit_array_reshaped = bit_array_cut.reshape((bit_array_cut.size//order_plus_one, order_plus_one))
    return bit_array_reshaped


def _initialize_dict(markov_order: int) -> dict[str, int]:
    """Initialize ocurrance dictionary with default values."""
    order_plus_one = markov_order + 1
    occurrence_dictionary = dict()
    for i in range(2**order_plus_one):
        occurrence = f'{i:0{order_plus_one}b}'
        occurrence_dictionary[occurrence] = 1
    return occurrence_dictionary


def _update_ocurrence_dict(unique_tuple: tuple[np.ndarray, np.ndarray], ocurrence_dictionary: dict[str, int]) -> dict[str, int]:
    """Return updated occurrence dictionary."""
    for j in range(unique_tuple[0].shape[0]):
        occurrence = ''.join([str(char) for char in unique_tuple[0][j].tolist()])
        ocurrence_dictionary[occurrence] += unique_tuple[1][j]
    return ocurrence_dictionary


def occurrence_dict_from_sequence(sequence: np.ndarray, markov_order: int) -> dict[str, int]:
    """Obtain occurrence dictionary from sequence of bits."""
    order_plus_one = markov_order + 1
    occurrence_dictionary = _initialize_dict(markov_order)
    for i in range(order_plus_one):
        bit_array_reshaped = _cut_and_reshape(sequence, i, markov_order)
        unique_tuple = np.unique(bit_array_reshaped, axis=0, return_counts=True)
        occurrence_dictionary = _update_ocurrence_dict(unique_tuple, occurrence_dictionary)
    return occurrence_dictionary


def total_count(bits: str, occurrence_dict: dict[str, int]) -> int:
    """
    Return the total count of a string of bits added to the count of
    the same string, except for the last bit, which is complemented.
    """
    previous_bits = bits[:-1]
    string_0 = ''.join((previous_bits, '0'))
    string_1 = ''.join((previous_bits, '1'))
    return occurrence_dict[string_0] + occurrence_dict[string_1]


def _cumulative_count(previous_bits: str, latest_bit: int, occurrence_dict: dict[str, int]) -> int:
    """Return the cumulative count of a particular string of bits."""
    if latest_bit == -1:
        return 0
    bit_string = ''.join((previous_bits, str(latest_bit)))
    if latest_bit:
        return total_count(bit_string, occurrence_dict)
    return occurrence_dict[bit_string]

def cumulative_count_tuple(bits: str, occurrence_dict: dict[str, int]) -> tuple[int]:
    """
    Return the cumulative counts in the numerators of the algorithm.
    
    The first term is the cumulative count of (x-1) and the second term
    is the cumulative count of x, where x is the value of the bit
    obtained.
    """
    cum_count_0 = _cumulative_count(bits[:-1], 0, occurrence_dict)
    if int(bits[-1]):
        cum_count_1 = total_count(bits, occurrence_dict)
        return cum_count_0, cum_count_1
    return 0, cum_count_0
