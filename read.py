from pathlib import Path

import numpy as np

import converter as c

BYTE_SIZE = 8
PADDING_CHUNK = 3
OCCURRENCE_CHUNK = 32


def read_bits(file_path: Path) -> np.ndarray:
    """Read bytes from file and convert to array of bits."""
    bit_string = list()
    with open(file_path, 'rb') as file:
        file_bytes = file.read()
        for byte in file_bytes:
            bit_string.append(f'{byte:08b}')
    bit_string = ''.join(bit_string)
    return c.bit_string_to_array(bit_string)


def separate_encoded_message(bits: np.ndarray|str) -> tuple:
    """
    Get order, orccurrence dictionary and encoded message.
    
    The order refers to the order of Markov used when encoding the
    message. The occurrence dictionary refers to the amount of times
    a particular sequence of (order) bits has appeared in the message
    plus one. The encoded message is the message compressed by the
    arithmetic coding algorithm.
    """
    if isinstance(bits, str):
        bits = c.bit_string_to_array(bits)
    padding_number = c.bit_array_to_int(bits[0:PADDING_CHUNK])
    markov_order = c.bit_array_to_int(bits[PADDING_CHUNK:BYTE_SIZE])
    occurrence_dict = dict()
    for i in range(2**(markov_order+1)):
        start_index = OCCURRENCE_CHUNK*i+BYTE_SIZE
        end_index = OCCURRENCE_CHUNK*(i+1)+BYTE_SIZE
        occurrence_bytes = bits[start_index:end_index]
        occurrence = f'{i:0{markov_order+1}b}'
        occurrence_dict[occurrence] = c.bit_array_to_int(occurrence_bytes)
    if padding_number:
        encoded_message = bits[end_index:-padding_number]
    else:
        encoded_message = bits[end_index:]
    return markov_order, occurrence_dict, encoded_message
