from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from time import sleep
from collections import namedtuple

Point = namedtuple('Point', ['x', 'y'])

class LineAnimator:
    '''
    class for animating a given seqence
    '''
    def __init__(self, ax, seq_func, inter_func, n: int, interval):
        self.ax = ax
        self.point_iter = seq_func(n, inter_func, interval)
        self.line, = ax.plot([],[])
        self.x_data = []
        self.y_data = []
        r = range(self.point_iter.longest())
        self.labels = [ax.text(0,0,'') for i in r]

    def animate(self, i):
        try:
            p = next(self.point_iter)
        except StopIteration:
            sleep(10)
            exit(0)
            
        if p == None:
            sleep(2)
            self.clear()
        else:
            self.x_data.append(p.x)
            self.y_data.append(p.y)
            self.line.set_data(self.x_data, self.y_data)
            if p.x == int(p.x):
                self.add_label(p)
            if p.y == 1:
                self.line.set_color('green')

        return (self.line, *self.labels)
            
    
    def add_label(self, p):
        t = self.labels[int(p.x)]
        #scalar
        z = 30
        _ , xmax = self.ax.get_xlim() 
        _ , ymax = self.ax.get_ylim()
        t.set_x(p.x+ xmax/(2*xmax + z))
        t.set_text(str(int(p.y)))
        #offset is above or below the vertex depending on 
        #direction of the line
        if p.y % 2 == 0:
            t.set_y(p.y + ymax/(2*ymax + z))
        else:
            t.set_y(p.y - ymax/(ymax + z))

    def clear(self):
        xlim, ylim = self.point_iter.ax_limits()
        ylim += np.log2(ylim)
        self.ax.set_xlim(0, xlim)
        self.ax.set_ylim(0, ylim)
        
        #clear all text
        for t in self.labels:
            t.set_text('')
            
        self.x_data.clear()
        self.y_data.clear()
        
        self.line.set_color('black')

    def frames(self) -> int:
        pass
        #TODO implement
        #return number of frames in the animation

class SequenceFunc:

    def __init__(self, n: int, inter_func, inter: int):
        self.paths = self.make_seqs(n)
        #FIXME
        self._path_idx = 10

        self.line_funcs = []
        for path in self.paths:
            pf = LineFunc(path, inter_func , inter)
            self.line_funcs.append(pf)

    def make_seqs(self, n: int):
        raise NotImplemented

    def __iter__(self):
        return self

    def __next__(self) -> tuple:
        try:
            return next(self.line_funcs[self._path_idx])
        #move to next sub iterator
        except StopIteration:
            self._path_idx += 1
            return None
        #iterator exhausted
        except IndexError:
            raise StopIteration

    def longest(self):
        return max([len(p) for p in self.paths])

    def ax_limits(self):
        p = self.paths[self._path_idx]
        xmax = max([x for x,y in p])
        ymax = max([y for x,y in p])

        return (xmax, ymax)


class Collatz(SequenceFunc):
    '''
    A iterator object which generates curves through all the collatz sequences
    '''
    def __init__(self, n, inter_func, inter):
        super().__init__(n, inter_func, inter)
    

    def make_seqs(self, n: int):
        paths = []
        for i in range(2, n+1):
            curr_verts = []
            x = 0
            y = i
            curr_verts.append([x,y])
            while y > 1:
                if y % 2 == 0:
                    y //=2
                else:
                    y = y * 3 + 1
                x += 1
                curr_verts.append([x,y])

            paths.append(curr_verts)

        return paths




class LineFunc:
    '''
    Itertor for generating a line with follows the path, based on the interval
    function created by inter_func
    '''
    def __init__(self, seq: list, inter_func, inter: int):
        self._func_map = {}
        self.seq = seq
        #number of points on each interval
        self.inter = inter
        self.cnt = 0

        for i in range(len(self.seq)-1):
           self._func_map[i] = inter_func(self.seq[i], self.seq[i+1])

    def __iter__(self):
        return self

    def __next__(self) -> float:
        
        x = self.cnt/self.inter

        if x > len(self.seq):
            raise StopIteration

        f = self._func_map.get(int(x), None)
        #TODO change this to a default value
        y = 1 if f == None else f(x)
        
        self.cnt += 1
        return Point(x,y)


'''
IntervalFunc's are used to generate points an intervel between
the start and the end point
'''

class IntervalFuncCos:
    
    def __init__(self, start: tuple, end: tuple):
        self.x0, y0 = start
        x1, y1 = end
        self.z = (y0 - y1)/2
        self.w = (y0 + y1)/2
    
    def __call__(self, x: float) -> float:
        return np.cos((x - self.x0) * np.pi) * self.z + self.w

 
class IntervalFuncCube:

    def __init__(self, start: tuple, end: tuple):
        self.x0, y0 = start
        x1, y1 = end
        self.z = (self.x0 + x1)/2
        self.w = (y0 + y1)/2
        self.r = (y1 - y0)*4 

    def __call__(self, x: float) -> float:
        return ((x - self.z)**3) * self.r  + self.w

class IntervalFuncSqr:
    
    def __init__(self, start: tuple, end: tuple):
        self.x0, self.y0 = start
        x1, y1 = end
        self.r = (y1 - self.y0)

    def __call__(self, x: float) -> float:
        return ((x - self.x0)**2) * self.r + self.y0


class IntervalFunc4th:
    
    def __init__(self, start: tuple, end: tuple):
        self.x0, self.y0 = start
        x1, y1 = end
        self.r = (y1 - self.y0)

    def __call__(self, x: float) -> float:
        return ((x - self.x0)**4) * self.r + self.y0


if __name__ == '__main__':
    n = 50
    i = 30
    fig, ax = plt.subplots()
    a = LineAnimator(ax, Collatz, IntervalFunc4th, n, i)
    a.clear()
    ani = FuncAnimation(fig, a.animate, 300, repeat = True, blit = True, interval = 20)
    plt.show()
