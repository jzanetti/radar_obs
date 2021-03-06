import pyart
import collect_radar_info
import numpy as np
import matplotlib.pyplot as plt
import data_processing
import wradlib

data = 'data/AKL170512004502_met_vola.raw'
data_config = {
    'target': 'plot_ppi', # plot_cappi, plot_ppi
    'field': 'reflectivity',
    'field_threshold': [15,45],
    # effective when plot_cappi:
    'cappi_config':
        {'grid_number': 1000, #the higher the more details, but run slower
         'cappi_height_range': (1500, 100000), # unit: meter 
         'cappi_domain_range': (-240000.0, 240000.0) # domain plotting radius in meter
         },
    # effective when plot_ppi:
    'ppi_config':
        {   
            'sweep_level':0,
            'plotting_method': 'user',
            'user':
                {
                    'grid_number': 500
                }
         }     
    }

qc_config = {
    'run_clutter_removal': False,
    'window_size': 5,
    }

if data_config['target'] == 'plot_cappi':
    radar = pyart.io.sigmet.read_sigmet(data)
    radar_stn_info,radar_azimuth,radar_elevation,radar_sweep_start,radar_sweep_end,radar_nsweep,radar_ref = collect_radar_info.return_radar_info(radar,data_config)
    ppi_data = collect_radar_info.get_ppi(radar_nsweep,radar_elevation,radar_sweep_start,radar_sweep_end,radar_azimuth,radar_ref)
    
    # exclude masked gates from the gridding
    gatefilter = pyart.filters.GateFilter(radar)
    gatefilter.exclude_transition()
    gatefilter.exclude_masked(data_config['field'])
    gatefilter.exclude_below(data_config['field'], data_config['field_threshold'][0])
    
    grid = pyart.map.grid_from_radars(
        (radar,), gatefilters=(gatefilter, ),
        grid_shape=(1, data_config['cappi_config']['grid_number'], data_config['cappi_config']['grid_number']),
        grid_limits=(data_config['cappi_config']['cappi_height_range'], 
                     data_config['cappi_config']['cappi_domain_range'], 
                     data_config['cappi_config']['cappi_domain_range']),
        fields=[data_config['field']])
    
    # create the plot
    longitude, latitude = grid.get_point_longitude_latitude()
    cappi = grid.fields[data_config['field']]['data'][0]
    cappi = data_processing.value_range(cappi)
    
    if qc_config['run_clutter_removal']:
        cappi_qc,clutter_index = data_processing.clutter_removal(cappi,qc_config,data_config)
    
    longitude_in = longitude[0,:]
    latitude_in = latitude[:,0]
    data_processing.plot_griddata(plt, cappi, longitude_in, latitude_in, radar_stn_info)
    plt.show()

if data_config['target'] == 'plot_ppi':
    import numpy as np
    import matplotlib.pyplot as plt
    import pyart
    
    # read in the file, create a RadarMapDisplay object
    radar = pyart.io.read(data)
    display = pyart.graph.RadarMapDisplay(radar)
    
    if data_config['ppi_config']['plotting_method'] == 'pyart':
        display.plot_ppi_map(data_config['field'], data_config['ppi_config']['sweep_level'], vmin=15, vmax=45,
                             min_lon=170, max_lon=180, min_lat=-40, max_lat=-33,
                             lon_lines=np.arange(170, 180, 1.0), projection='lcc',
                             lat_lines=np.arange(-40, -33, 1.), resolution='h',
                             lat_0=radar.latitude['data'][0],
                             lon_0=radar.longitude['data'][0])
        
        # plot range rings at 10, 20, 30 and 40km
        display.plot_range_ring(60., line_style='k-')
        display.plot_range_ring(120., line_style='k--')
        display.plot_range_ring(180., line_style='k-')
        display.plot_range_ring(240., line_style='k--')
        
        # plots cross hairs
        display.plot_line_xy(np.array([-40000.0, 40000.0]), np.array([0.0, 0.0]),
                             line_style='k-')
        display.plot_line_xy(np.array([0.0, 0.0]), np.array([-20000.0, 200000.0]),
                             line_style='k-')
        
        # Indicate the radar location with a point
        display.plot_point(radar.longitude['data'][0], radar.latitude['data'][0])
        
        plt.show()
        
    elif data_config['ppi_config']['plotting_method'] == 'user':
        radar_location,radar_azimuth,radar_elevation,\
                radar_sweep_start,radar_sweep_end,radar_nsweep,\
                radar_ngates, radar_range, \
                radar_ref = collect_radar_info.return_radar_info(radar,data_config)
                        
                        
        gridded_data,lon_data,lat_data = collect_radar_info.get_ppi(radar_location,\
                                                                    data_config['ppi_config']['sweep_level'],
                                                                    data_config['ppi_config']['user']['grid_number'],
                                                                    radar_nsweep,radar_elevation,
                                                                    radar_sweep_start, radar_sweep_end, 
                                                                    radar_azimuth,radar_ngates, radar_range,
                                                                    radar_ref)
        data_processing.plot_griddata(plt, gridded_data, lon_data, lat_data, radar_location)
        plt.show()
        
        
