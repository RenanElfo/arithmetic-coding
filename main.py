from pathlib import Path

import numpy as np

import occurrences as oc
import read as r
from mbitlimits import MBitLimits
from encode import _header_string, ORDER, encoded_bytes
from converter import bit_array_to_bytes, bit_string_to_array
#from unused_functions import generate_sequence

DATA_PATH = Path(r'modelo2.dat')


def main():
    #np.random.seed(4)
    bit_array = r.read_bits(DATA_PATH)
    #bit_array = generate_sequence(5, 0.8)
    print(bit_array)
    occurrence_dictionary = oc.occurrence_dict_from_sequence(bit_array, ORDER)
    print(occurrence_dictionary)
    #print(oc.cumulative_count_tuple('0', occurrence_dictionary), oc.total_count('1', occurrence_dictionary))

    limits = MBitLimits(ORDER, occurrence_dictionary)
    encoded_message = limits.encode(bit_array)
    #print(len(encoded_message), len(encoded_message)%8, limits.padding_number)
    print(len(encoded_message))
    print(f'{encoded_message}:', len(encoded_message)//8, 'bytes', f'; Padding bits: {limits.padding_number}')
    print(r'%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')

    header = _header_string(limits.padding_number, ORDER, occurrence_dictionary)
    #print(len(header))
    #compressed = encoded_bytes(ORDER)
    #print(len(compressed))

    order, occurrence_dict, message = r.separate_encoded_message(''.join((header, encoded_message)))
    decode_limits = MBitLimits(order, occurrence_dict)
    decoded_message = decode_limits.decode(message)
    print('Hello World!', decoded_message)
    decoded_array = bit_string_to_array(decoded_message)
    print(len(decoded_message), print(decoded_array))

    # print(decoded_array[:10] == bit_array[:10])
    # for i in limits.historic_lower[9:12]:
    #     print(f'{int(i):0{limits.word_length}b}')
    # print()
    # for i in decode_limits.historic_lower[9:12]:
    #     print(f'{int(i):0{decode_limits.word_length}b}')
    # print()
    # for i in limits.historic_upper[9:12]:
    #     print(f'{int(i):0{limits.word_length}b}')
    # print()
    # for i in decode_limits.historic_upper[9:12]:
    #     print(f'{int(i):0{decode_limits.word_length}b}')

    # historic_lower_enc = np.array(limits.historic_lower)
    # historic_upper_enc = np.array(limits.historic_upper)
    # historic_lower_dec = np.array(decode_limits.historic_lower)
    # historic_upper_dec = np.array(decode_limits.historic_upper)
    # print(historic_lower_dec[9:12] == historic_lower_enc[9:12])
    # print(historic_upper_dec[9:12] == historic_upper_enc[9:12])

    print('Finally:', decoded_array.size, bit_array.size)


if __name__ == '__main__':
    main()
