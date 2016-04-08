![](https://zippy.gfycat.com/SarcasticOpenHedgehog.gif)

With **I**mplicit **R**eference to **P**arameters\[0\], Instead of telling *what to do*, we express *what we want*.

\[0\]: http://osp.chickenkiller.com/mediawiki/index.php?title=IRP
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

In python we can use the special `property` objet to access and compute the node.

```
class P:

    def __init__(self,x):
        self._x = x

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self.x + 10
```

`Y` have no explicit parameter (x is implicit).  And, when we ask for `Y`, we doesn’t handle the execution sequence!  IRPy extend this idea of decorator by adding lazy evalutation (if you ask for `Y` twice, we dont recompute it) and auto creation of `setter`.

