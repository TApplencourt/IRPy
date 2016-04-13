![](https://zippy.gfycat.com/SarcasticOpenHedgehog.gif)

#[![PyPi](https://img.shields.io/pypi/v/irpy.svg)](https://pypi.python.org/pypi/irpy) [![TravisCI](https://img.shields.io/travis/TApplencourt/IRPy.svg)]() [![License](https://img.shields.io/pypi/l/irpy.svg)](http://www.wtfpl.net/)


IRPy (pronounce /kəˈθuːluː/) extend the python `property` function in order to support lazy evaluation and mutability of nested properties.
Lazy evaluation of properties are quite common ([Werkzeug](http://werkzeug.pocoo.org/docs/0.11/utils/#werkzeug.utils.cached_property) for example),
but coherence problems can arise if you have inference rule between mutable properties. The aim of this library is to solve this problem.


##Install
- With [pip](https://pip.pypa.io/en/stable/):
```
pip install irpy
```
- With [conda](http://conda.pydata.org/docs/): 
```
conda install -c https://conda.anaconda.org/tapplencourt irpy
```
- Or you can manually add [irpy.py](https://raw.githubusercontent.com/TApplencourt/IRPy/master/irpy.py) to `PYTHONPATH` 

##Usage

- `lazy_property`: a simple lazy property;
- `lazy_property_mutable`: this property can change. When doing so, all these ancestors are invalided, they will be recomputed when needed. Futhermore, all these descendant are now unattainable;
- `lazy_property_leaf(mutable,immutable)`: this function allow the creating of node from values defined in the `__init__` class method.

## But why? Or *What is a scientific code*?
A program is a function of its input data:
```
output = program (input)
```
A program can be represented as a production tree where
- The root is the output;
- The leaves are the input data; 
- The nodes are the intermediate variables;
- The edges represent the relation needs/needed by.

In python, this way of thinking is encouraged by the usage of nested, special object, `property`. Indeed each `property` are one nodes of the production tree, and by nested then you define the edges. 

For example:
```python
class NotTrivialFunction(object):
    '''Compute : t(u(d1,d2),v(d3,d4),w(d5))
    where:
        t(x,y) = x + y + 4
        u(x,y) = x + y + 1
        v(x,y) = x + y + 2
        w(x)   = x + 3
    and d1, d2, d3, d3, d5 are the parameters'''

    def __init__(self, d1, d2, d3, d4, d5):
        self.d1 = d1
        self.d2 = d2
        self.d3 = d3
        self.d4 = d4
        self.d5 = d5

    @properpty
    def t(self):
        return self.u1 + self.v + 4

    @properpty
    def u1(self):
        return self.fu(self.d1, self.d2)

    @properpty
    def v(self):
        return self.u2 + self.w + 2

    @properpty
    def u2(self):
        return self.fu(self.d3, self.d4)

    @properpty
    def w(self):
        return self.d5 + 3

    def fu(self, x, y):
        return x + y + 1

```

In this example `d[1,5]`,`u[1,2]`,`v`,`w`,`t` are the node of the production tree. One can see that these properties have no explicit parameter 
(in fact, IRPy mean [**I**mplicit **R**eference **P**arameter](http://osp.chickenkiller.com/mediawiki/index.php?title=IRP) for P**y**thon).

This simplify dramatically simplify program development. Indeed:
- The global production tree is not known by the programmer, the programmer doesn’t handle the execution sequence. Just ask a property, it will be computed on the fly:
```python
f = NotTrivialFunction(d1=1, d2=5, d3=8, d4=10, d=7)
assert (f.t == 42)
```
- The program is easy to write (adding a new `property` only require to know about the name of theses implicit parameters); 
- Any change of dependencies will be handled properly automatically.


But, the same data will be re computed multiple times. A simple solution is to use lazy evaluation of these nodes/properties. Just use `property_lazy` for doing so 
(all these exemple can be found in the [exemple](https://github.com/TApplencourt/IRPy/blob/master/exemple.py) file).

```python
class NotTrivialFunction(object):
    '''Compute : t(u(d1,d2),v(d3,d4),w(d5))
    where:
        t(x,y) = x + y + 4
        u(x,y) = x + y + 1
        v(x,y) = x + y + 2
        w(x)   = x + 3
    and d1, d2, d3, d3, d5 are the parameters'''

    @lazy_property_leaves(immutables="d1 d2 d3 d4 d5".split())
    def __init__(self, d1, d2, d3, d4, d5):
        self.d1 = d1
        self.d2 = d2
        self.d3 = d3
        self.d4 = d4
        self.d5 = d5

    @lazy_property
    def t(self):
        return self.u1 + self.v + 4

    @lazy_property
    def u1(self):
        return self.fu(self.d1, self.d2)

    @lazy_property
    def v(self):
        return self.u2 + self.w + 2

    @lazy_property
    def u2(self):
        return self.fu(self.d3, self.d4)

    @lazy_property
    def w(self):
        return self.d5 + 3

    def fu(self, x, y):
        return x + y + 1
```
In this IRP paradigm as in `irppy.py` node are by default immutable. This mean that you cannot set these node by hand. The only way to compute a node is by using the function who have be decorated. 
For example:

```python
f = NotTrivialFunction(d1=1, d2=5, d3=8, d4=10,d5=7)
f.u1 = 2
```
Will raise an error.


##Tricky part: Mutability

In the precedant example, all the node of the production tree are immutable. In a real world application this a quite a limitation.
For example, in an iterative resolution procedure of an equation (Newton-Raphson), we need to change some node (x <- x - f(x)/f'(x) ) and recompute another accordingly (f(x) and f'(x)) if we ask them again.

This is the essential innovation of IRPy. Use the`lazy_property_mutable` and the `lazy_property_leavs(mutables)` functions too define theses mutable nodes.

Lets use these decorators to write a simple Newton-Raphson algorithm to solve cos x - x = 0.
```python
class NewtonRaphson(object):
    '''Solve cos x - x = 0 by Newton Rapshon's algorithm'''

    @irp_leaves_mutables("x")
    def __init__(self,x):
        self.x = x        

    @irp_node_mutable
    def f(self):
        return cos(self.x) - self.x

    @irp_node_mutable
    def fprime(self):
        return -sin(self.x) - 1

    @irp_node_mutable
    def x_next(self):
        return self.x - self.f / self.fprime

    def solve(self):
        while abs(self.x - self.x_next) > 1.e-9:
            self.x = self.x_next
```

See how in the `solve` function, when we modify `x` it change the value of `x_next(x,f(x),f'(x))` accordingly. At anytime, any where you can be sure that all your production tree are in valid state!

