import numpy as np

from encode import DATA_PATH


def generate_sequence(size: int, probability_of_zero: float) -> np.ndarray:
    """Generate random sequence of bits."""
    return (np.random.rand(size) > probability_of_zero).astype(np.int8)


def cumulative_dict(ocurrence_dictionary: dict[str, int], markov_order: int) -> dict[str, dict[int, int]]:
    """Create cumulative dictionary from ocurrence dictionary."""
    cumulative_dictionary = dict()
    for i in range(2**markov_order):
        previous_bits = f'{i:0{markov_order}b}'
        cumulative_dictionary[previous_bits] = dict()
        for bit in range(-1, 2):
            if bit == -1:
                cumulative_dictionary[previous_bits][bit] = 0
            else:
                ocurrence_string = ''.join((previous_bits, str(bit)))
                cumulative_dictionary[previous_bits][bit] = cumulative_dictionary[previous_bits][bit-1] + ocurrence_dictionary[ocurrence_string]
    return cumulative_dictionary


def print_file():
    bit_string = []
    with open(DATA_PATH, 'rb') as file:
        file_bytes = file.read()
        for byte in file_bytes:
            bit_string.append(f'{byte:08b}')
    bit_string = ''.join(bit_string)
    print(bit_string)
    print(len(bit_string))


def _read_bytes() -> np.ndarray:
    """Debugging."""
    with open(DATA_PATH, 'rb') as file:
        file_bytes = file.read()
    return file_bytes
