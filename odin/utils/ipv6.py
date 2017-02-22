import re
from odin.exceptions import ValidationError


def is_valid_ipv6_address(ip_str):
    """
    Ensure we have a valid IPv6 address.
    Args:
        ip_str: A string, the IPv6 address.
    Returns:
        A boolean, True if this is a valid IPv6 address.
    """
    # Prevent circular imports
    from odin.validators import validate_ipv4_address

    symbols_re = re.compile(r'^[0-9a-fA-F:.]+$')
    if not symbols_re.match(ip_str):
        return False

    # We need to have at least one ':'.
    if ':' not in ip_str:
        return False

    # We can only have one '::' shortener.
    if ip_str.count('::') > 1:
        return False

    # '::' should be encompassed by start, digits or end.
    if ':::' in ip_str:
        return False

    # A single colon can neither start nor end an address.
    if ((ip_str.startswith(':') and not ip_str.startswith('::')) or
            (ip_str.endswith(':') and not ip_str.endswith('::'))):
        return False

    # We can never have more than 7 ':' (1::2:3:4:5:6:7:8 is invalid)
    if ip_str.count(':') > 7:
        return False

    # If we have no concatenation, we need to have 8 fields with 7 ':'.
    if '::' not in ip_str and ip_str.count(':') != 7:
        # We might have an IPv4 mapped address.
        if ip_str.count('.') != 3:
            return False

    ip_str = _explode_shorthand_ip_string(ip_str)

    # Now that we have that all squared away, let's check that each of the
    # hextets are between 0x0 and 0xFFFF.
    for hextet in ip_str.split(':'):
        if hextet.count('.') == 3:
            # If we have an IPv4 mapped address, the IPv4 portion has to
            # be at the end of the IPv6 portion.
            if not ip_str.split(':')[-1] == hextet:
                return False
            try:
                validate_ipv4_address(hextet)
            except ValidationError:
                return False
        else:
            try:
                # a value error here means that we got a bad hextet,
                # something like 0xzzzz
                if int(hextet, 16) < 0x0 or int(hextet, 16) > 0xFFFF:
                    return False
            except ValueError:
                return False
    return True


def _explode_shorthand_ip_string(ip_str):
    """
    Expand a shortened IPv6 address.
    Args:
        ip_str: A string, the IPv6 address.
    Returns:
        A string, the expanded IPv6 address.
    """
    if not _is_shorthand_ip(ip_str):
        # We've already got a longhand ip_str.
        return ip_str

    hextet = ip_str.split('::')

    # If there is a ::, we need to expand it with zeroes
    # to get to 8 hextets - unless there is a dot in the last hextet,
    # meaning we're doing v4-mapping
    if '.' in ip_str.split(':')[-1]:
        fill_to = 7
    else:
        fill_to = 8

    if len(hextet) > 1:
        sep = len(hextet[0].split(':')) + len(hextet[1].split(':'))
        new_ip = hextet[0].split(':')

        for __ in range(fill_to - sep):
            new_ip.append('0000')
        new_ip += hextet[1].split(':')

    else:
        new_ip = ip_str.split(':')

    # Now need to make sure every hextet is 4 lower case characters.
    # If a hextet is < 4 characters, we've got missing leading 0's.
    ret_ip = []
    for hextet in new_ip:
        ret_ip.append(('0' * (4 - len(hextet)) + hextet).lower())
    return ':'.join(ret_ip)


def _is_shorthand_ip(ip_str):
    """Determine if the address is shortened.
    Args:
        ip_str: A string, the IPv6 address.
    Returns:
        A boolean, True if the address is shortened.
    """
    if ip_str.count('::') == 1:
        return True
    if any(len(x) < 4 for x in ip_str.split(':')):
        return True
    return False
