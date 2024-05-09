import numpy as np

from occurrences import cumulative_count_tuple, total_count
from converter import bit_array_to_int


class MBitLimits:
    """
    Represent the limits of arithmetic coding algorithm and execute it.

    This class keeps track of the upper and lower limits used in the
    implementation for the arithmetic coding and, by doing so, it
    allows for the execution of the algorithm. Other important
    attributes are stored.
    """
    occurrence_dict: dict[str, int]
    e_3_mapping_counter: int
    padding_number: int
    word_length: int
    tag: int
    lower: int
    upper: int
    bits: str
    historic_lower: list[int]
    historic_upper: list[int]

    def __init__(self, markov_order: int, occurrence_dict: dict[str, int]) -> None:
        self.word_length = int(2 + np.ceil(np.log2(sum(occurrence_dict.values()))))
        self.tag = 0
        self.lower = 0
        self.upper = 2**self.word_length - 1
        self.bits = ''.join(['0' for i in range(markov_order+1)])
        self.occurrence_dict = occurrence_dict
        self.e_3_mapping_counter = 0
        self.historic_lower = [self.lower]
        self.historic_upper = [self.upper]

    def __repr__(self) -> str:
        """
        Define representation for MBitLimits when using print().

        Useful mostly for debugging purposes. Doesn't affect how the
        algorithm works.
        """
        lower_string = f'lower = ({self.lower:0{self.word_length}b})₂'
        upper_string = f'upper = ({self.upper:0{self.word_length}b})₂'
        bits = f'bits = {self.bits}'
        return ', '.join((lower_string, upper_string, bits))

    @property
    def upper_left_most_bit(self) -> int:
        """Return the left most bit of the upper limit."""
        return self.upper >> (self.word_length-1)

    @property
    def upper_second_left_most_bit(self) -> int:
        """Return the second left most bit of the upper limit."""
        return (self.upper >> (self.word_length-2)) - (self.upper_left_most_bit << 1)

    @property
    def lower_left_most_bit(self) -> int:
        """Return the left most bit of the lower limit."""
        return self.lower >> (self.word_length-1)

    @property
    def lower_second_left_most_bit(self) -> int:
        """Return the second left most bit of the lower limit."""
        return (self.lower >> (self.word_length-2)) - (self.lower_left_most_bit << 1)

    def _get_bit(self, bit: int|str|np.integer) -> None:
        """Store value of bit while updating limits."""
        self.bits = ''.join((self.bits[1:], str(bit)))
        self._update_limits()

    def _decode_bit(self) -> int:
        """Decode a bit given tag while updating limits."""
        tag_factor = self.tag - self.lower + 1
        upper_factor = self.upper - self.lower + 1
        numerator = tag_factor*total_count(self.bits, self.occurrence_dict) - 1
        value_to_compare = numerator//upper_factor
        previous_bits = self.bits[1:]
        cum_tuple_string = ''.join((previous_bits, '1'))
        cum_count_0, _ = cumulative_count_tuple(cum_tuple_string, self.occurrence_dict)
        decoded_bit = 0 if value_to_compare < cum_count_0 else 1
        self._get_bit(decoded_bit)
        return decoded_bit

    def _update_limits(self) -> None:
        """Update the limits values based on last bit received."""
        factor = self.upper - self.lower + 1
        cum_tuple = cumulative_count_tuple(self.bits, self.occurrence_dict)
        denominator = total_count(self.bits, self.occurrence_dict)
        numerator_lower = factor*cum_tuple[0]
        numerator_upper = factor*cum_tuple[1]
        self.upper = self.lower + numerator_upper//denominator - 1
        self.lower = self.lower + numerator_lower//denominator
        self.historic_lower.append(self.lower)
        self.historic_upper.append(self.upper)

    def _shift_limits(self) -> None:
        """
        Shifts limits to the left by one respecting rules.
        
        Uppon shifting to left, the right most bit of the lower limit
        has to be zero and the right most bit of the upper limit has to
        be one.
        """
        self.lower = (self.lower << 1) % 2**self.word_length
        self.upper = (self.upper << 1) % 2**self.word_length + 1

    def _shift_tag(self, bit: int) -> None:
        """
        Shifts limits to the left by one respecting rules.
        
        Uppon shifting to left, the right most bit of the tag has to
        be the next bit of the sequence being decoded.
        """
        self.tag = (self.tag << 1) % 2**self.word_length + bit

    def _complement_left_most_bit(self) -> None:
        """Compliments the left most bit of both limits."""
        self.lower = (self.lower + 2**(self.word_length - 1)) % 2**self.word_length
        self.upper = (self.upper + 2**(self.word_length - 1)) % 2**self.word_length
        self.tag = (self.tag + 2**(self.word_length - 1)) % 2**self.word_length

    def _decide_mapping(self) -> int:
        """
        Return the code for the mapping to be used.

        The three possible mappings are E_1, E_2 and E_3, where
        E_1 is used when both lower and upper limits have left most bit
        equal to zero, E_2 is used when both lower and upper limits have
        left most bit equal to one, and E_3 is used when the lower and
        upper limits have different left most bits, but the second left
        most bits of the lower and upper limits are equal to one and
        zero, respectively.

        The code for each mapping is 1, for E_1; 2, for E_2, 3, for
        E_3; and 0, if no mapping is required.
        """
        if (self.lower_left_most_bit == self.upper_left_most_bit
                and self.lower_left_most_bit == 0):
            return 1
        elif (self.lower_left_most_bit == self.upper_left_most_bit
                and self.lower_left_most_bit == 1):
            return 2
        elif (self.lower_second_left_most_bit == 1
                and self.upper_second_left_most_bit == 0):
            return 3
        else:
            return 0

    def encode(self, bit_array: np.ndarray) -> str:
        """Return encoded message."""
        encoded_message = []
        iteration = 0
        for bit in bit_array:
            self._get_bit(bit)
            if iteration < 20:
                print(f'{bit = }, {self}')
            while self._decide_mapping():
                if self._decide_mapping() == 1 or self._decide_mapping() == 2:
                    if iteration < 20:
                            print(f'ENCODING: Mapping {self._decide_mapping()}', f'{iteration = }', sep='; ')
                    bit = self.lower_left_most_bit
                    encoded_message.append(str(bit))
                    self._shift_limits()
                    for _ in range(self.e_3_mapping_counter):
                        complement = (bit + 1) % 2
                        encoded_message.append(str(complement))
                    self.e_3_mapping_counter = 0
                if self._decide_mapping() == 3:
                    if iteration < 20:
                            print(f'ENCODING: Mapping {self._decide_mapping()}', f'{iteration = }', sep='; ')
                    self._shift_limits()
                    self._complement_left_most_bit()
                    self.e_3_mapping_counter += 1
                if iteration < 20:
                    print(self)
            iteration += 1
        lower_string = f'{self.lower:0{self.word_length}b}'
        encoded_message.append(lower_string[0])
        complement = (int(lower_string) + 1) % 2
        for _ in range(self.e_3_mapping_counter):
            encoded_message.append(str(complement))
        encoded_message.append(lower_string[1:])
        encoded_string = ''.join(encoded_message)
        self.padding_number = (8 - (len(encoded_string) % 8)) % 8
        padding_string = ''.join('0' for i in range(self.padding_number))
        return ''.join((encoded_string, padding_string))

    def decode(self, bit_array: np.ndarray) -> str:
        """Return decoded message."""
        decoded_message = []
        self.tag = bit_array_to_int(bit_array[0:self.word_length])
        array_index = self.word_length
        iteration = 0
        while self.tag != self.lower:
            decoded_message.append(str(self._decode_bit()))
            if iteration < 20:
                print(f'bit = {self.bits[-1]}, {self}')
            try:
                while self._decide_mapping():
                    if self._decide_mapping() == 1 or self._decide_mapping() == 2:
                        if iteration < 20:
                            print(f'DECODING: Mapping {self._decide_mapping()}', f'{iteration = }', sep='; ')
                        self._shift_limits()
                        next_bit = int(bit_array[array_index])
                        array_index += 1
                        self._shift_tag(next_bit)
                    if self._decide_mapping() == 3:
                        if iteration < 20:
                            print(f'DECODING: Mapping {self._decide_mapping()}', f'{iteration = }', sep='; ')
                        self._shift_limits()
                        next_bit = int(bit_array[array_index])
                        array_index += 1
                        self._shift_tag(next_bit)
                        self._complement_left_most_bit()
                    if iteration < 20:
                        print(self)
                iteration += 1
            except IndexError:
                print("Warning: algorithm didn't stop.")
                return ''.join(decoded_message)
        print(f'{iteration = }, {self.tag}, {self.lower}')
        return ''.join(decoded_message)
