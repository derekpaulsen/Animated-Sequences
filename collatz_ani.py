from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from time import sleep

#Globals for animate function
path_seqs = None
patch = None
path_idx = 0
step = 0
y_max = 0
x_max = 0
def make_collatz(n: int) -> list:
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

def clear_fig() -> None:
    #TODO display the start length
    global ax, patch, x_max, y_max

    #adjust scale on axes
    x_max = max([x for x,y in path_seqs[path_idx]]) + 1
    y_max = max([y for x,y in path_seqs[path_idx]])
    y_max += np.log2(y_max)
    ax.set_xlim(0, x_max)
    ax.set_ylim(0, y_max)
    
    patch.set_edgecolor('black')
    #clear all text
    for t in text_objs:
        t.set_text('')

    return (patch,)

def add_label(x: int, y: int) -> None:
    '''
    add a label to the vertex at (x,y), offset is scaled
    to improve readability 
    '''
    global step, text_objs, y_max, x_max
    #current text object being modified
    t = text_objs[step]
    #scalar
    z = 30

    t.set_x(x+ x_max/(2*x_max + z))
    t.set_text(str(y))
    #offset is above or below the vertex depending on 
    #direction of the line
    if y % 2 == 0:
        t.set_y(y + y_max/(2*y_max + z))
    else:
        t.set_y(y - y_max/(y_max + z))

def animate(i: int) -> tuple:
    global step, path_idx, ax, verts 
    path_len = len(path_seqs[path_idx])
    #change path to green when completed
    if step == path_len-1:
        patch.set_edgecolor('green')
    #reset and get ready to display next path
    elif step >= path_len:
        step = 0
        path_idx += 1
        sleep(1.5)
        clear_fig()

    #extend the path
    x,y = path_seqs[path_idx][step]
    verts[step:, 0] = x
    verts[step:, 1] = y

    add_label(x,y)
    step += 1

    return (patch, *text_objs)


n = 25
path_seqs = make_collatz(n)   

seq_lim = max([len(l) for l in path_seqs])
num_frames = sum([len(l) for l in path_seqs]) 

fig, ax = plt.subplots()

#create text boxes
text_objs = [ax.text(0,0,'') for i in range(seq_lim)]

verts = np.zeros((seq_lim,2))
codes = [Path.MOVETO].extend([Path.LINETO] * (seq_lim - 1))

path = Path(verts, codes)
patch = PathPatch(path, facecolor = 'none', edgecolor = 'black', lw = 2, animated = True)
ax.add_patch(patch)

#animtion
ani = FuncAnimation(fig, animate, frames = num_frames, repeat = False, blit = True, interval = 400)
plt.show()
