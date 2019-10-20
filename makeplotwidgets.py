"""
We create a Graphical User Interface with plots and some control widgets.
This is the backend code for `ShowPlots.ipynb`.
"""

def guisetup():
    """
    Prepare the plot, the widgets and connect them for interaction.
    This function uses IPython magic `%matplotlib widget`. Hence, it must
    only be called from a Jupyter notebook or Jupyterlab environment.
    """
    
    import ipympl
    from IPython import get_ipython
    ipython = get_ipython()
    ipython.magic('matplotlib widget')
    import numpy as np
    import ipywidgets as ipw
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    from matplotlib.gridspec import GridSpec
    from matplotlib.ticker import ScalarFormatter
    
    from extractdata import getschedule, getstats, getshell
    
    # Get the simulation parameter lists
    gamma, tempmap = getschedule()
    
    # Prepare the plots
    plt.style.use('ggplot')

    # Subplot 2 (ax1) x-axis tick formatter
    formatter = ScalarFormatter(useOffset=True, useMathText=True)
    formatter.set_powerlimits((3, 3))

    plt.ioff()
    fig = plt.figure()
    fig.set_tight_layout(True)
    fig.canvas.layout.max_width='1000px'
    fig.canvas.layout.height='500px'
    gs = GridSpec(2, 2, figure=fig)
    ax0 = fig.add_subplot(gs[0, :-1])
    ax1 = fig.add_subplot(gs[1, :-1], sharex=ax0)
    ax2 = fig.add_subplot(gs[:, 1], projection='3d')

    ax0.set_ylabel(r'MSD')
    ax0.set_ylim(0.0, 5.0)
    plt.setp(ax0.get_xticklabels(), visible=False)

    ax1.set_ylabel(r'Volume')
    ax1.set_ylim(20.0, 47.0)

    ax1.set_xlabel(r'Time Steps')
    ax1.xaxis.set_major_formatter(formatter)
    ax1.set_xlim(0, 2000000)

    # Prepare plot artists
    timearr = np.arange(0, 2000000, 4000)
    title = fig.suptitle(r'$\gamma = {0:8.3f}$, $1/\beta = {1:6.4f}$'.format(gamma[0], tempmap[gamma[0]][0]))

    # Get starting data
    msd, vol = getstats(0, 0, 'Volume')

    # The three Mean Squared Displacement curves
    msdlines = []
    for i in range(3):
        msdlines.append(ax0.plot(timearr, msd[i, :])[0])

    # The three curves for whatever variable is on second plot
    arrlines = []
    for i in range(3):
        arrlines.append(ax1.plot(timearr, vol[i, :])[0])
    
    # Prepare the contorl widgets
    gammaw = ipw.IntSlider(min=0, max=29, step=1, value=0, description=r'FvK #', continuous_update=False)
    tempw = ipw.IntSlider(min=0, max=19, step=1, value=0, description=r'Temperature', continuous_update=False)
    timew = ipw.IntSlider(min=0, max=1996000, step=4000, value=1996000, description=r'Time Step', continuous_update=False)
    runw = ipw.Dropdown(options=[0, 1, 2], description='Run #:')
    plot2w = ipw.Dropdown(options=['Volume', 'rmsAngleDeficit', 'Asphericity'], description='Second plot:')
    controls = ipw.HBox([ipw.VBox([plot2w, gammaw, tempw]), ipw.VBox([runw, timew])])
    
    # The final gui
    gui = ipw.VBox([controls, fig.canvas])
    
    #-------------------------------------------------------------------------------
    # Set up interactions
    #-------------------------------------------------------------------------------
    
    def updatecurves(gammaid, tempid, plot2):
        """
        Update the 2d plots.
        """
        # Get the arrays for 2D plots
        msd, arr2 = getstats(gammaid, tempid, plot2)
        for i in range(3):
            msdlines[i].set_ydata(msd[i, :])
            arrlines[i].set_ydata(arr2[i, :])
        gammaval = gamma[gammaid]
        tempval = tempmap[gammaval][tempid]
        text = r'$\gamma = {0:8.3f}$, $1/\beta = {1:6.4f}$'.format(gammaval, tempval)
        title.set_text(text)
        fig.canvas.draw_idle()

    def updateplot2axes(plot2):
        """
        Change the axes for second plot based on selection:
        """
        if plot2 is 'Volume':
            ax1.set_ylim(20.0, 47.0)
            ax1.set_ylabel(r'Volume')
        elif plot2 is 'Asphericity':
            ax1.set_ylim(0.0, 0.05)
            ax1.set_ylabel(r'Asphericity')
        else: #plot2 is 'rmsAngleDeficit':
            ax1.set_ylim(0.0, 1.2)
            ax1.set_ylabel(r'rms Angle Deficit')
        updatecurves(gammaw.value, tempw.value, plot2)

    def update3dplot(gammaid, tempid, runid, time=1996000):
        """
        Update the 3D plot with new shell structure.
        """
        points, mesh = getshell(gammaid, tempid, runid, time)
        ax2.cla()
        ax2.plot_trisurf(points[:,0], points[:,1], points[:,2], triangles=mesh)
        fig.canvas.draw_idle()
    
    
    outplot2 = ipw.interactive_output(updateplot2axes, {'plot2':plot2w})
    outplotcurves = ipw.interactive_output(updatecurves, {'gammaid':gammaw, 'tempid':tempw, 'plot2':plot2w})
    outplot3d = ipw.interactive_output(update3dplot, {'gammaid':gammaw, 'tempid':tempw, 'runid':runw, 'time':timew})

    return gui