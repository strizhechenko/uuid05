from base64 import b64encode
from time import time
import os

day = 86400

worker_id = os.getpid()
if worker_id == 1:  # prevent collisions while running in multiple containers
    import socket
    hostname = socket.gethostname()
    worker_id = ord(hostname[0]) + ord(hostname[-1])


class UUID05(int):
    def as_b64(self, *args, **kwargs) -> str:
        """
        If you're using uuid05 results as strings and want it to be more compact, and being integer or not doesn't matter
        you may use this function to encode it to base64. You can transparently pass arguments of b64encode function here.
        As there's not decoding assumed padding symbols are removed.
        %timeit b64(uuid05()) - 2.87 µs ± 13.9 ns per loop @ 3.2GHz
        >>> UUID05(34714).as_b64(altchars=b'_-')
        'h5o'
        >>> UUID05(11402098).as_b64(altchars=b'_-')
        'rfty'
        >>> UUID05(3136979908).as_b64(altchars=b'_-')
        'uvqDxA'
        >>> UUID05(29136919548).as_b64(altchars=b'_-')
        'BsiyG-w'
        """
        uid_as_bytes = self.to_bytes((self.bit_length() + 7) // 8, byteorder='big')
        return b64encode(uid_as_bytes, *args, **kwargs).decode().replace('=', '')

    @classmethod
    def make(cls, workers=10, ttl=2 * day, precision=0) -> 'UUID05':
        """
        Compact human-readable unique identifiers for temporary objects in small non-synchronizing distributed systems.
        If your objects are persistent - you'd better use nanoid.
        If you need to generate multiple UIDs for multiple object at once - generate one and use loop variable as suffix.
        %timeit uuid05() - 2.1 µs ± 2.08 ns per loop @ 3.2GHz
        :arg workers - count of hosts in a system;
        :arg ttl - how many seconds a temporary object lives in a system (maximum) before being deleted;
        :arg precision (optional) - you can override (increase) a precision if objects are created frequently (max - 6);
        >>> assert UUID05.make(2, 3600) <= 132400
        >>> assert UUID05.make(10, 3600) <= 932400
        >>> assert UUID05.make(10, 3600, precision=2) <= 9356400
        >>> assert UUID05.make(10, 2 * 86400) <= 91555200
        >>> assert UUID05.make(16, 3600) <= 15356400
        >>> assert UUID05.make(16, 1800) <= 15178200
        """
        precision = min(6, precision or int(workers ** (1 / 4)))
        run_id = worker_id % (workers - 1)
        time_id = int((time() % ttl) * 10 ** precision)
        return UUID05(f'{run_id}{time_id}')

    @classmethod
    def uuid05_max_value(cls, machines=10, ttl=2 * day, precision=0) -> 'UUID05':
        """:returns - maximum value of an uuid05 with given params"""
        precision = min(precision or int(machines ** (1 / 4)), 6)
        run_id = machines - 1
        time_id = ttl * ((10 ** precision) - 1)
        return UUID05(f'{run_id}{time_id}')


if __name__ == '__main__':
    from random import randint
    for _ttl in 3600, 2 * 86400:
        for _workers in 2, 4, 10, 16, 32, 256:
            worker_id = randint(0, _workers)
            example_value = UUID05.make(_workers, _ttl)
            max_value = UUID05.uuid05_max_value(_workers, _ttl)
            max_in_b64 = max_value.as_b64(altchars=b'-_')
            print(f'| {_ttl} | {_workers} | {worker_id} | {example_value} | {max_value} | {max_in_b64} |')
