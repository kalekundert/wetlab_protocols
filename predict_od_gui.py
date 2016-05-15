#!/usr/bin/env python3

import os
import numpy as np
import gi; gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject
from matplotlib.figure import Figure
from numpy import arange, sin, pi
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from pprint import pprint

def minutes_to_str(minutes):
    return '{}h{:02d}'.format(int(minutes//60), int(minutes % 60))

def str_to_minutes(str):
    import re

    parsed_time = re.match('(\d+)h(\d+)?|(\d+)m', str)
    if not parsed_time:
        raise ValueError("can't interpret '{}' as a time.".format(str))

    hours = parsed_time.group(1) or 0
    minutes = parsed_time.group(2) or parsed_time.group(3) or 0

    return 60 * int(hours) + int(minutes)

def float_or_none(x):
    return float(x) if x is not None else None


def time_vs_od(params):
    times = [str_to_minutes(x[0]) for x in params['time_vs_od']]
    ods = [float(x[1]) for x in params['time_vs_od']]

    # Estimate the initial OD if the user says how much overnight culture was 
    # subcultured and didn't actually measure the OD at t=0.  The user can also 
    # provide the OD of the overnight culture, but by default this is assumed 
    # to be 4.

    if 0 not in times and params['subculture']:
        overnight_od = params.get('overnight_od', 4.00)
        overnight_vol = float(params['subculture'].split(':')[0])
        subculture_vol = float(params['subculture'].split(':')[1])
        initial_od = overnight_od * overnight_vol / subculture_vol

        times = [0] + times
        ods = [initial_od] + ods

    return times, ods

def growth_curve(t, *fit):
    return fit[0] * np.exp(fit[1] * t)

def fit_growth_curve(params):
    from scipy.optimize import curve_fit
    times, ods = time_vs_od(params)
    initial_guess = 0.02267968, 0.02818784

    if len(times) == 0:
        return initial_guess

    elif len(times) == 1:
        times = [0] + times
        ods = [initial_guess[0]] + ods

    return curve_fit(growth_curve, times, ods, p0=initial_guess)[0]

def time_estimate(od, fit):
    return np.log(od/fit[0] + 1) / fit[1]

def print_time_estimate(params, fit):
    print("OD={} at {}".format(
        params['target'],
        minutes_to_str(time_estimate(params['target'], fit)),
    ))

def plot_growth_curve(params, fit):
    target_od = params['target']
    known_times, known_ods = time_vs_od(params)
    max_time = 1.1 * time_estimate(target_od, fit)
    fit_times = np.linspace(0, max_time)
    fit_ods = growth_curve(fit_times, *fit)

    axes.plot(known_times, known_ods, 'ko', fillstyle='none')
    axes.plot(fit_times, fit_ods, 'k-')
    axes.plot(fit_times, [target_od] * len(fit_times), '--', color='grey')
    axes.xlim(0, max_time)
    axes.xlabel('Time (min)')
    axes.ylabel('OD600')


# Setup the window itself.

win = Gtk.Window()
win.connect("delete-event", Gtk.main_quit )
win.set_default_size(644, 365)
win.set_title("Predict OD")

class PredictOd(Gtk.HBox):

    def __init__(self):
        super().__init__()
        self.params = ParamsEditor()
        self.fig = Figure(facecolor='#e9e9e9')
        self.axes = self.fig.add_subplot(1, 1, 1)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.set_size_request(300, 300)

        self.axes.set_xlabel('Time (min)')
        self.axes.set_ylabel('OD')
        self.time_points, = self.axes.plot([], [], 'ko', fillstyle='none')
        self.predicted_od, = self.axes.plot([], [], 'k-')
        self.target_od, = self.axes.plot([], [], '--', color='gray')
        self.fig.tight_layout(pad=3)

        self.params.connect('new-params', self.on_new_params)

        self.pack_start(self.params, False, False, 0)
        self.pack_start(self.canvas, True, True, 0)

        self.on_new_params()

    def on_new_params(self, *args):
        params = self.params.get_params()
        fit = fit_growth_curve(params)

        # Update the plot.

        target_od = params['target']
        known_times, known_ods = time_vs_od(params)
        max_time = 1.1 * time_estimate(target_od, fit)
        fit_times = np.linspace(0, max_time)
        fit_ods = growth_curve(fit_times, *fit)

        self.time_points.set_xdata(known_times)
        self.time_points.set_ydata(known_ods)
        self.predicted_od.set_xdata(fit_times)
        self.predicted_od.set_ydata(fit_ods)
        self.target_od.set_xdata(fit_times)
        self.target_od.set_ydata([target_od] * len(fit_times))

        self.axes.relim()
        self.axes.autoscale()
        self.axes.set_xlim(0, max_time)
        self.canvas.draw()


class ParamsEditor(Gtk.Grid):

    __gsignals__ = {
            'new-params': (
                GObject.SIGNAL_RUN_FIRST, None, ()),
    }

    def __init__(self):
        super().__init__()
        self.target_od = LabeledEntry("Target OD", "0.6")
        self.overnight_od = LabeledEntry("Overnight OD", "4.0")
        self.subculture_dilution = LabeledEntry("Subculture Dilution")
        self.time_vs_od = TimeVsOd()
        self.time_estimate = TimeEstimate(self)

        self.set_row_spacing(5)
        self.set_column_spacing(2)
        self.set_column_homogeneous(True)

        self.attach(self.target_od, 0, 0, 2, 1)
        self.attach(self.overnight_od, 0, 1, 1, 1)
        self.attach(self.subculture_dilution, 1, 1, 1, 1)
        self.attach(self.time_vs_od, 0, 2, 2, 1)
        self.attach(self.time_estimate, 0, 3, 2, 1)

        #hbox = Gtk.HBox()
        #hbox.set_spacing(2)
        #hbox.pack_start(self.overnight_od, True, True, 0)
        #hbox.pack_start(self.subculture_dilution, True, True, 0)

        #self.pack_start(self.target_od, False, False, 5)
        #self.pack_start(hbox, False, False, 5)
        #self.pack_start(self.time_vs_od, True, True, 5)
        #self.pack_end(self.time_estimate, False, False, 5)

        self.set_border_width(20)

        on_new_params = lambda *args: self.emit('new-params')
        self.target_od.connect('new-params', self.on_new_params)
        self.overnight_od.connect('new-params', self.on_new_params)
        self.subculture_dilution.connect('new-params', self.on_new_params)
        self.time_vs_od.connect('new-params', self.on_new_params)

    def get_params(self):
        params = {
                'target': float_or_none(self.target_od.get_value()),
                'overnight_od': float_or_none(self.overnight_od.get_value()),
                'subculture': self.subculture_dilution.get_value(),
                'time_vs_od':self.time_vs_od.get_time_points(),
        }
        return params

    def on_new_params(self, *args):
        self.emit('new-params')


class LabeledEntry(Gtk.VBox):

    __gsignals__ = {
            'new-params': (
                GObject.SIGNAL_RUN_FIRST, None, ()),
    }

    def __init__(self, label, initial_value=None):
        super().__init__()
        self.label = Gtk.Label(label)
        self.label.set_justify(Gtk.Justification.LEFT)
        self.label.set_halign(Gtk.Align.START)

        self.entry = Gtk.Entry()
        self.entry.set_width_chars(0)
        #self.entry.set_max_width_chars(0)
        self.entry.set_size_request(0, 0)
        if initial_value:
            self.entry.set_text(initial_value)

        self.set_spacing(2)
        self.pack_start(self.label, True, False, 0)
        self.pack_start(self.entry, True, False, 0)

        self.entry.connect('activate', lambda *w: self.emit('new-params'))
        self.entry.connect('focus-out-event', lambda *w: self.emit('new-params'))

    def get_value(self):
        return self.entry.get_text()


class TimeVsOd(Gtk.Grid):

    __gsignals__ = {
            'new-params': (
                GObject.SIGNAL_RUN_FIRST, None, ()),
    }

    class EntryPair:

        def __init__(self):
            self.time = Gtk.Entry()
            self.time.set_width_chars(0)
            self.time.set_size_request(0, 0)

            self.od = Gtk.Entry()
            self.od.set_width_chars(0)
            self.od.set_size_request(0, 0)

        def __repr__(self):
            return '({}, {})'.format(self.time, self.od)

        def __bool__(self):
            return bool(self.time.get_text() and self.od.get_text())

        def get_time_point(self):
            return self.time.get_text(), self.od.get_text()


    def __init__(self):
        super().__init__()
        self.entries = []

        time_label = Gtk.Label("Time")
        time_label.set_justify(Gtk.Justification.LEFT)
        time_label.set_halign(Gtk.Align.START)

        od_label = Gtk.Label("OD")
        od_label.set_justify(Gtk.Justification.LEFT)
        od_label.set_halign(Gtk.Align.START)

        self.grid = Gtk.Grid()
        self.grid.set_row_spacing(2)
        self.grid.set_column_spacing(2)
        self.grid.set_column_homogeneous(True)
        self.grid.set_vexpand(True)

        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroller.add(self.grid)

        self.set_row_spacing(2)
        self.set_column_spacing(2)
        self.set_column_homogeneous(True)
        self.set_vexpand(True)

        self.attach(time_label, 0, 0, 1, 1)
        self.attach(od_label, 1, 0, 1, 1)
        self.attach(scroller, 0, 1, 2, 1)

        self.add_row()

    def get_time_points(self):
        return [row.get_time_point() for row in self.entries if row]

    def add_row(self):
        row = self.EntryPair()
        row.time.connect('activate', self.on_enter_time)
        row.time.connect('focus-out-event', self.on_enter_time)
        row.od.connect('activate', self.on_enter_od)
        row.od.connect('focus-out-event', self.on_enter_od)

        i = len(self.entries)

        self.entries.append(row)
        self.grid.attach(row.time, 0, i, 1, 1)
        self.grid.attach(row.od, 1, i, 1, 1)
        self.show_all()

    def on_enter_time(self, widget, *args):
        self.emit('new-params')

        # Add a new row to the widget if the last row is being filled in.
        if widget is self.entries[-1].time:
            self.add_row()

    def on_enter_od(self, widget, *args):
        self.emit('new-params')


class TimeEstimate(Gtk.VBox):

    def __init__(self, params_editor):
        super().__init__()
        self.label = Gtk.Label("Time Estimate")
        self.label.set_justify(Gtk.Justification.LEFT)
        self.label.set_halign(Gtk.Align.START)

        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        self.progress_bar.set_size_request(0, 0)

        self.set_spacing(2)
        self.pack_start(self.label, False, False, 0)
        self.pack_start(self.progress_bar, False, False, 0)

        self.on_new_params(params_editor)
        params_editor.connect('new-params', self.on_new_params)

    def on_new_params(self, widget):
        params = widget.get_params()
        fit = fit_growth_curve(params)
        times = time_vs_od(params)[0]
        estimate = time_estimate(params['target'], fit)

        self.progress_bar.set_fraction(max(times) / estimate if times else 0)
        self.progress_bar.set_text("OD={} at {}".format(
            params['target'], minutes_to_str(estimate)))


win.add(PredictOd())

#vbox.add(grid)
#hbox.pack_start(Params(), False, False, 5)


win.show_all()
if not os.fork():
    Gtk.main()
