#!/usr/bin/env python3

from pylab import *
from scipy.optimize import curve_fit

def growth_curve(t, a, b, c):
    return a * np.exp(b * t) - a

def predict_od(od, a, b, c):
    return np.log(od/a + 1) / b


t_od = array([
    #[ 30, 0.070],
    #[ 60, 0.128],
    #[ 90, 0.299],
    #[100, 0.401],
    #[ 30, 0.065],
    #[ 60, 0.120],
    #[ 90, 0.274],
    #[100, 0.370],
    #[ 80, 0.1893],
    #[ 80, 0.2458],
    #[100, 0.3728],
    #[120, 0.5400],
    #[ 80, 0.2743],
    #[100, 0.4322],
    #[120, 0.6133],
    #[120, 0.1016],
    #[160, 0.2291],
    #[200, 0.5077],
    [0,0],
    [60+15, 0.1211],
    [60+15, 0.1225],
    [60+35, 0.2101],
    [60+35, 0.2236],
])

t = t_od[:,0]
od = t_od[:,1]

p0 = 0.02267968, 0.02818784, 0
popt, pcov = curve_fit(growth_curve, t, od, p0=p0)

target = 0.25
t_target = predict_od(target, *popt)
print("OD={} at {}h{}".format(target, int(t_target//60), int(t_target%60)))

tx = linspace(0, 1.1 * t_target)
odx = growth_curve(tx, *popt)

plot(t, od, 'o')
plot(tx, odx)
plot(tx, [target] * len(tx))
xlim(0, 1.1 * t_target)
show()




