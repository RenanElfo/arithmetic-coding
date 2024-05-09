from pathlib import Path

import read as r
from mbitlimits import MBitLimits
from converter import bit_string_to_bytes
from occurrences import occurrence_dict_from_sequence

ORDER = 0
ENCODED_PATH = Path(r'encoded_message.txt')


def _header_string(padding_number: int, markov_order: int, occurrence_dict: dict[str, int]) -> str:
    """Generate header string for encoded message."""
    string_list = [f'{padding_number:03b}', f'{markov_order:05b}']
    for i in range(len(occurrence_dict)):
        occurrence = f'{i:0{markov_order+1}b}'
        occurrence_count = occurrence_dict[occurrence]
        string_list.append(f'{occurrence_count:032b}')
    return ''.join(string_list)

def encoded_bytes(markov_order: int, data_path: Path) -> bytes:
    bit_array = r.read_bits(data_path)
    occurrence_dict = occurrence_dict_from_sequence(bit_array, markov_order)
    limits = MBitLimits(markov_order, occurrence_dict)
    encoded_message = limits.encode(bit_array)
    header = _header_string(limits.padding_number, markov_order, occurrence_dict)
    return bit_string_to_bytes(''.join((header, encoded_message)))
