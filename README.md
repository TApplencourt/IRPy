![](https://zippy.gfycat.com/SarcasticOpenHedgehog.gif)

IRPy (pronounce /kəˈθuːluː/) extend the python `property` function in orderto support lazy evaluation.

##Install
- With [pip](https://pip.pypa.io/en/stable/):
```
pip install irpy
```
- With [conda](http://conda.pydata.org/docs/): 
```
conda install -c https://conda.anaconda.org/tapplencourt irpy
```
- Or you can manualy add `irpy.py` to `PYTHONPATH` 


## What is a scientific code?
A program is a function of its input data:
```
output = program (input)
```
A program can be represented as a production tree where
- The root is the output 
- The leaves are the input data 
- The nodes are the intermediate variables 
- The edges represent the relation needs/needed by.

In python we can use the special `property` function to access and compute the node. For example:

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

In this example `d[1,5]`,`u[1,2]`,`v`,`w`,`t` are the node of the production tree. One can see that these properties have no explicits parameter (in fact, IRPy mean **I**mplicit **R**eference **P**arameter for P**y**thon \[0\])!

This simplify dramaticaly the workflow. Indeed:
- The global production tree is not known by the programmer ;  The programmer doesn’t handle the execution sequence
- The program is easy to write (adding a new `property` only require to know about the name of this implicit parameter) 
- Any change of dependencies will be handled properly automatically!

But: The same data will be re computed multiple times. 
- Simple solution: Lazy evaluation using memo functions! 
Doing this, using the `irpy` library is really easy. Only replace the `property` function by `irp_node` one and it will work.

```python
class NotTrivialFunction(object):
    '''Compute : t(u(d1,d2),v(d3,d4),w(d5))
    where:
        t(x,y) = x + y + 4
        u(x,y) = x + y + 1
        v(x,y) = x + y + 2
        w(x)   = x + 3
    and d1, d2, d3, d3, d5 are the parameters'''

    @irp_leaves_mutables("d1")
    def __init__(self, d1, d2, d3, d4, d5):
        self.d1 = d1
        self.d2 = d2
        self.d3 = d3
        self.d4 = d4
        self.d5 = d5

    @irp_node
    def t(self):
        return self.u1 + self.v + 4

    @irp_node
    def u1(self):
        return self.fu(self.d1, self.d2)

    @irp_node
    def v(self):
        return self.u2 + self.w + 2

    @irp_node
    def u2(self):
        return self.fu(self.d3, self.d4)

    @irp_node
    def w(self):
        return self.d5 + 3

    def fu(self, x, y):
        return x + y + 1
```

Now, if you (or the python interpreter during his exploration of the production tree) ask for the same node twice it won't be recomputed! (For more detailed explanation on how we achieve this, please read the source code.)

##Tricky part: Mutability

In this example, all the variations of the production tree are immutable. You can't change any node. In a real world application this a quite a limitation. For example, in an iterative procedure, we need to change some node and recompute another accordingly.
This can be achieved in IRPy with the `irp_node_mutable` and the `irp_leaveas_mutables`. In addition, both of theses function create the `setter` of these node automatically.

See this demo:
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

See how in the `solve` function, when we modify `x` it change `x_ext(x,f(x),f'(x))` acordingly.

#Exemple

You can see all these exemple, in the `run_test.py` file.

\[0\]: http://osp.chickenkiller.com/mediawiki/index.php?title=IRP
