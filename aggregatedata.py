import h5py as hp
import numpy as np


def getstats(runid, fileid):
    basedir = '/home/amit/WorkSpace/UCLA/simulations/PhaseDiagram/RawData'
    statfilepath = '{}/Run{}/DetailedOutput-{}.h5'.format(basedir, runid, fileid)
    vtkfilepath = '{}/Run{}/VTKFile-{}.h5'.format(basedir, runid, fileid)
    with hp.File(statfilepath, 'r') as statfile, hp.File(vtkfilepath, 'r') as vtkfile:
        msd = statfile['MSD'][::4000]
        vol = statfile['Volume'][::4000]
        rms = statfile['RMSAngleDeficit'][::4000]
        # Calculate asphericity
        for i in range(0, 1000, 2):
            points = vtkfile['T{}/Points'.format(i)]
            R = np.linalg.norm(points, axis=1, keepdims=True)
            R0 = R.mean()
            asp = np.mean((R - R0)**2)/R0**2
    return msd, vol, rms, asp


def onestatfile():
    """
    There are 4 dimensions -- simulation id(600), physical variables(4),
    runs(3) and timesteps(500). For every scene, we need to pull up data for
    all time-steps for selected physical variables for a given simulation id.

    The physical variables are stored as per the following index:
    {'MSD': 0, 'Volume': 1, 'RMSAngleDeficit': 2, 'Asphericity': 3}.

    The simulation ids are arranged in Gamma-major ascending order i.e. index 0
    refers to the smallest gamma and the smallest temperature for "that" gamma.
    index 1 refers to same gamma as index 0 but for the next higher temperature
    for "that" gamma.
    """
    with hp.File('StatsFile.h5', 'w') as onefile:
        alldata = np.empty((600, 4, 3, 500), dtype=np.float32)
        for j in range(600):
            for i in range(3):
                msd, vol, rms, asp = getstats(i, j+1)
                alldata[j, 0, i, :] = msd
                alldata[j, 1, i, :] = vol
                alldata[j, 2, i, :] = rms
                alldata[j, 3, i, :] = asp
        onefile.create_dataset('Stats', data=alldata, chunks=(1, 4, 3, 500),
                compression='gzip', compression_opts=9)


def onevtkfile():
    """
    There are 4 dimensions -- simulation id(600), timesteps(500), runs(3) and
    coordinates(216). For every scene, we need to pull up 216 floats for the 72
    (x, y, z) coordinates. The user may want to see the shell for another run
    of the same simulation parameters. Hence, runs are the second fastest
    varying dimension.
    """
    basedir = '/home/amit/WorkSpace/UCLA/simulations/PhaseDiagram/RawData'
    with hp.File('VTKFile.h5', 'w') as onefile:
        allvtk = np.empty((600, 500, 3, 216), dtype=np.float32)
        for j in range(600):
            for i in range(3):
                vtkfilepath = '{}/Run{}/VTKFile-{}.h5'.format(basedir, i, j+1)
                with hp.File(vtkfilepath, 'r') as vtkfile:
                    for t in range(500):
                        allvtk[j, t, i, :] = vtkfile['T{}/Points'.format(2*t)][:].ravel()
        onefile.create_dataset('Points', data=allvtk, chunks=(1, 50, 3, 216), 
                compression='gzip', compression_opts=9)


if __name__ == '__main__':
    onevtkfile()
    onestatfile()
