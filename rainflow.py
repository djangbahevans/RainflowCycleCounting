#!/usr/bin/env python
"""
-------------------------------------------------------------------------------
Rainflow counting function
Copyright (C) 2017 Evans Djangbah
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
Contact: Evans Djangbah, Kwame Nkrumah University of Science and Technology
Email: djangbahevans@gmail.com
-------------------------------------------------------------------------------
USAGE:
To call the function in a script on array of turning points <array_ext>:
    import rainflow as rf
    array_out = rf.rainflow(array_ext)
-------------------------------------------------------------------------------
DEPENDENCIES:
- Numpy
-------------------------------------------------------------------------------
NOTES:
Some portions of Python code modified from rainflow.c code with mex function for Matlab from
WISDEM project: https://github.com/WISDEM/AeroelasticSE/tree/master/src/AeroelasticSE/rainflow
-------------------------------------------------------------------------------
"""

from random import choice
from threading import Thread

import numpy as np


class Valley(object):
    def __init__(self, value, index, sig):
        self.__value__ = value
        self.index = index
        self.__parent_signal__ = sig
        self.position = [value]
        self.index_of_position = [index]
        self.pos_dict = {index: value}
        self.terminate = False

    @property
    def value(self):
        return self.__value__

    @property
    def range(self):
        return round(abs(self.value - self.position[-1]), 1)

    @property
    def parent_signal(self):
        return self.__parent_signal__

    def plot(self, axes):
        print('Plotting Valley at index {}'.format(self.index))
        x = []
        y = []
        shapes = ['s', '^', '*', 'o', '.', 'v', '<', '>', '1', '2', '3', '4',
                  '8', 'p', 'P', 'h', 'H', '+', 'x', 'X', 'D', 'd', '|', '_']
        colors = ['y', 'm', 'c', 'r', 'g', 'b', 'k']
        shape = choice(shapes)
        color = choice(colors)
        for i, index in enumerate(self.index_of_position):
            if self.position[i] != self.position[i-1] and i > 0:
                m = (self.parent_signal[index]-self.parent_signal[index - 1])
                c = self.parent_signal[index] - m*index
                y += [self.position[i-1]]
                x += [(y[-1] - c)/m]
                y += [self.position[i]]
                x += [(y[-1] - c)/m]
            else:
                x += [index]
                y += [self.position[i]]
        axes.plot(x, y, color)
        axes.plot(x[-1], y[-1], color + shape)
        axes.plot(x[0], y[0], color + shape)


class Peak(object):
    def __init__(self, value, index, sig):
        self.__value__ = value
        self.index = index
        self.__parent_signal__ = sig
        self.position = [value]
        self.index_of_position = [index]
        self.pos_dict = {index: value}
        self.terminate = False

    @property
    def value(self):
        return self.__value__

    @property
    def range(self):
        return round(abs(self.value - self.position[-1]), 1)

    @property
    def parent_signal(self):
        return self.__parent_signal__

    def plot(self, axes):
        print('Plotting Peak at index {}'.format(self.index))
        x = []
        y = []
        shapes = ['s', '^', '*', 'o', '.', 'v', '<', '>', '1', '2', '3', '4',
                  '8', 'p', 'P', 'h', 'H', '+', 'x', 'X', 'D', 'd', '|', '_']
        colors = ['y', 'm', 'c', 'r', 'g', 'b', 'k']
        shape = choice(shapes)
        color = choice(colors)
        for i, index in enumerate(self.index_of_position):
            if self.position[i] != self.position[i-1] and i > 0:
                m = (self.parent_signal[index]-self.parent_signal[index - 1])
                c = self.parent_signal[index] - m*index
                y += [self.position[i-1]]
                x += [(y[-1] - c)/m]
                y += [self.position[i]]
                x += [(y[-1] - c)/m]
            else:
                x += [index]
                y += [self.position[i]]
        axes.plot(x, y, color)
        axes.plot(x[-1], y[-1], color + shape)
        axes.plot(x[0], y[0], color + shape)


def isvalley(index, signal):
    try:
        if signal[index+1] > signal[index]:
            return True
    except IndexError:
        if signal[index-1] > signal[index]:
            return True
    return False


def eval_peaks(peaks_extremes, sig):
    """
    Rainflow codes for the evaluation of valleys

    INPUT
    peaks_extreme: List containing only Valley objects
    sig: Original list or tuple from which valleys_extreme was created

    OUTPUT
    None
    """
    print('Inside peak function')
    for a, peak in enumerate(peaks_extremes):
        print('Peak at index {}'.format(peak.index))
        con_sigs = sig[peak.index+1:]
        for con_sig, _ in enumerate(con_sigs):
            if not peak.terminate:
                peak.index_of_position += [con_sig+peak.index+1]
                if not isvalley(con_sig+peak.index + 1, sig):
                    peak.position += [peak.position[-1]]
                    peak.pos_dict[peak.index_of_position[-1]
                                  ] = peak.position[-1]
                    if con_sigs[con_sig] >= peak.value:
                        peak.terminate = True
                        break
                else:
                    c_peaks = peaks_extremes[:a]
                    max_ind = max(peak.index_of_position)
                    if con_sigs[con_sig] < peak.position[-1]:
                        peak.pos_dict[peak.index_of_position[-1]
                                      ] = con_sigs[con_sig]
                        peak.position += [con_sigs[con_sig]]
                    else:
                        peak.pos_dict[peak.index_of_position[-1]
                                      ] = peak.position[-1]
                        peak.position += [peak.position[-1]]
                    for c_peak in c_peaks[::-1]:
                        if max(c_peak.index_of_position) >= max_ind:
                            c_peak_pos = c_peak.pos_dict[max_ind-1]
                            peak.terminate = True if c_peak_pos > \
                                peak.position[-1] else peak.terminate
                            peak.position[-1] = c_peak_pos if c_peak_pos > \
                                peak.position[-1] else peak.position[-1]
                            peak.pos_dict[peak.index_of_position[-1]] = c_peak_pos if \
                                c_peak_pos > peak.position[-1] else peak.position[-1]
            else:
                break
    print('Exiting Peak Function')


def eval_valleys(valleys_extreme, sig):
    """
    Rainflow codes for the evaluation of valleys

    INPUT
    valleys_extreme: List containing only Valley objects
    sig: Original list or tuple from which valleys_extreme was created

    OUTPUT
    None
    """
    print('Inside Valleys function')

    # Loop through all valley objects
    for a, valley in enumerate(valleys_extreme):
        print('Valley at index {}'.format(valley.index))
        # Considers signals that come after selected valley
        con_sigs = sig[valley.index+1:]
        # Loops through the selected signal
        for con_sig, _ in enumerate(con_sigs):
            if not valley.terminate:  # While the cycle hasn't ended
                # Jump to the next extrema and append the index of the next extrema to the valley's index property
                valley.index_of_position += [con_sig+valley.index+1]
                # Check to see if the next extrema is a valley
                if isvalley(con_sig+valley.index + 1, sig):
                    # Append the value of the next extrema to the position property of the valley
                    valley.position += [valley.position[-1]]
                    
                    # Also append it to the post_dict dictionary with the index as key
                    valley.pos_dict[valley.index_of_position[-1]
                                    ] = valley.position[-1]
                    # Terminate if the value of the current valley is greater than the value of the considered extrema
                    if con_sigs[con_sig] <= valley.value:
                        valley.terminate = True
                        break
                else: # If the next extrema is a peak
                    c_valleys = valleys_extreme[:a] 
                    max_ind = max(valley.index_of_position)
                    if con_sigs[con_sig] > valley.position[-1]:
                        valley.pos_dict[valley.index_of_position[-1]
                                        ] = con_sigs[con_sig]
                        valley.position += [con_sigs[con_sig]]
                    else:
                        valley.pos_dict[valley.index_of_position[-1]
                                        ] = valley.position[-1]
                        valley.position += [valley.position[-1]]
                    for k in c_valleys[::-1]:
                        if max(k.index_of_position) >= max_ind:
                            k_pos = k.pos_dict[max_ind-1]
                            valley.terminate = True if k_pos <= \
                                valley.position[-1] else valley.terminate
                            valley.position[-1] = k_pos if k_pos <= \
                                valley.position[-1] else valley.position[-1]
                            valley.pos_dict[valley.index_of_position[-1]] = k_pos if k_pos \
                                <= valley.position[-1] else valley.position[-1]
            else:
                break
    print('Exiting Valley function')


def rainflow(sig):
    """
    Find and plot rainflow parameters

    INPUTS
    List or tuple sig: List or tuple containing series signal

    OUTPUTS:
    Tuple sig: Original inputted list
    List peaks: A list containing
    """
    new_sig = []
    for i, signal in enumerate(sig):
        try:
            # Attempt to round of to a 1 decimal place
            new_sig += [round(float(signal), 1)]
        except ValueError:
            pass

    # Convert signal into a tuple of extrema
    sig = tuple(sig2ext(new_sig))

    # Create a Valley and Peak objects from the extrema signal
    valleys = []
    peaks = []
    for i, value in enumerate(sig[:-1]):
        if isvalley(i, sig):
            valleys += [Valley(value, i, sig)]
        else:
            peaks += [Peak(value, i, sig)]

    # Run independent rainflow code of separate threads
    p = Thread(target=eval_peaks, args=(peaks, sig))
    v = Thread(target=eval_valleys, args=(valleys, sig))

    p.start()
    v.start()

    # Join the two threads to the main thread
    p.join()
    v.join()

    return sig, peaks, valleys


def sig2ext(sig):
    """
    Returns a list of all local minima and maxima in input list
    Inputs: A list or a tuple of signals
    Output: A list of local extrema signals

    This code was originally written in MATLAB by Evans Djangbah
    This is a slightly modified form which only accepts one signal
    """
    w1 = np.diff(sig)
    w = [True] + [True if w1[i]*w1[i+1] <=
                  0 else False for i in range(len(w1)-1)] + [True]
    ext = [sig[i] for i, val in enumerate(w) if val is True]

    w1 = np.diff(ext)
    w = [True] + [False if w1[i] == 0 and w1[i+1] ==
                  0 else True for i in range(len(w1)-1)] + [True]
    ext1 = [ext[i] for i, val in enumerate(w) if val is True]
    ext = ext1

    w = [True] + [False if ext[i] == ext[i+1]
                  else True for i in range(len(ext)-1)]
    ext1 = [ext[i] for i, val in enumerate(w) if val is True]
    ext = ext1
    del ext1

    if len(ext) > 2:
        w1 = np.diff(ext)
        w = [True] + [True if w1[i]*w1[i+1] <
                      0 else False for i in range(len(w1)-1)] + [True]
        ext1 = [ext[i] for i, val in enumerate(w) if val is True]
        ext = ext1
        del ext1

    return ext
