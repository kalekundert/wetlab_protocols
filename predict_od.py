#!/usr/bin/env python3

"""\
Predict how long it will take a culture to reach a certain OD.  The time 
estimate can be updated as the culture grows.

Usage:
    predict_od.py [gui]
"""

## Imports
import os, numpy as np
from cmd import Cmd
from matplotlib import pyplot
from pprint import pprint

## GUI imports
# Try to import the GTK+3 bindings.  If that doesn't work, make a mock object 
# that looks like the Gtk module.  This will allow all my classes to be defined 
# without error, and in gui_main() I can check to see whether or not the import 
# was successful.
try:
    from unittest.mock import Mock
    import gi; gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, GObject
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
except ImportError:
    Gtk, GObject = Mock(), Mock()


class OdPredictor:

    def __init__(self):
        self.target_od = 0.6
        self._overnight_od = 4.0
        self._subculture_dilution = None
        self._time_points = []
        self._growth_fit = (
                4/250,          # 250x subculture dilution.
                np.log(2)/30,   # 30 minute doubling time.
        )
        self._stale = True

    @property
    def overnight_od(self):
        return self._overnight_od

    @overnight_od.setter
    def overnight_od(self, value):
        self._overnight_od = value
        self._stale = True

    @property
    def subculture_dilution(self):
        return self._subculture_dilution

    @subculture_dilution.setter
    def subculture_dilution(self, value):
        self._subculture_dilution = value
        self._stale = True

    @property
    def time_points(self):
        times = [str_to_minutes(x[0]) for x in self._time_points]
        ods = [float(x[1]) for x in self._time_points]

        # Estimate the initial OD if the user says how much overnight culture 
        # was subcultured and didn't actually measure the OD at t=0.  The user 
        # can also provide the OD of the overnight culture, but by default this 
        # is assumed to be 4.

        if 0 not in times:
            if self.subculture_dilution:
                overnight_vol = float(self.subculture_dilution.split(':')[0])
                subculture_vol = float(self.subculture_dilution.split(':')[1])
                initial_od = self.overnight_od * overnight_vol / subculture_vol
                times = [0] + times
                ods = [initial_od] + ods

        return times, ods

    def add_time_point(self, time, od):
        self._time_points.append((time, od))
        self._stale = True

    @property
    def growth_fit(self):
        if self._stale:
            from scipy.optimize import curve_fit
            times, ods = self.time_points

            if len(times) == 0:
                self._stale = False
                return self._growth_fit

            # If we only have one time point, create another assuming the  
            # doubling time really is 30 minutes.  This is conceptually the 
            # same as fitting only the initial OD, but the code is simpler.
            elif len(times) == 1:
                times = times + [times[0] + 30]
                ods = ods + [ods[0] * 2]

            self._stale = False
            self._growth_fit = curve_fit(
                    growth_curve, times, ods, p0=self._growth_fit)[0]

        return self._growth_fit

    @property
    def time_estimate(self):
        return time_estimate(self.target_od, *self.growth_fit)

    @property
    def time_estimate_str(self):
        return "OD={} at {}".format(
                self.target_od, minutes_to_str(self.time_estimate))

    def plot_time_estimate(self, axes=None):
        if axes is None:
            axes = pyplot.gca()

        known_times, known_ods = self.time_points
        max_time = 1.1 * self.time_estimate
        fit_times = np.linspace(0, max_time)
        fit_ods = growth_curve(fit_times, *self.growth_fit)

        axes.clear()
        axes.plot(known_times, known_ods, 'ko', fillstyle='none')
        axes.plot(fit_times, fit_ods, 'k-')
        axes.plot(fit_times, [self.target_od] * len(fit_times), '--', color='grey')
        axes.set_xlim(0, max_time)
        axes.set_xlabel('Time (min)')
        axes.set_ylabel('OD')


class OdPredictorCli(Cmd):

    def __init__(self):
        super().__init__()
        self.predictor = OdPredictor()

    def do_target_od(self, arg):
        """
        The target OD is the OD you want your cells to reach.  The default 
        value is 0.6, which is mid-log phase for healthy E. coli.  The prompt 
        predicts how long your culture will have to grow to reach this OD.

        target_od
            Display the target OD.

        target_od <float>
            Set the target OD.
        """
        if arg:
            self.predictor.target_od = eval(arg)
        else:
            print("target OD: {}".format(self.predictor.target_od))

    def do_overnight_od(self, arg):
        """
        The OD of the overnight culture you use to start your culture.  The 
        default value is 4.0, which is a typical OD for an overnight culture.  
        This parameter is only used to estimate the initial OD of your culture 
        if you provide a subculture dilution and don't measure an OD for 0h00.

        overnight_od
            Display the overnight OD.

        overnight_od <float>
            Set the overnight OD.
        """
        if arg:
            self.predictor.overnight_od = eval(arg)
        else:
            print("overnight OD: {}".format(self.predictor.overnight_od))

    def do_subculture_dilution(self, arg):
        """
        How much overnight culture you diluted into how much fresh media.  This 
        parameter is only used to estimate the initial OD of your culture if 
        you provide a subculture dilution and don't measure an OD for 0h00.

        subculture_dilution
            Display the subculture dilution.

        subculture_dilution <overnight_vol:fresh_media_vol>
            Set the subculture dilution, given as the volume of overnight 
            culture used, then a colon, then the volume of fresh media used.
        """
        if arg:
            self.predictor.subculture_dilution = eval(arg)
        else:
            print("subculture dilution: {}".format(self.predictor.subculture_dilution))

    def do_update(self, arg):
        """
        Record a new OD measurement.  The time estimate will be updated to fit 
        every recorded measurement as well as possible.

        update <time> <od>
            Record that the culture was at the given OD at the given time.  The 
            time should be given as "<hours>h<minutes>".  For example, you 
            would indicate 3 hours and 15 minutes as "3h15".
        """
        time, od = arg.split()
        self.predictor.add_time_point(time, od)

    def do_plot(self, arg):
        """
        Plot the predicted growth curve.
        """
        self.predictor.plot_time_estimate()
        pyplot.show()

    def do_quit(self, arg):
        """
        Quit the program.
        """
        return True

    @property
    def prompt(self):
        return self.predictor.time_estimate_str + ': '

    def emptyline(self):
        pass


class OdPredictorGui(Gtk.HBox):

    def __init__(self):
        super().__init__()
        self.controls = ControlPanel()
        self.controls.connect('new-params', self.on_new_params)

        self.fig = Figure(facecolor='#e9e9e9')
        self.axes = self.fig.add_subplot(1, 1, 1)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.set_size_request(300, 300)
        self.fig.tight_layout(pad=3)

        self.pack_start(self.controls, False, False, 0)
        self.pack_start(self.canvas, True, True, 0)

        self.on_new_params()

    def on_new_params(self, *args):
        predictor = self.controls.get_params()
        predictor.plot_time_estimate(self.axes)
        self.canvas.draw()


class ControlPanel(Gtk.Grid):

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

        self.set_border_width(20)

        on_new_params = lambda *args: self.emit('new-params')
        self.target_od.connect('new-params', self.on_new_params)
        self.overnight_od.connect('new-params', self.on_new_params)
        self.subculture_dilution.connect('new-params', self.on_new_params)
        self.time_vs_od.connect('new-params', self.on_new_params)

    def get_params(self):
        predictor = OdPredictor()
        predictor.target_od = float_or_none(self.target_od.get_value())
        predictor.overnight_od = float_or_none(self.overnight_od.get_value())
        predictor.subculture_dilution = self.subculture_dilution.get_value()
        for time, od in self.time_vs_od.get_time_points():
            predictor.add_time_point(time, od)
        return predictor

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
        predictor = widget.get_params()
        times = predictor.time_points[0]

        self.progress_bar.set_fraction(
                max(times) / predictor.time_estimate
                if predictor.time_points[0] else 0)
        self.progress_bar.set_text(predictor.time_estimate_str)



def growth_curve(t, *fit):
    return fit[0] * np.exp(fit[1] * t)

def time_estimate(od, *fit):
    return np.log(od/fit[0] + 1) / fit[1]

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


def cli_main():
    OdPredictorCli().cmdloop()

def gui_main():
    if isinstance(Gtk, Mock):
        raise SystemExit("The gui requires the python bindings to GTK+ 3.0 (also called GObject introspection).")

    win = Gtk.Window()
    win.connect("delete-event", Gtk.main_quit )
    win.set_default_size(644, 365)
    win.set_title("Predict OD")
    win.add(OdPredictorGui())
    win.show_all()
    if not os.fork():
        Gtk.main()


if __name__ == '__main__':
    import docopt
    args = docopt.docopt(__doc__)

    if args['gui']:
        gui_main()
    else:
        cli_main()
