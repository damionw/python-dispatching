Dispatching
===========

This is `dispatching`, an implementation of multiple dispatch function
prototypes for python.

#### What is multiple dispatch ?
Multiple dispatch is a subclass of polymorphism, where multiple
implementations of the same function with the same name can exist
within the same namespace, differentiated only by the number of
parameters and their types.

This implementation also allows parameter values to be used as
differentiating characteristics, a la Erlang function parameter
pattern matching.

When the function name is invoked, an appropriate instance is
selected according to its parameter signature.

#### Why is this useful ?
Glad you asked.

This makes logic much simpler to understand. Complex layers of
conditional expressions and data validation are removed from
view. Plus, the coder doesn't have to write any of it

#### Installation:
1. git clone https://github.com/damionw/python-dispatching
2. python setup.py install

#### Examples:
Look at the files in the distribution's examples directory
