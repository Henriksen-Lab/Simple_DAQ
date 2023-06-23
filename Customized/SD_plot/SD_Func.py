import numpy as np

import scipy
from scipy.optimize import curve_fit
from scipy import signal
from scipy import interpolate
from scipy.misc import derivative


def linear_func(x, A):
    y = A * x
    return y


def convolution_gaussian_func(x, x0, A, sigma):
    x1 = np.linspace(-100, 100, 100000)
    y1 = A / (x1 - x0)
    y2 = np.exp(-0.5 * (x1) ** 2 / sigma ** 2) / (np.sqrt(2 * np.pi) * sigma)
    y = interpolate.interp1d(x1,
                             signal.convolve(y1, y2, 'same') / sum(y2),
                             kind='linear',
                             bounds_error=False,
                             fill_value="extrapolate")
    return y(x)


def antisymetric(y):
    y = np.array(y)
    y = (y - y[::-1]) / 2
    return y

# def dfitdx(x, *params):
#     fit = f(x)
#     return derivative(fit, x, dx=1e6, args=params)

def compute_slope(x, y):
    dx = np.diff(x)
    dy = np.diff(y)
    slope = dy / dx
    newx = (x[:-1] + x[1:])/2
    return newx, slope