import numpy as np

BYTE_SIZE = 8


def bit_string_to_array(bit_string: str) -> np.ndarray:
    """Convert string of bits into an array."""
    return np.array([int(bit) for bit in bit_string]).astype(np.int8)


def bit_array_to_int(bit_array: np.ndarray) -> int:
    """
    Convert array of bits into integer.

    The array is interpreted as the binary digits of a number which is
    returned as an integer.
    """
    exponents_array = np.arange(bit_array.size - 1, -1, -1)
    powers_of_2_array = 1 << exponents_array
    return int(bit_array.dot(powers_of_2_array))


def bit_array_to_bytes(bit_array: np.ndarray) -> bytes:
    """
    Convert array of bits into their bytes equivalent.
    
    Each group of 8 bits in the array is interpreted as a byte and the
    resulting sequence is returned as bytes type.
    """
    if bit_array.size % BYTE_SIZE != 0:
        raise ValueError('Bit array size is not multiple of 8.')
    byte_array = bit_array.reshape(int(bit_array.size/BYTE_SIZE), BYTE_SIZE)
    byte_array = np.apply_along_axis(bit_array_to_int, axis=1, arr=byte_array)
    byte_list = byte_array.tolist()
    return bytes(byte_list)


def bit_string_to_bytes(bit_string: str) -> bytes:
    """
    Convert string of bits into their bytes equivalent.
    
    Each group of 8 bits in the string is interpreted as a byte and the
    resulting sequence is returned as bytes type.
    """
    bit_array = bit_string_to_array(bit_string)
    return bit_array_to_bytes(bit_array)