import time
import random
import collections

#: Epoch for simpleflake timestamps, starts at the year 2000
SIMPLEFLAKE_EPOCH = 946702800

# field lengths in bits
SIMPLEFLAKE_TIMESTAMP_LENGTH = 41
SIMPLEFLAKE_RANDOM_LENGTH = (64 - SIMPLEFLAKE_TIMESTAMP_LENGTH)

# left shift amounts
SIMPLEFLAKE_RANDOM_SHIFT = 0
SIMPLEFLAKE_TIMESTAMP_SHIFT = SIMPLEFLAKE_RANDOM_LENGTH

# consistent hashing
SIMPLEFLAKE_CONSISTENT_HASH_LENGTH = 12  # low-order bits of SIMPLEFLAKE_RANDOM_LENGTH
SIMPLEFLAKE_CONSISTENT_HASH_MASK = ((1 << SIMPLEFLAKE_CONSISTENT_HASH_LENGTH) - 1)


simpleflake_struct = collections.namedtuple("SimpleFlake",
                                            ["timestamp", "random_bits"])

# ===================== Utility ====================


def pad_bytes_to_64(string):
    return format(string, "064b")


def binary(num, padding=True):
    """Show binary digits of a number, pads to 64 bits unless specified."""
    binary_digits = "{0:b}".format(int(num))
    if not padding:
        return binary_digits
    return pad_bytes_to_64(int(num))


def extract_bits(data, shift, length):
    """Extract a portion of a bit string. Similar to substr()."""
    bitmask = ((1 << length) - 1) << shift
    return ((data & bitmask) >> shift)

# ==================================================


def simpleflake(timestamp=None, random_bits=None, epoch=SIMPLEFLAKE_EPOCH):
    """Generate a 64 bit, roughly-ordered, globally-unique ID."""
    second_time = timestamp if timestamp is not None else time.time()
    second_time -= epoch
    millisecond_time = int(second_time * 1000)
    randomness = (random_bits if random_bits is not None
                  else random.SystemRandom().getrandbits(SIMPLEFLAKE_RANDOM_LENGTH))
    flake = (millisecond_time << SIMPLEFLAKE_TIMESTAMP_SHIFT) + randomness
    return flake


def parse_simpleflake(flake):
    """Parses a simpleflake and returns a named tuple with the parts."""
    timestamp = SIMPLEFLAKE_EPOCH\
        + extract_bits(flake,
                       SIMPLEFLAKE_TIMESTAMP_SHIFT,
                       SIMPLEFLAKE_TIMESTAMP_LENGTH) / 1000.0
    random = extract_bits(flake,
                          SIMPLEFLAKE_RANDOM_SHIFT,
                          SIMPLEFLAKE_RANDOM_LENGTH)
    return simpleflake_struct(timestamp, random)

def consistent_hash_id(flake):
    """Extract a consistent-hash id from `flake`."""
    return (flake & SIMPLEFLAKE_CONSISTENT_HASH_MASK)

def consistentflake(flake):
    """Generate a new simpleflake with same consistent-hash id as `flake`."""
    new_flake = simpleflake()
    new_flake &= ~SIMPLEFLAKE_CONSISTENT_HASH_MASK
    new_flake |= consistent_hash_id(flake)
    return new_flake
