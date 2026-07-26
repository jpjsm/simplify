# base94.py
from blake3 import blake3

ALPHABET = "".join(chr(i) for i in range(33, 127))  # 94 printable ASCII chars
BASE = len(ALPHABET)
CHAR_TO_VAL = {c: i for i, c in enumerate(ALPHABET)}


def encode_base94(data: bytes) -> str:
    """Fully reversible Base94 encoding using big-integer conversion."""
    # Convert bytes → big integer
    num = int.from_bytes(data, "big")

    # Special case: empty or zero
    if num == 0:
        return ALPHABET[0]

    # Convert big integer → Base94 digits
    out = []
    while num > 0:
        num, rem = divmod(num, BASE)
        out.append(ALPHABET[rem])

    return "".join(reversed(out))


def decode_base94(s: str) -> bytes:
    """Decode Base94 string back into bytes."""
    num = 0
    for c in s:
        num = num * BASE + CHAR_TO_VAL[c]

    # Convert big integer → bytes
    # We need to compute the minimum number of bytes required
    byte_len = (num.bit_length() + 7) // 8
    return num.to_bytes(byte_len, "big")


def blake3_128_base91(path: str) -> str:
    # Compute full BLAKE3 hash
    h = blake3(path.encode("utf-8")).digest(length=16)  # 128 bits = 16 bytes

    # Encode using Base91
    return encode_base94(h)


if __name__ == "__main__":
    path1 = "/home/jp/projects/simplify/architecture.md"
    path2 = "/Home/jp/projects/simplify/architecture.md"

    assert path1 != path2
    assert blake3_128_base91(path1) == blake3_128_base91(path1)
    assert blake3_128_base91(path1) != blake3_128_base91(path2)

    print("OK")
