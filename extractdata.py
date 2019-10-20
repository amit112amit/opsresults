import numpy as np
import h5py as hp
from collections import defaultdict
from pyhull.convex_hull import ConvexHull


def getschedule():
    """
    Read the file 'Schedule.csv' and collect the temperatures for each value of gamma.
    This file is sorted by gamma and then temperatures for each gamma.
    """
    tempmap = defaultdict(list)
    gammaset = set()
    with open('Schedule.csv', 'r') as csvfile:
        data = csvfile.read().split('\n')[1:-1]
        for row in data:
            gamma, temp = [round(float(s), 4) for s in row.split(',')]
            gammaset.add(gamma)
            tempmap[gamma].append(temp)
    gamma = sorted(list(gammaset))
    return gamma, tempmap


def getstats(gammaid, tempid, var2):
    """
    Given gamma and temperature indices, get the plot arrays for msd and `y2`.
    
    Parameters:
    -----------
    gammaid: index of gamma if the unique gamma values are arranged in ascending order.
    tempid: index of temperature if the unique temperature values are arranged in ascending order.
    var2: string for the physical variable to be plotted on the second plot as per the following map
        Valid values are 'Volume', 'rmsAngleDeficit', 'Asphericity'
    
    Returns:
    --------
    2 numpy arrays for msd and `var2`, each having 3 rows and 500 columns.
    """
    mapping = {'Volume': 1, 'rmsAngleDeficit': 2, 'Asphericity': 3}
    
    # There are 20 values of temperature for each gamma.
    index0 = 20*gammaid + tempid
    index1 = mapping[var2]
    
    with hp.File('StatsFile.h5', 'r') as statfile:
        msd = statfile['Stats'][index0, 0, :, :]
        arr2 = statfile['Stats'][index0, index1, :, :]
    return msd, arr2



def getshell(gammaid, tempid, run, time=1996000):
    """
    For a given gamma id, temperature id and timestep, read the coordinates from file and generate a mesh.
    
    Parameters:
    -----------
    gammaid: index of gamma
    tempid: index of temperature
    run: 0, 1 or 2. For every combination of gamma and temperature, we have 3 runs. 
    time: timestep
    
    Returns:
    --------
    x, y, z: coordinates of vertices of the mesh
    triangles: a Nx3 array giving connectivity of vertices forming the mesh
    """
    # There are 20 values of temperature for each gamma.
    index0 = 20*gammaid + tempid
    index1 = time // 4000
    index2 = run
    with hp.File('VTKFile.h5', 'r') as vtkfile:
        points = vtkfile['Points'][index0, index1, index2, :].reshape(-1, 3)
    
    sphere = points/np.linalg.norm(points, axis=1, keepdims=True)
    hull = ConvexHull(sphere)
    return points, hull.vertices