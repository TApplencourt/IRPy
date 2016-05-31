![](https://zippy.gfycat.com/SarcasticOpenHedgehog.gif)

[![PyPi](https://img.shields.io/pypi/v/irpy.svg)](https://pypi.python.org/pypi/irpy) [![TravisCI](https://img.shields.io/travis/TApplencourt/IRPy.svg)](https://travis-ci.org/TApplencourt/IRPy) [![License](https://img.shields.io/pypi/l/irpy.svg)](http://www.wtfpl.net/)


IRPy (pronounce /kəˈθuːluː/) extend the python `property` function in order to support lazy evaluation and mutability of nested properties (`property` that use `properties` in their declaration and so forth).
Lazy evaluation of properties are quite common ([Werkzeug](https://werkzeug.pocoo.org/docs/0.11/utils/#werkzeug.utils.cached_property), [cached-property](https://github.com/pydanny/cached-property)...),
but coherence problems can arise if you have inference rule between mutable properties. The aim of this library is to solve this problem.


## Install
- With [pip](https://pip.pypa.io/en/stable/):
```
pip install irpy
```
- With [conda](http://conda.pydata.org/docs/): 
```
conda install -c https://conda.anaconda.org/tapplencourt irpy
```
- You can download [irpy.pyx](https://raw.githubusercontent.com/TApplencourt/IRPy/master/irpyx.py) rename it into `irpy.py` and add it to `PYTHONPATH`.

## API
- `lazy_property`: a simple lazy property;
- `lazy_property_mutable`: a lazy property that can change. When doing so, all of these ancestors are invalided and will be recomputed when needed. Furthermore, all of these descendants are now unattainable;
- `lazy_property_leaf(mutable,immutable)`: this function allow node creation's from values defined in the `__init__` class method.

## But why i need all of this? Or *What is a scientific code*?
A program is a function of its input data:
```
output = program (input)
```
A program can be represented as a production tree where
- The root is the output;
- The leaves are the input data; 
- The nodes are the intermediate variables;
- The edges represent the relation needs/needed by.

In python, this way of thinking is encouraged by the usage of, special object, `property`. Indeed each `property` are one nodes of the production tree. When you nest them, you define implicitly the edges of this tree. 

### Illustration

This code snippet:
```python
class WeightFactory(object):
    '''Compute the weight of a rectangle'''

    def __init__(self, l1, l2, l3):
        '''Dimension of the box (m)'''
        self.l1 = l1
        self.l2 = l2
        self.l3 = l3

    @property
    def volume(self):
        " V = l1 * l2 * l3 (m^3)"
        return self.l1 * self.l2 * self.l3 

    @property
    def density(self):
        "Volumetric mass density of Iron (kg/m^3)"
        return 7.87 * 10**3

    @property
    def mass(self):
        "m = V * d (kg)"
        return self.volume * self.density

    @property
    def g(self):
        "g-force (m/s2) in equator"
        return 9.7803

    @property
    def weight(self):
        "(Newton)"
        return self.mass*self.g
```
can be represend as:

![](https://cdn.rawgit.com/TApplencourt/IRPy/master/examples/weight.svg)

In this example `l[1,3]`, `volume`, `density`, `mass`, `g`, `weight` are the node of the production tree. 

### Remarks

In the source code of the snipper, one can see that properties have no explicit parameter 
(in fact, IRPy mean [**I**mplicit **R**eference **P**arameter](http://osp.chickenkiller.com/mediawiki/index.php?title=IRP) for P**y**thon).

And this simplify dramatically sotfware developments. Indeed:
- The global production tree is not known by the programmer, the programmer doesn’t handle the execution sequence. Just ask a property, it will be computed on the fly:
```python
f = WeightFactory(1,1,1)
assert ( abs(f.weight - 76970.961) < 1.e-4)
```
- The program is easy to write (adding a new `property` only require to know about the name of theses implicit parameters);

### Lazy evaluation

But, the same data will be recomputed multiple times. A simple solution is to use lazy evaluation of these nodes/properties. Just replace `property` into `lazy_property` and you are good to go.
(all these example can be found in the [examples](https://github.com/TApplencourt/IRPy/blob/master/examples) folder).

### Draw back

In IRP paradigm, a Russian nesting lazy property, nodes are by default immutable. 
This mean that you cannot set these node by hand; the only way to compute a node is by using the function who have be decorated. 

For example:
```python
f = WeightFactory(1,1,1)
try:
    f.g = 1.622
except AttributeError:
    print "Node are immutable!"
```

## Mutability

In `IRPy`, the node who can be changed by hand are decorated with the `lazy_property_mutable` function. 
```python
@lazy_property_mutable
def g(self):
    "g-force (m/s2) in equator"
    return 9.7803
```

### Ancestor are invalided
When this kind of node node (for example `g`) are set, all her [ancestors](https://en.wikipedia.org/wiki/Tree_(data_structure)#Terminologies_used_in_Trees) (`wieght` in your case) will be recomputed the nest time somebody ask for them.

```python
f = WeightFactory(1,1,1)
assert ( abs(f.weight - 76970.961) < 1.e-4)
f.g = 1.622
assert ( abs(f.weight - 12765.14) < 1.e-4)
```
### Descendant are removed from the tree

Is we change an node (the `mass` for example), all her  descendants are removed from the tree and are, for now, unreachable.

```python
f = WeightFactory(1,1,1)
f.mass = 80
try:
    print f.volume
except AttributeError:
    print "Node have been removed"
```
