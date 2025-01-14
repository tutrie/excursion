import numpy as np
import itertools
import logging
import pyDOE

from . import  utils

log = logging.getLogger(__name__)


def sample_grid(scandetails,ndim,sizes):
    los = np.random.uniform(0,0.1, size = ndim)
    his = np.random.uniform(0.9, 1.0, size =ndim)
    mesh =  np.array(np.meshgrid(*[np.linspace(los[i],his[i],sizes[i]) for i in range(ndim)]))
    X = utils.mesh2points(mesh, mesh.shape[1:])
    for i in range(ndim):
        vmin, vmax = scandetails.plot_rangedef[i][0], scandetails.plot_rangedef[i][1]
        X[:,i] = X[:,i]*(vmax-vmin) + vmin
    X = X[~scandetails.invalid_region(X)]
    return X

def latin_sample_n(scandetails,npoints,ndim):
    sample_n = npoints
    while True:
        X = pyDOE.lhs(ndim, samples=sample_n)

        for i in range(ndim):
            vmin, vmax = scandetails.plot_rangedef[i][0], scandetails.plot_rangedef[i][1]
            X[:,i] = X[:,i]*(vmax-vmin) + vmin
        len_before = len(X)
        X = X[~scandetails.invalid_region(X)]
        len_after = len(X)
        if not len_after >= npoints: #invalid might throw out points, so sample until we get what we want
            factor = float(len_before)/float(len_after) if len_after else 2
            sample_n = int(sample_n * factor)
            continue
        return X[:npoints]

def regular_grid_generator(
    scandetails,
    central_range = [5,20],
    nsamples_per_grid = 15,
    min_points_per_dim = 2):
    ndim = len(scandetails.plot_rangedef[:,2])
    grids = set(x for y in range(*central_range) for x in itertools.combinations_with_replacement([y,y-1,y-2],ndim))
    grids = [g for g in grids if np.all(np.array(g) >= min_points_per_dim)]
    grids = sorted(grids, key=lambda k: np.product(k))
    def makegrids(sizes):
        for s in range(nsamples_per_grid):
            yield sample_grid(scandetails,ndim,sizes)
    for g in grids:
        for X in makegrids(g):
            yield X,g

def latin_hypercube_generator(scandetails, nsamples_per_npoints = 50, point_range = [4, 100]):
    ndim = len(scandetails.plot_rangedef[:,2])
    import pyDOE
    for npoints in range(*point_range):
        for s in range(nsamples_per_npoints):
            yield latin_sample_n(scandetails,npoints,ndim), None
