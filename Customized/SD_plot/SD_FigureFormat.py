import os
import numpy as np
from PIL import Image
import matplotlib as mpl
from matplotlib import cm
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec


def get_color_cycle(NUM_COLORS, cmap='coolwarm'):
    cm = plt.get_cmap(cmap)
    custom_cycler = [cm(1. * x / NUM_COLORS) for x in range(NUM_COLORS)]
    return custom_cycler


fontsize = 8
# Font
font = {
    # 'family': "Helvetica",
    "weight": 'normal',
    "size": fontsize}
mpl.rc("font", **font)
mpl.rcParams['mathtext.fontset'] = 'stix'
mpl.rcParams['mathtext.bf'] = 'sans:italic:bold'
mpl.rcParams['figure.dpi'] = 300
mpl.rcParams['figure.autolayout'] = True

# Linewidth
linewidth = 0.5
mpl.rcParams['axes.linewidth'] = linewidth
mpl.rcParams['axes.labelweight'] = 'normal'
mpl.rcParams['lines.linewidth'] = linewidth
mpl.rcParams['xtick.major.width'] = linewidth
mpl.rcParams['xtick.major.size'] = 3
mpl.rcParams['ytick.major.width'] = linewidth
mpl.rcParams['ytick.major.size'] = 3

mpl.rcParams['legend.fontsize'] = 5
mpl.rcParams['axes.formatter.limits'] = -2, 4

mpl.rcParams['axes.formatter.useoffset'] = False
mpl.rcParams['axes.spines.top'] = True
mpl.rcParams['xtick.top'] = True
mpl.rcParams['xtick.direction'] = 'in'
mpl.rcParams['axes.spines.right'] = True
mpl.rcParams['ytick.right'] = True
mpl.rcParams['ytick.direction'] = 'in'
mpl.rcParams['axes.xmargin'] = 0.0  # x margin.  See `axes.Axes.margins`
mpl.rcParams['axes.ymargin'] = 0.1  # y margin.  See `axes.Axes.margins`
mpl.rcParams['legend.frameon'] = False
mpl.rcParams['legend.borderpad'] = 0
mpl.rcParams['axes.titlepad'] = 15

# color
# colorcycle = ["#DF9E9B","#99BADF","#D8E7CA","#99CDCE","#999ACD","#FFD0E9"] # 6 light
colorcycle = ["#354e97", "#70a3c4", "#c7e5ec", "#f5b46f", "#df5b3f"]  # 5 Blue->red
# colorcycle = ["#fbf49a","#eeb5ba","#7e5874","#ffe2b5","#edb073","#ce223d","#aeadd6","#91adb9","#d1d1d1","#c48ab6"]
# colorcycle = ["#7b7b7c","#28a8de","#fff300","#f3835e","#ef5a29","#f1eee8"]
# colorcycle = ["#8ecfc9", "#ffbe7a", "#fa7f6f", "#82b0d2", "#beb8dc", "#e7dad2"]

# colorcycle = get_color_cycle(8, cmap='coolwarm')
# mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=colorcycle)

# layout

fig_size = np.asarray([10, 7])
fig_size = fig_size / 2.54


def get_im(fg):
    if isinstance(fg, (np.ndarray, np.generic)):
        im = fg
    else:
        # get the figure canvas and renderer
        canvas = fg.canvas
        renderer = canvas.get_renderer()
        # draw the figure canvas
        canvas.draw()
        # get the numpy array of the figure canvas
        im = np.array(renderer.buffer_rgba())
        plt.close(fg)
    return im


def turn_off(list):
    for ax in list:
        ax.axis('off')
        # ax.axis('tight')


def import_fig(path):
    # open the image with PIL
    img = Image.open(path)
    # convert the image to a numpy array with float dtype
    arr = np.asarray(img, dtype=np.float32) / 255.0
    # close the PIL image to free memory
    img.close()
    return arr.astype(float)


def vertical_stack(fig_width, heights, figs, labels=None, sharex=False):
    gs = gridspec.GridSpec(ncols=1, nrows=len(heights), height_ratios=heights)
    fig = plt.figure(figsize=(fig_width, np.sum(heights)))
    # create the axes objects for each subplot
    axs = []
    for i in range(len(heights)):
        if i == 0:
            axs.append(fig.add_subplot(gs[i]))  # No sharing for the first subplot
        else:
            if sharex:
                axs.append(fig.add_subplot(gs[i], sharex=axs[0]))  # sharex with the first subplot
            else:
                axs.append(fig.add_subplot(gs[i]))
        axs[i].imshow(figs[i])
        if labels is not None:
            axs[i].text(0.05, 1.05, labels[i], transform=axs[i].transAxes, fontweight='bold', va='top')
    turn_off(axs)
    return fig


def horizontal_stack(fig_height, widths, figs, labels=None):
    gs = gridspec.GridSpec(ncols=len(widths), nrows=1, width_ratios=widths)
    fig = plt.figure(figsize=(np.sum(widths), fig_height))
    # create the axes objects for each subplot
    axs = []
    for i in range(len(widths)):
        axs.append(fig.add_subplot(gs[i]))
        axs[i].imshow(figs[i])
        if labels is not None:
            axs[i].text(0.05, 1 + 0.05, labels[i], transform=axs[i].transAxes, fontweight='bold', va='top')
    turn_off(axs)
    return fig


def insert(fg, fig_insert, left, bottom, width, height):
    # decrease label/tick sizes in fig_insert
    for ax in fg.axes:
        ax.tick_params(labelsize=8)
        for label in ax.get_xticklabels():
            label.set_size(8)
        for label in ax.get_yticklabels():
            label.set_size(8)
    ax = fg.add_axes([left, bottom, width, height])
    ax.imshow(get_im(fig_insert))
    ax.axis('off')


def add_vline(vlines, y, label='', position=None, color='grey', ls='--', fontsize=8):
    plt.vlines(x=vlines, ymin=min(y), ymax=max(y), color=color, ls=ls)
    for i, x in enumerate(vlines):
        if position is None:
            position = min(y)
        if isinstance(label, list):
            plt.text(x, position, f'{label[i]}', rotation=90, verticalalignment='bottom', fontsize=fontsize,
                     color=color)
        else:
            plt.text(x, position, f'{label}:{x}', rotation=90, verticalalignment='bottom', fontsize=fontsize,
                 color=color)


def get_path(filename):
    figure_folder = r'/Users/chellybone/Library/CloudStorage/Box-Box/N15_Figs/Methods:Supp/Sensitivity/3_17'
    # figure_folder = r'/Users/chellybone/Library/CloudStorage/OneDrive-WashingtonUniversityinSt.Louis/wustl/2023 Spring/ESR_cal/fg'
    # figure_folder = r'C:\Users\duxin\OneDrive - Washington University in St. Louis\wustl\2023 Spring\ESR_cal\fg\convolution'
    full_path = os.path.join(figure_folder, filename)
    return full_path

def offset(myFig,myAx,n=1,yOff=60):
    dx, dy = 0., yOff/myFig.dpi
    return myAx.transData + mpl.transforms.ScaledTranslation(dx,n*dy,myFig.dpi_scale_trans)

def plot_waterfall(xs,ys,z,offset):
    fig, ax = plt.subplots(figsize=(5, 6))
    for idx, i in enumerate(z):
        z_ind = max(z) - idx  ## to ensure each plot is "behind" the previous plot
        trans = offset(fig, ax, idx, yOff=offset)

        ## note that I am using both .plot() and .fill_between(.. edgecolor="None" ..)
        #  in order to circumvent showing the "edges" of the fill_between
        ax.plot(xs, ys, color="k", linewidth=0.5, transform=trans, zorder=z_ind)
        ax.fill_between(xs, ys, -0.5, facecolor="w", edgecolor="None", transform=trans, zorder=z_ind)

    ## turn off the spines
    for side in ["top", "right", "left"]:
        ax.spines[side].set_visible(False)
    ## and turn off the y axis
    ax.set_yticks([])
