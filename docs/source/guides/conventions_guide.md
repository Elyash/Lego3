# Conventions Guide

## General

Our conventions based on [Google Python Conventions](https://google.github.io/styleguide/pyguide.html) with several matches to [Octavius Project](https://github.com/Steven17D/Octavius).

Before continue to read the following conventions, make sure you understand the above Google conventions.

> **Note:** For user convenience we use several tools to force the conventions. 
You can find them in [Conventions tools](../configurations/conventions_linters.md) and under the development of _helpers.

## Special Conventions

### Python 3

#### DocString

Every class and function should have documentation to describe their rule and functionality.

Since we are using static typing in this project, some of the docstring info stays irrelevant so we updated the docstrings:

##### Class

Google Python conventions:

```python
class SampleClass(object):
    """Summary of class here.

    Longer class information...

    Attributes:
        likes_spam (bool): Indicating if we like SPAM or not.
        eggs (int): Count of the eggs we have laid.
    """
```

Lego 3 conventions:

```python
class SampleClass(object):
    """Summary of class here.

    Longer class information...

    Attributes:
        likes_spam: Indicating if we like SPAM or not.
        eggs: Count of the eggs we have laid.
    """

    likes_spam: bool
    eggs: int
```

##### function

Google Python conventions:

```python
def fetch_bigtable_rows(big_table, keys, other_silly_variable=None):
    """Fetches rows from a Bigtable.

    Retrieves rows pertaining to the given keys from the Table instance represented by big_table. Silly things may happen if other_silly_variable is not None.

    Args:
        big_table(BigTable): An open Table instance.
        keys(Tuple(str)): A sequence of keys of each table row to fetch.
        other_silly_variable (int, None): Another optional variable, that has a much longer name
            than the other args, and which does nothing.

    Returns:
        dict(str: tuple(str)): A mapping keys to the corresponding table row data fetched. Each row
            is represented as a tuple of strings. For example:
            {'Serak': ('Rigel VII', 'Preparer'),
            'Zim': ('Irk', 'Invader'),
            'Lrrr': ('Omicron Persei 8', 'Emperor')}

        If a key from the keys argument is missing from the dictionary, then that row was not found in the table.

    Raises:
        IOError: An error occurred accessing the bigtable.Table object.
    """
    ...
```

Lego 3 conventions:

```python

def fetch_bigtable_rows(
        big_table: BigTable,
        keys: Tuple[str],
        other_silly_variable: Optional[int] = None
    ) -> Dict[str, Tuple[str]]:
    """Fetches rows from a Bigtable.

    Retrieves rows pertaining to the given keys from the Table instance represented by big_table. Silly things may happen if other_silly_variable is not None.

    Args:
        big_table: An open Table instance.
        keys: A sequence of keys of each table row to fetch.
        other_silly_variable: Another optional variable, that has a much longer name than the
            other args, and which does nothing.

    Returns:
        A mapping keys to the corresponding table row data fetched. Each row is represented as a tuple
            of strings. For example:
            {'Serak': ('Rigel VII', 'Preparer'),
            'Zim': ('Irk', 'Invader'),
            'Lrrr': ('Omicron Persei 8', 'Emperor')}

    If a key from the keys argument is missing from the dictionary, then that row was not found in the table.

    Raises:
        IOError: An error occurred accessing the bigtable.Table object.
    """
    ...
```

#### Function Signature

Since the function's signature needs to contain the typing information also, we decide to change the signature conventions as follows.

Notice the change required just in a long function signature, in other cases you can leave the function signature the same as Google conventions.

Google Python conventions:

```python
def drive(vehicle: Vehicle, source: str, destination: str,
          speed: float = 50, stops: int = 0, seats: int = 10,
          shoule_document: bool = True) -> None:
    ...
```

Lego 3 conventions:

```python
def drive(
        vehicle: Vehicle,
        source: str,
        destination: str,
        speed: float = 50.0,
        stops: int = 0,
        seats: int = 10,
        should_document: bool = True
    ) -> None:
    ...
```

#### Variables Declaration Order

Google Python conventions not mentioned any convention describes the order of the variables declared in function or class.

In Lego 3 project we decided to enforce a convention to better-looking code.  

**The variables declaration both in function and class should be ordered by their declaration length (i.e. the first declaration is the shortest one, and the last is the longest one).**

For example:

```python
# The following declarations not match the convention.
def bad():
    my_socket = socket.socket()
    socket_index = 1
    favorite_repo = 'Lego 3'

# The following declarations match the convention.
def good():
    socket_index = 1
    favorite_repo = 'Lego 3'
    my_socket = socket.socket()
```

### Typing

In Lego 3 project we force the developer to use static typing for the following reasons:  

* It helps catch bugs in development time.
* It helps develop this integrated project since the API of the functions is more stable.
* It helps read and understand the code.

Most of the relevant needed typing knowledge can be found in [typing documentation](https://docs.python.org/3/library/typing.html).

### RPyC

RPyC used commonly in Lego 3 project and by our experience, it is important to distinguish between remote and local objects and functions.

To do so, we force the following convention:

**A variable name of variable contains remote object or function should start with an `r_` (or `R_` for constants).**

For example:

```python
# Local variables
send = socker.send
AF_INET = socket.AF_INET

# Remote variables
R_AF_INET = connection.modules['socket'].AF_INET
r_send = connection.modules['socket'].send
```
