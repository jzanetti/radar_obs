import numpy
import wradlib
from mpl_toolkits.basemap import Basemap, cm

def plot_griddata(plt,cappi,lon,lat,radar_stn_info):
    #lon = longitude[0,:]
    #lat = latitude[:,0]
    m = Basemap(projection='stere',lat_0=radar_stn_info[1], lon_0=radar_stn_info[0],
                llcrnrlat=min(lat),urcrnrlat=max(lat),
                llcrnrlon=min(lon),urcrnrlon=max(lon))
    m.drawcoastlines()
    m.drawstates()
    m.drawcountries()
    ny = cappi.shape[0]; nx = cappi.shape[1]
    lons, lats = m.makegrid(nx, ny)
    x, y = m(lons, lats)
    cs = m.pcolor(x,y,cappi,cmap=plt.get_cmap('jet'))
    cbar = m.colorbar(cs,location='bottom',pad="5%")
    cbar.set_label('dBZ')
    plt.clim([5,60])

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