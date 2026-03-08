# https://github.com/brhumphe/jenkins_hash

import numpy as np


def rshift_zero_padded(val, n):
    """Zero-padded right shift"""
    return (val % 0x100000000) >> n


def _mix(a, b, c):
    """
    mix 3 32-bit values reversibly.
    For every delta with one or two bit set, and the deltas of all three
    high bits or all three low bits, whether the original value of a,b,c
    is almost all zero or is uniformly distributed,
    * If mix() is run forward or backward, at least 32 bits in a,b,c
    have at least 1/4 probability of changing.
    * If mix() is run forward, every bit of c will change between 1/3 and
    2/3 of the time.  (Well, 22/100 and 78/100 for some 2-bit deltas.)
    mix() was built out of 36 single-cycle latency instructions in a
    structure that could supported 2x parallelism, like so:
    a -= b;
    a -= c; x = (c>>13);
    b -= c; a ^= x;
    b -= a; x = (a<<8);
    c -= a; b ^= x;
    c -= b; x = (b>>13);
    """

    """  
    # 1st set
    a -= b; a -= c; a ^= (c>>13); 
    b -= c; b -= a; b ^= (a<<8); 
    c -= a; c -= b; c ^= (b>>13); 
    # 2nd set
    a -= b; a -= c; a ^= (c>>12);  
    b -= c; b -= a; b ^= (a<<16); 
    c -= a; c -= b; c ^= (b>>5); 
    # 3rd set
    a -= b; a -= c; a ^= (c>>3);  
    b -= c; b -= a; b ^= (a<<10); 
    c -= a; c -= b; c ^= (b>>15);
    """
    # 1st set
    a -= b
    a -= c
    a ^= (rshift_zero_padded(c, 13))

    b -= c
    b -= a
    b ^= (a << 8)

    c -= a
    c -= b
    c ^= rshift_zero_padded(b, 13)

    # 2nd set
    a -= b
    a -= c
    a ^= rshift_zero_padded(c, 12)

    b -= c
    b -= a
    b ^= a << 16

    c -= a
    c -= b
    c ^= rshift_zero_padded(b, 5)

    # Third set
    a -= b
    a -= c
    a ^= rshift_zero_padded(c, 3)

    b -= c
    b -= a
    b ^= a << 10

    c -= a
    c -= b
    c ^= rshift_zero_padded(b, 15)

    return a, b, c


def _hash(input_data, initVal=0):
    """
    hash() -- hash a variable-length key into a 32-bit value
      k     : the key (the unaligned variable-length array of bytes)
      len   : the length of the key, counting by bytes
      level : can be any 4-byte value
    Returns a 32-bit value.  Every bit of the key affects every bit of
    the return value.  Every 1-bit and 2-bit delta achieves avalanche.
    About 36+6len instructions.
    The best hash table sizes are powers of 2.  There is no need to do
    mod a prime (mod is so slow!).  If you need less than 32 bits,
    use a bitmask.  For example, if you need only 10 bits, do
      h = (h & hashmask(10));
    In which case, the hash table should have hashsize(10) elements.
    If you are hashing n strings (ub1 **)k, do it like this:
      for (i=0, h=0; i<n; ++i) h = hash( k[i], len[i], h);
    By Bob Jenkins, 1996.  bob_jenkins@burtleburtle.net.  You may use this
    code any way you wish, private, educational, or commercial.  It's free.
    See http://burtleburtle.net/bob/hash/evahash.html
    Use for hash table lookup, or anything where one collision in 2^32 is
    acceptable.  Do NOT use for cryptographic purposes.
    """
    data = bytes(input_data, encoding='ascii')
    len_pos = len(data)
    length = len(data)
    if length == 0:
        return 0

    a = 0x9e3779b9
    b = 0x9e3779b9
    c = initVal
    p = 0
    while len_pos >= 12:
        a += ((data[p + 0]) + ((data[p + 1]) << 8) + ((data[p + 2]) << 16) + ((data[p + 3]) << 24))
        b += ((data[p + 4]) + ((data[p + 5]) << 8) + ((data[p + 6]) << 16) + ((data[p + 7]) << 24))
        c += ((data[p + 8]) + ((data[p + 9]) << 8) + ((data[p + 10]) << 16) + ((data[p + 11]) << 24))
        q = _mix(a, b, c)
        a = q[0]
        b = q[1]
        c = q[2]
        p += 12
        len_pos -= 12

    c += length
    if len_pos >= 11:
        c += (data[p + 10]) << 24
    if len_pos >= 10:
        c += (data[p + 9]) << 16
    if len_pos >= 9:
        c += (data[p + 8]) << 8
    # the first byte of c is reserved for the length
    if len_pos >= 8:
        b += (data[p + 7]) << 24
    if len_pos >= 7:
        b += (data[p + 6]) << 16
    if len_pos >= 6:
        b += (data[p + 5]) << 8
    if len_pos >= 5:
        b += (data[p + 4])
    if len_pos >= 4:
        a += (data[p + 3]) << 24
    if len_pos >= 3:
        a += (data[p + 2]) << 16
    if len_pos >= 2:
        a += (data[p + 1]) << 8
    if len_pos >= 1:
        a += (data[p + 0])
    q = _mix(a, b, c)
    a = q[0]
    b = q[1]
    c = q[2]

    return rshift_zero_padded(c, 0)


def lookup2(data: any) -> int:
    """Python implementation of Jenkins hash function lookup2"""
    return _hash(data)


def ooat(key: any) -> int:
    """Python implementation of Jenkins hash one-at-a-time function via numpy"""
    key_hash = 0
    for c in key:
        key_hash += np.int32(ord(c))
        key_hash += np.int32(key_hash) << np.int32(10)
        key_hash = np.int32(key_hash) ^ (np.int32(key_hash) >> np.int32(6))

    key_hash += key_hash << np.int32(3)
    key_hash ^= key_hash >> np.int32(11)  # Don't need to cast key_hash to int32 here I guess
    key_hash += key_hash << np.int32(15)

    return np.uint32(key_hash) >> np.uint32(0)


# [object Object] (unknownlite): modified function ooat to make it unsigned
def ooat_unsigned(key: any) -> int:
    """Python implementation of Jenkins hash one-at-a-time function via numpy"""
    key_hash = 0
    with np.errstate(over='ignore'):
        for c in key:
            key_hash += np.uint32(ord(c))
            key_hash += np.uint32(key_hash) << np.uint32(10)
            key_hash = np.uint32(key_hash) ^ (np.uint32(key_hash) >> np.uint32(6))

        key_hash += key_hash << np.uint32(3)
        key_hash ^= key_hash >> np.uint32(11)  # Don't need to cast key_hash to int32 here I guess
        key_hash += key_hash << np.uint32(15)

    return np.uint32(key_hash) >> np.uint32(0)


if __name__ == "__main__":
    print(ooat_unsigned('corona'))
