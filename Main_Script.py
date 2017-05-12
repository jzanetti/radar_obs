import pyart
import collect_radar_info
import numpy as np
import matplotlib.pyplot as plt

data = '/home/szhang/Programs/metservice_sample_data/radar/Auckland/AKL170511214502_met_vola.raw'
radar = pyart.io.sigmet.read_sigmet(data)
radar_stn_altitude,radar_azimuth,radar_elevation,radar_sweep_start,radar_sweep_end,radar_nsweep,radar_ref = collect_radar_info.return_radar_info(radar)
ppi_data = collect_radar_info.get_ppi(radar_nsweep,radar_elevation,radar_sweep_start,radar_sweep_end,radar_azimuth,radar_ref)

# exclude masked gates from the gridding
gatefilter = pyart.filters.GateFilter(radar)
gatefilter.exclude_transition()
gatefilter.exclude_masked('reflectivity')

# perform Cartesian mapping, limit to the reflectivity field.
grid = pyart.map.grid_from_radars(
    (radar,), gatefilters=(gatefilter, ),
    grid_shape=(1, 1000, 1000),
    grid_limits=((2000, 2000), (-123000.0, 123000.0), (-123000.0, 123000.0)),
    fields=['reflectivity'])

# create the plot
fig = plt.figure()
ax = fig.add_subplot(111)
ax.imshow(grid.fields['reflectivity']['data'][0], origin='lower')
plt.show()