import numpy as np

import scipy
from datetime import datetime as dt
from scipy.optimize import curve_fit
from scipy import signal
from scipy import interpolate
from scipy.misc import derivative

def ratio_func(x, A):
    y = A * x
    return y

def linear_func(x, A, B):
    y = A * x + B
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

def round_to_2e(arr, align_width=10):
    output = []
    if isinstance(arr, (list, np.ndarray)):
        for item in arr:
            if isinstance(item, str):
                output.append(item.ljust(align_width))
            else:
                output.append(f"{item:.2e}".ljust(align_width))
        return ', '.join(output)
    else:
        raise TypeError("Input must be a list or a numpy array.")

def get_ymd(timestamp):
    time = dt.fromtimestamp(timestamp)
    today = time.strftime("%Y%m%d")
    return today