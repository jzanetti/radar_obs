import numpy
import wradlib as wrl
import datetime

def return_radar_info(radar,data_config):
    radar_location = (radar.longitude['data'][0],radar.latitude['data'][0],radar.altitude['data'][0])
    radar_azimuth = radar.azimuth['data']
    radar_elevation = radar.elevation['data']
    radar_sweep_start = radar.sweep_start_ray_index['data']
    radar_sweep_end = radar.sweep_end_ray_index['data']
    radar_nsweep = radar.nsweeps
    radar_ref = radar.fields[data_config['field']]['data']
    radar_ngates = radar.ngates
    radar_range = radar.range['data']
    radar_time_str = radar.time['units']
    radar_time = datetime.datetime.strptime(radar_time_str[-20:-1],'%Y-%m-%dT%H:%M:%S')
    
    return radar_location,radar_time,radar_azimuth,radar_elevation, \
            radar_sweep_start,radar_sweep_end,radar_nsweep,radar_ngates,radar_range,\
            radar_ref

def get_ppi(radar_location,sweep_number,grid_number,
            radar_nsweep,radar_elevation,radar_sweep_start,radar_sweep_end,radar_azimuth,radar_ngates, radar_range, radar_ref):

    radar_start = radar_sweep_start[sweep_number]
    radar_end = radar_sweep_end[sweep_number]
        
    cur_radar_azimuth = radar_azimuth[radar_start:radar_end]
    cur_radar_range = radar_range
    cur_radar_ele = radar_elevation[radar_start:radar_end]
    cur_radar_data = radar_ref[radar_start:radar_end,:]
    gridded_data,lon_data,lat_data = ppi_grid(radar_location,cur_radar_azimuth,cur_radar_range,cur_radar_ele,cur_radar_data,grid_number)

    return gridded_data,lon_data,lat_data

def ppi_grid(radar_location,cur_radar_azimuth,cur_radar_range,cur_radar_ele,cur_radar_data, grid_number):
    """EPSG is a spatial reference number:
    For Auckland, it is 5759, check details from http://spatialreference.org/ref/epsg/?search=Auckland&srtext=Search
    The recommended approach is the following, but it does work for some reason
    epsg_number = {
        'Auckland': 5759
        }
    gk3 = wrl.georef.epsg_to_osr(epsg_number['Auckland'])
    """
    polargrid = numpy.meshgrid(cur_radar_range, cur_radar_azimuth)
    lon, lat, alt = wrl.georef.polar2lonlatalt_n(polargrid[0], polargrid[1],
                                             cur_radar_ele.mean(), radar_location)
    ae = wrl.georef.create_osr("aeqd", lon_0=radar_location[0], lat_0=radar_location[1])
    x, y = wrl.georef.reproject(lon, lat, projection_target=ae)

    xgrid = numpy.linspace(x.min(), x.max(), grid_number)
    ygrid = numpy.linspace(y.min(), y.max(), grid_number)
    lon_data = numpy.linspace(lon.min(), lon.max(), grid_number)
    lat_data = numpy.linspace(lat.min(), lat.max(), grid_number)
    
    grid_xy = numpy.meshgrid(xgrid, ygrid)
    grid_xy = numpy.vstack((grid_xy[0].ravel(), grid_xy[1].ravel())).transpose()
    
    xy=numpy.concatenate([x.ravel()[:,None],y.ravel()[:,None]], axis=1)
    gridded = wrl.comp.togrid(xy, grid_xy, max(cur_radar_range), numpy.array([x.mean(), y.mean()]), cur_radar_data.ravel(), wrl.ipol.Nearest)
    gridded_data = numpy.ma.masked_invalid(gridded).reshape((len(xgrid), len(ygrid)))
    
    return gridded_data,lon_data,lat_data


    
        
