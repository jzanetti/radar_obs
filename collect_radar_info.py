
def return_radar_info(radar):
    radar_stn_altitude = radar.altitude['data'][0]
    radar_azimuth = radar.azimuth['data']
    radar_elevation = radar.elevation['data']
    radar_sweep_start = radar.sweep_start_ray_index['data']
    radar_sweep_end = radar.sweep_end_ray_index['data']
    radar_nsweep = radar.nsweeps
    radar_ref = radar.fields['reflectivity']['data']

    return radar_stn_altitude,radar_azimuth,radar_elevation,radar_sweep_start,radar_sweep_end,radar_nsweep,radar_ref

def get_ppi(radar_nsweep,radar_elevation,radar_sweep_start,radar_sweep_end,radar_azimuth,radar_ref):
    ppi_data = {}
    for i in range(radar_nsweep):
        radar_start = radar_sweep_start[i]
        radar_end = radar_sweep_end[i]
        ppi_data['level_'+str(i)] = radar_ref[radar_start:radar_end]
    
    return ppi_data
        