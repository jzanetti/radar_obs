import collect_radar_info
import numpy as np
import data_processing
import wradlib
import argparse
import pyart as py
import os
import matplotlib.pyplot as plt
import datetime
import glob
import ntpath

def radar_config(method):
    data_config = {
        'target': method, # plot_cappi, plot_ppi
        'field': 'reflectivity',
        'field_threshold': [5,45],
        'cappi_config':
            {'grid_number': 1000, #the higher the more details, but run slower
             'cappi_height_range': (1500, 100000), # unit: meter 
             'cappi_domain_range': (-240000.0, 240000.0) # domain plotting radius in meter
             },
        'ppi_config':
            {   
                'sweep_level':1,
                'plotting_method': 'user',
                'user':
                    {
                        'grid_number': 500
                    }
             }     
        }
    
    qc_config = {
        'run_clutter_removal': True,
        'window_size': 5,
        }
    
    return data_config, qc_config

def myradar_program(args, cfile):
    data = cfile
    fig_dir = args.output_fig_dir + '/' + args.radar_name
    fig_size = args.figure_size
    
    if os.path.exists(fig_dir) == False:
        os.makedirs(fig_dir)
    
    data_config, qc_config = radar_config(args.method)
    
    title_str_prefix = 'CAPPI, ' + str(data_config['cappi_config']['cappi_height_range'][0]) + 'm - ' + str(data_config['cappi_config']['cappi_height_range'][1]) + 'm'
    
    if data_config['target'] == 'plot_cappi':
        radar = py.io.read(data)
        radar_stn_info,radar_time,radar_azimuth,radar_elevation,radar_sweep_start,radar_sweep_end,radar_nsweep,_,_,radar_ref \
                    = collect_radar_info.return_radar_info(radar,data_config)

        # exclude masked gates from the gridding
        gatefilter = py.filters.GateFilter(radar)
        gatefilter.exclude_transition()
        gatefilter.exclude_masked(data_config['field'])
        gatefilter.exclude_below(data_config['field'], data_config['field_threshold'][0])
        
        grid = py.map.grid_from_radars(
            (radar,), gatefilters=(gatefilter, ),
            grid_shape=(1, data_config['cappi_config']['grid_number'], data_config['cappi_config']['grid_number']),
            grid_limits=(data_config['cappi_config']['cappi_height_range'], 
                         data_config['cappi_config']['cappi_domain_range'], 
                         data_config['cappi_config']['cappi_domain_range']),
            fields=[data_config['field']])
        
        longitude, latitude = grid.get_point_longitude_latitude()
        cappi = grid.fields[data_config['field']]['data'][0]
        cappi = data_processing.value_range(cappi)
        
        if qc_config['run_clutter_removal']:
            cappi_qc,clutter_index = data_processing.clutter_removal(cappi,qc_config,data_config)
        
        title_str = 'CAPPI, ' + str(data_config['cappi_config']['cappi_height_range'][0]) + 'm-' + \
                            str(data_config['cappi_config']['cappi_height_range'][1]) + 'm, ' + radar_time.strftime('%Y-%m-%dT%H:%M:%S')
        longitude_in = longitude[0,:]
        latitude_in = latitude[:,0]
        data_processing.plot_data(data_config,fig_size,fig_dir,title_str,cappi,longitude_in,latitude_in,radar_stn_info,radar_time)
    
    if data_config['target'] == 'plot_ppi':
        # read in the file, create a RadarMapDisplay object
        radar = py.io.read(data)
        display = py.graph.RadarMapDisplay(radar)
        
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
            radar_location,radar_time, radar_azimuth,radar_elevation,\
                    radar_sweep_start,radar_sweep_end,radar_nsweep,\
                    radar_ngates, radar_range, \
                    radar_ref = collect_radar_info.return_radar_info(radar,data_config)
                            

            if qc_config['run_clutter_removal']:
                _,clutter_index = data_processing.clutter_removal(radar_ref,qc_config,data_config)
                radar_ref[clutter_index] = 0.0
            gridded_data,lon_data,lat_data = collect_radar_info.get_ppi(radar_location,\
                                                                        data_config['ppi_config']['sweep_level'],
                                                                        data_config['ppi_config']['user']['grid_number'],
                                                                        radar_nsweep,radar_elevation,
                                                                        radar_sweep_start, radar_sweep_end, 
                                                                        radar_azimuth,radar_ngates, radar_range,
                                                                        radar_ref)
            title_str = 'PPI, {}, Level {}, {}'.format(args.radar_name, data_config['ppi_config']['sweep_level'], 
                                                       radar_time.strftime('%Y-%m-%dT%H:%M:%S'))
            #title_str = 'PPI, ' + str(data_config['ppi_config']['sweep_level']) + ', ' + radar_time.strftime('%Y-%m-%dT%H:%M:%S')

            data_processing.plot_data(data_config,fig_size,fig_dir,title_str, gridded_data,lon_data,lat_data,radar_location,radar_time, args.radar_name)


def valid_timerange(radar_dir, radar_startdatime, radar_enddatime, stn_name):
    all_files = glob.glob('{}/{}*met_vola.raw'.format(radar_dir, stn_name))
    selected_files = []
    for cfile in all_files:
        cfiletime = datetime.datetime.strptime(ntpath.basename(cfile)[3:15], '%y%m%d%H%M%S')
        if cfiletime >= radar_startdatime and cfiletime <= radar_enddatime:
            selected_files.append(cfile)
    selected_files.sort()

    return selected_files

def args_opts_process(args):
    radar_startdatime = datetime.datetime.strptime(args.start, '%Y%m%dT%H%M%S')
    radar_enddatime = datetime.datetime.strptime(args.end, '%Y%m%dT%H%M%S')
    radar_dir = args.radar_data_dir
    selected_files = valid_timerange(radar_dir, radar_startdatime, radar_enddatime, args.radar_name)
    
    return selected_files

if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(
        description='Radar_program_monitoring')
    PARSER.add_argument('radar_data_dir', type=str, help="radar_data_dir", 
                        default='/var/lib/nfs/amps-data-transfer/observations_test/radar')
    PARSER.add_argument('radar_name', type=str, help="radar name, e.g., WLG")
    PARSER.add_argument('start', type=str, help="start time of radar - YYYYMMDDTHHMMSS")
    PARSER.add_argument('end', type=str, help="end time of radar - YYYYMMDDTHHMMSS")
    PARSER.add_argument('output_fig_dir', type=str, help="fig_dir")
    PARSER.add_argument('figure_size', type=str, help="fig_size")
    PARSER.add_argument('method', type=str, help="data plotting method: plot_cappi, plot_ppi")

    ARGS = PARSER.parse_args(['/var/lib/nfs/amps-data-transfer/observations_test/radar',
                              'WLG',
                              '20170601T200000','20170601T210000',
                              '/home/szhang/workspace/radar_data_processing/figure',
                              '(15,15)',
                              'plot_ppi'
                              ])
    selected_files = args_opts_process(ARGS)
    len_files = len(selected_files)
    for num, cfile in enumerate(selected_files, start=0):
        print '{}/{}: {}'.format(num, len_files, cfile)
        myradar_program(ARGS, cfile)
    
    print 'job done'


