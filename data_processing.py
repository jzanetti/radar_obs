import numpy
import wradlib
from mpl_toolkits.basemap import Basemap, cm
import matplotlib.pyplot as plt
from ast import literal_eval as make_tuple

def plot_data(data_config,fig_size,fig_dir,title_str,
              radar_data,longitude,latitude,radar_stn_info,radar_time):
    filename_str = title_str
    for tar in [', ', '-', ':']:
        filename_str = filename_str.replace(tar,'_')
        
    plt.figure(figsize=make_tuple(fig_size))
    plot_griddata(plt, radar_data, longitude, latitude, radar_stn_info, title_str)
    plt.savefig(fig_dir + '/' + filename_str + '.png', bbox_inches='tight')
    plt.close()


def plot_griddata(plt,radar_data,lon,lat,radar_stn_info,title_str):
    m = Basemap(projection='stere',lat_0=radar_stn_info[1], lon_0=radar_stn_info[0],
                llcrnrlat=min(lat),urcrnrlat=max(lat),
                llcrnrlon=min(lon),urcrnrlon=max(lon))
    m.drawcoastlines()
    m.drawstates()
    m.drawcountries()
    ny = radar_data.shape[0]; nx = radar_data.shape[1]
    lons, lats = m.makegrid(nx, ny)
    x, y = m(lons, lats)
    cs = m.pcolor(x,y,radar_data,cmap=plt.get_cmap('jet'))
    cbar = m.colorbar(cs,location='bottom',pad="5%")
    cbar.set_label('dBZ')
    plt.clim([5,60])
    plt.title(title_str)

def plot_clutter_index(plt,clutter_index,longitude,latitude,radar_stn_info):
    lon = longitude[0,:]
    lat = latitude[:,0]
    m = Basemap(projection='stere',lat_0=radar_stn_info[0], lon_0=radar_stn_info[1],
                llcrnrlat=min(lat),urcrnrlat=max(lat),
                llcrnrlon=min(lon),urcrnrlon=max(lon))
    m.drawcoastlines()
    m.drawstates()
    m.drawcountries()
    ny = clutter_index.shape[0]; nx = clutter_index.shape[1]
    lons, lats = m.makegrid(nx, ny)
    x, y = m(lons, lats)
    cs = m.pcolor(x,y,clutter_index)
    
def value_range(data_in):
    data_in[numpy.logical_or(data_in > 120.0, data_in < 0.0)] = 0.0
    return data_in

def clutter_removal(data_in,qc_config,data_config):
    if isinstance(data_in, numpy.ma.core.MaskedArray):
        data_out=data_in.filled()
        
    clutter_index = wradlib.clutter.filter_gabella(data_out, wsize=qc_config['window_size'], 
                                       thrsnorain=data_config['field_threshold'][0], 
                                       tr1=data_config['field_threshold'][0], 
                                       n_p=6, tr2=1.3, 
                                       rm_nans=False, radial=False, cartesian=True)
    mask_index = numpy.logical_or(clutter_index,data_in.mask)
    data_out = numpy.ma.masked_where(mask_index, data_out)
    
    return data_out,clutter_index