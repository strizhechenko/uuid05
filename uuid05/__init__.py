from base64 import b64encode
from time import time
import os

day = 86400
disable_cache = False


worker_id = os.getpid()
if worker_id == 1:  # prevent collisions while running in multiple containers
    import socket
    hostname = socket.gethostname()
    worker_id = ord(hostname[0]) + ord(hostname[-1])


class UUID05(int):
    previous_values = dict()

    def as_b64(self, *args, **kwargs) -> str:
        """
        If you're using uuid05 results as strings and want it to be more compact, and being integer or not
        doesn't matter you may use this function to encode it to base64. You can transparently pass
        arguments of b64encode function here. As there's not decoding assumed padding symbols are removed.
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
        :arg workers - count of hosts in a system;
        :arg ttl - how many seconds a temporary object lives in a system (maximum) before being deleted;
        :arg precision (optional) - you can override (increase) a precision if objects are created frequently (max - 6);
        >>> assert UUID05.make(2, 3600) <= 132400
        >>> assert UUID05.make(10, 3600) <= 932400
        >>> assert UUID05.make(10, 3600, precision=2) <= 9356400
        >>> assert UUID05.make(10, 2 * 86400) <= 91555200
        >>> assert UUID05.make(16, 3600) <= 15356400
        >>> assert UUID05.make(16, 1800) <= 15178200
        >>> assert UUID05.make() != UUID05.make()
        """
        precision = min(6, precision or int(workers ** (1 / 4)))
        run_id = worker_id % (workers - 1)
        now = time()
        time_id = int((now % ttl) * 10 ** precision)
        result = UUID05(f'{run_id}{time_id}')

        if disable_cache:
            return result

        if (previous := cls.previous_values.get((workers, ttl, precision))) is None:
            cls.previous_values[(workers, ttl, precision)] = result, now
            return result

        value, calculated_at = previous
        # value < result -> enough time passed since .make() was used in for loop
        # now - calculated_at > ttl / 2 -> such usage is abusing collision preventing mechanism
        if value < result or now - calculated_at > ttl / 2:
            cls.previous_values[(workers, ttl, precision)] = result, now
            return result

        # We're probably called in a cycle. Trying to handle it by incrementing previous value.
        cls.previous_values[(workers, ttl, precision)] = value + 1, now
        return cls.previous_values[(workers, ttl, precision)][0]

    @classmethod
    def max_value(cls, workers=10, ttl=2 * day, precision=0) -> 'UUID05':
        """:returns - maximum value of an uuid05 with given params"""
        precision = min(precision or int(workers ** (1 / 4)), 6)
        run_id = workers - 1
        time_id = ttl * ((10 ** precision) - 1)
        return UUID05(f'{run_id}{time_id}')


if __name__ == '__main__':
    from random import randint
    for _ttl in 3600, 2 * 86400:
        for _workers in 2, 4, 10, 16, 32, 256:
            worker_id = randint(0, _workers)
            example_value = UUID05.make(_workers, _ttl)
            max_value = UUID05.max_value(_workers, _ttl)
            max_in_b64 = max_value.as_b64(altchars=b'-_')
            print(f'| {_ttl} | {_workers} | {worker_id} | {example_value} | {max_value} | {max_in_b64} |')
