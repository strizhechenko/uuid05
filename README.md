**UUID05** - compact human-readable almost unique identifiers for temporary objects
in small non-synchronizing distributed systems.

Well, it's not really unique (that's why 0.5) and collisions are possible
but probability is low and it's probably acceptable.

The library provides you with just 2 functions: `uuid05() -> int` and `int2b64(int) -> str` and have zero dependencies.

**Examples** below explain how it works:

| TTL <br/>(seconds) | Workers | Worker ID | Example value |     Max value | int2b64(max_value) |
|-------------------:|--------:|----------:|--------------:|--------------:|--------------------|
|        (hour) 3600 |       2 |         1 |          9589 |        132400 | AgUw               |
|               3600 |       4 |         2 |         29589 |        332400 | BRJw               |
|               3600 |      10 |         4 |         49589 |        932400 | Djow               |
|               3600 |      16 |         1 |        195893 |      15356400 | 6lHw               |
|               3600 |      32 |        11 |       1195893 |      31356400 | Ad518A             |
|               3600 |     256 |        53 |     539589397 |   25535996400 | BfIQYfA            |
|    (2 days) 172800 |       2 |         1 |       1449589 |      11555200 | sFGA               |
|             172800 |       4 |         2 |      21449589 |      31555200 | AeF-gA             |
|             172800 |      10 |         4 |      41449589 |      91555200 | BXUFgA             |
|             172800 |      16 |         4 |     414495893 |    1517107200 | Wm04AA             |
|             172800 |      32 |        14 |    1414495893 |    3117107200 | uctIAA             |
|             172800 |     256 |       179 | 1791449589397 | 2551727827200 | AlIe1KkA           |

## Installing

``` shell
pip install uuid05
```

## Using

``` python
from uuid05 import uuid05, int2b64

# May be parametrized by workers: int, ttl: int, precision: int
# defaults are: workers=10, ttl=2 days, precision=1
uid: int = uuid05()
suffix: str = int2b64(uid)
object_name: str = f'autotest_object_{suffix}'
```

It can be also used as an utility from command-line:

``` shell
$ uuid05
61503153
$ uuid05 -w 2
1503125
$ uuid05 -t 3600 -w 2
27091
$ uuid05 -b -t 3600 -w 2
aZ8
$ uuid05 -b -w 2
FvN2
$ uuid05 -b
AxHktA
$ uuid --help
```

## When UUID05 is suitable

In E2E/UI-testing. It's slow, and sometimes you need to check a data created by tests _after_ run.

Or, more generally, in staging environments where you aren't sure that your _testing_ system 
will delete data after runs, but _tested_ system is aware of such a data and deletes it after some time.
There's also be multiple testing systems instances running simultaneously, and you don't want them to affect each other.

You also may want identifiers to be more or less rememberable for at least 10-15 seconds while you switching tabs.

Oh, and you _don't_ want to synchronize workers via network.
Otherwise Redis, Memcached or another database with a single INCRementing counter would do the trick.

## When UUID05 isn't suitable

- If your system isn't distributed. Local counter in memory or file will work better.
- If your objects are persistent - you'd better use [py-nanoid](https://github.com/puyuan/py-nanoid). 
- If you need to generate multiple UIDs for multiple object really _quick_:
  - generate one and reuse it, using a semantic or loop variable as a suffix;
  - pass **precision** argument to `uuid05()`. It scales automatically with worker count, but if there are less than 16 workers, default is 1 which means 1 uuid per 0.1 second, usually it's enough.
    - `precision=3` argument will use milliseconds.
    - `precision=6` for microseconds.
  - if `precision=6` is not enough stop trying to make your identifier compact.
- If you believe that semi-persistent data is a testing antipattern, 
  and it should be cleared by testing system before or after each run.

## Development

- Tests are doctests and may be run by `pytest`.
- Documentation - look at code, it's just two files.
