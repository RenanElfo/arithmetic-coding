from json import dumps
from pathlib import Path

from encode import encoded_bytes


def main():
    how_compressed = dict()
    for i in range(1, 5):
        file_string = f'modelo{i}.dat'
        data_path = Path(file_string)
        how_compressed[file_string] = dict()
        for order in range(4):
            how_compressed[file_string][order] = len(encoded_bytes(order, data_path))*8
    print(how_compressed)
    with open(r'relas.json', 'w') as file:
        file.write(dumps(how_compressed))


if __name__ == '__main__':
    main()