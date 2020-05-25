#!/usr/local/bin/python3

'''
version 120815 Working to display minimum/day
version 171031
version 200206 display min
version 200213 python3
'''
version = 'v5 200213 python3'

import matplotlib
matplotlib.use('TkAgg')
#matplotlib.use('WxAgg')
#matplotlib.use('macosx')
import argparse as ap
import datetime as dt
import matplotlib.pyplot as pl
#import pylab as pl
#import matplotlib.pyplt as pl
import os
import sys
import math
import pandas as pd
import numpy as np
import matplotlib.scale as mscale
#import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
import matplotlib.ticker as ticker
#import numpy as np

#print os.environ['HOME'], os.environ['USER'], os.environ['HOST']
print(os.environ)
rootdir = os.environ['HOME']
host = os.environ['HOST'].split('.')[0]
debug = True

mondir = rootdir+'/Work/Mondata/Mailmon/'

#there used to be a readactivs in version 1
class SquareRootScale(mscale.ScaleBase):
    """
    ScaleBase class for generating square root scale.
    """

    name = 'root'

    def __init__(self, axis, **kwargs):
        mscale.ScaleBase.__init__(self)

    def set_default_locators_and_formatters(self, axis):
        axis.set_major_locator(ticker.AutoLocator())
        axis.set_major_formatter(ticker.ScalarFormatter())
        axis.set_minor_locator(ticker.NullLocator())
        axis.set_minor_formatter(ticker.NullFormatter())

    def limit_range_for_scale(self, vmin, vmax, minpos):
        return  max(0., vmin), vmax

    class SquareRootTransform(mtransforms.Transform):
        input_dims = 1
        output_dims = 1
        is_separable = True

        def transform_non_affine(self, a): 
            return np.array(a)**0.5

        def inverted(self):
            return SquareRootScale.InvertedSquareRootTransform()

    class InvertedSquareRootTransform(mtransforms.Transform):
        input_dims = 1
        output_dims = 1
        is_separable = True

        def transform(self, a):
            return np.array(a)**2

        def inverted(self):
            return SquareRootScale.SquareRootTransform()

    def get_transform(self):
        return self.SquareRootTransform()

mscale.register_scale(SquareRootScale)

def GetArgs():
    '''
    Get the arguments to reading the data
    '''
    parser = ap.ArgumentParser(description='Plot mail load')
    #    parser.add_argument('integers', metavar='N', type=int, nargs='+',
    #               help='an integer for the accumulator')
    parser.add_argument('-w','--window',\
                    choices=['all','ayear','aquart','amonth',\
                            'thismonth','aweek','thisweek','today','aday'],
                    default = 'amonth',
                    help='window for display')
    parser.add_argument('-n','--noupdate', action = 'store_true',
                   help='work with local data')
    parser.add_argument('-m','--mode', choices=['todo','in','avg','min','max','weekd'],
                        default = 'todo',
                        help='plot todo, inflow or averages')
    parser.add_argument('-s','--scale', choices=['linear','log','root'],
                        default = 'linear',
                        help ='scale on y axis, lin, log or root')
    parser.add_argument('-d','--dumpdata', action = 'store_true',
                   help='dump data to file')
    parser.add_argument('-r','--readdump', action = 'store_true',
                   help='read dumped data')
    parser.add_argument('-b','--benchmark', action = 'store_true',
                    help='do stat for benchmark')
    parser.add_argument('-y','--yearcomp', action = 'store_true',
                    help='compare with last year')

    args = parser.parse_args()
    return args

def readmonfiles():
    '''
    Find the files with the monitor data
    '''

    #meas = pd.DataFrame()
    measl = []
    mons = os.listdir(mondir)
    for monfile in mons:
        if (os.path.isfile(mondir+monfile) and (monfile.find('HuibMail')>=0)):
            measf = open( mondir+monfile, 'r')
            try:
                tmp = pd.read_csv(mondir+monfile,header=None,\
                    parse_dates=[[0,1]], infer_datetime_format=True, dayfirst=True, index_col=0)
                #apparently names does not work with combining dates
                #names=['date','jall','jdel','jnew','jflg','mall','mdel','mnew','mflg'])
                tmp.columns = ['jall','jdel','jnew','jflg','mall','mdel','mnew','mflg']
                tmp.index.name = 'date'
                #print tmp
            except:
                print(monfile,' seems corrupted')
            measl.append(tmp)
            measf.close()
            #meas = pd.concat(measl)
    meas = pd.concat( measl)
    
    print('Read {} files for {} data entries ({:6.2f}% complete)'\
        .format(len(mons),len(meas),100.*len(meas)/(len(mons)*288) ))
    
    return meas


def datewindow( wind, measmin, measmax ):
    '''
    From a window string, return a window
    '''
    if wind == 'thismonth':
        today = dt.date.today()
        datemin = dt.datetime(today.year,today.month,1,4,0)
        datemax = datemin + dt.timedelta(31)
    elif wind == 'ayear':
        today = dt.datetime.today()
        datemin = dt.datetime(today.year,today.month,today.day,4,0) - dt.timedelta(365)
        datemax = today + dt.timedelta(0.1)
    elif wind == 'aquart':
        today = dt.datetime.today()
        datemin = dt.datetime(today.year,today.month,today.day,4,0) - dt.timedelta(91)
        datemax = today + dt.timedelta(0.1)
    elif wind == 'amonth':
        today = dt.datetime.today()
        datemin = dt.datetime(today.year,today.month,today.day,4,0) - dt.timedelta(31)
        datemax = today + dt.timedelta(0.1)
    elif wind == 'thisweek':
        today = dt.date.today()
        dayow = today.weekday()
        todam = dt.datetime(today.year,today.month,today.day,4,0)
        datemin = todam - dt.timedelta(dayow)
        datemax = datemin + dt.timedelta(7)
    elif wind == 'aweek':
        today = dt.datetime.today()
        datemin = dt.datetime(today.year,today.month,today.day,4,0) - dt.timedelta(7)
        datemax = today + dt.timedelta(0.1)
    elif wind == 'today':
        today = dt.datetime.now()
        datemin = dt.datetime(today.year,today.month,today.day,4,0)
        datemax = datemin + dt.timedelta(1)
    elif wind == 'aday':
        today = dt.datetime.now()
        datemin = today - dt.timedelta(1)
        datemax = today + dt.timedelta(0.01)
    else:
        datemin=measmin
        datemax=measmax + dt.timedelta(0.5)

    print("Window '{}' = {} -to- {}".format(wind, datemin, datemax))
    return datemin, datemax

def accumdt( meas ):
    '''
    From the measurements, collect useful data... this is the tricky bit
    '''
    meas.sort_index(axis=0, ascending=True,inplace=True)
    iref = 0
    mailjin = 0; mailjout = 0; mailmin = 0; mailmout = 0
    
    t0 = dt.datetime(1963,8,8) #assuming I did not get mail before that
    ymdl = []
    jin = []; jout = []; mout = []; min = []
    mcur = 0; jcur = 0; mlast = 0; jlast = 0
    for idx,row in meas.iterrows():
        #huibhier need to compare days
        #print t0,'-', t0.date(),'----' , idx,'-', idx.date()
        if t0.date() != idx.date():
            mailjin = 0; mailjout = 0; mailmin = 0; mailmout = 0
            if ( idx < t0):
               print('Huhh?: ',idx,t0)
            t0 = idx
        else:
            jlast = jcur
            jcur = row['jall']-row['jdel']
            if ( jcur >  jlast ):
                mailjin += jcur - jlast
            else:
                mailjout += jlast -jcur
            mlast = mcur
            mcur = row['mall'] - row['mdel']
            if ( mcur > mlast ):
                mailmin += mcur - mlast
            else:
                mailmout += mlast - mcur
        jin.append(mailjin)
        jout.append(mailjout)
        mout.append(mailmout)
        min.append(mailmin)

    meas['jin'] = pd.Series(jin,meas.index)
    meas['jout'] = pd.Series(jout,meas.index)
    meas['mout'] = pd.Series(mout,meas.index)
    meas['min'] = pd.Series(min,meas.index)
    meas['wd']= meas.index.weekday
    meas['poll'] = meas.index.strftime('%H')
    
    meas['jall'] = meas['jall']-meas['jdel']
    meas['jflg'] = meas['jall']-meas['jflg']
    meas['mall'] = meas['mall']-meas['mdel']
    meas['mflg'] = meas['mall']-meas['mflg']
    
    #print meas
    return

def simpledusk2dawn(dmin, dmax ):
    #print dmin, dmax
    hdusk=22
    hdawn=8
    shade = []
    id = dmin
    # id is the running variable, associated with end of work da
    while ( id < dmax ):
        #colour all the nights grey and set colour for the day....
        pair = {}
        #every day has two intervals: from dawn to dusk and from dusk until dawn next day

        pair['start'] = min(dt.datetime(id.year,id.month,id.day,hdawn,0),dmax)
        pair['end'] = max(dt.datetime(id.year,id.month,id.day,hdusk,0),dmin)
        if (id.weekday() > 4 ):
            pair['color'] = 'grey'
        else:
            pair['color'] = 'white'
        #print pair
        shade.append(pair)
        pair = {}
            
        pair['start'] = min(dt.datetime(id.year,id.month,id.day,hdusk,0),dmax)
        pair['end'] = max(dt.datetime(id.year,id.month,id.day,hdawn,0)+dt.timedelta(1),dmin)
        pair['color'] = 'grey'
        shade.append(pair)
        #print pair

        id = id +dt.timedelta(1)

    return shade


def maxrangepd( t, y1, y2 ):
    
    maxy = max( y1.max(), y2.max() )

    return maxy
    
def statdates( measp ):
    
    print(measp.describe())
    return

def plotdates_pd( measp ):
    #print meas['index']
    
    print('scale',opts.scale)
    dolog = False
    if (opts.scale == 'log'): dolog=True
    if (opts.mode == 'todo' or opts.mode == 'in'):
        #These modes use real dates
        #ymax = maxrangepd(measp.date, measp.jall, measp.mall )
        if (opts.mode == 'todo'):        
            bx = measp.plot(y=['jall','jflg','jnew','mall','mflg','mnew'],\
                color=['navy','slateblue','lightslategray','red','indianred','lightsalmon'],\
                xlim=(datemin,datemax),\
                #ylim=(-0.5,1.1*ymax),\
                legend = False,\
                title="Huib's mail")
            bx.legend(['jive','flg','new','me','flg','new'],\
                loc='upper center', bbox_to_anchor=(0.5, -0.07), ncol=2, fontsize=8)
            bx.set_ylabel("#mail to do")
        elif (opts.mode == 'in'):
            #ymax = maxrangepd(measp.date, measp.jin, measp.jout )
            bx = measp.plot(y=['jin','jout','min','mout'],\
                color=['navy','slateblue','red','lightsalmon'],\
                xlim=(datemin,datemax),\
                #ylim=(-0.5,1.1*ymax),\
                legend = False,\
                title="Huib's mail")
            bx.legend(['jin','jout','min','mout'],\
                loc='upper center', bbox_to_anchor=(0.5, -0.07), ncol=2, fontsize=8) 
        else:
            print('STUB1')   
            
        shade = simpledusk2dawn(datemin, datemax)
        for i in range(len(shade)):
            #print 'shades:', shade[i]['start'],shade[i]['end']
            pl.axvspan(shade[i]['start'],shade[i]['end'],fc=shade[i]['color'],alpha=0.15, ec='none')

    elif (opts.mode == 'avg' or opts.mode == 'min'):
        bx = measp['jall'].resample('D').min().plot(label='jmintodo',\
            xlim=(datemin,datemax), color='navy')
        measp['mall'].resample('D').min().plot(label='mmintodo',color='red')
        measp['jin'].resample('D').max().plot(label='maxjin', color='slateblue')
        measp['min'].resample('D').max().plot(label='maxmin', color='indianred')
        bx.legend(['jall min','mall min','jin max','min max'],\
            loc='upper center', bbox_to_anchor=(0.5, -0.07), ncol=2, fontsize=8)                    
        #pl.legend()    
    elif opts.mode == 'weekd':
        avgall = measp.groupby((measp.index.dayofweek)*24. + (measp.index.hour))['jall','mall','jin','min'].mean()
        bx = avgall.plot(color=['navy','red','slateblue','indianred'],logy=dolog)
        bx.legend(['jall','mall','jin','min'],\
            loc='upper center', bbox_to_anchor=(0.5, -0.07), ncol=2, fontsize=8)   
    else:
        print('STUB2')   

    box = bx.get_position()
    bx.set_position([box.x0-0.1*box.width, box.y0 + box.height * 0.2,\
                 1.2*box.width, box.height * 0.8])
    bx.set_yscale(opts.scale)

    #bx.set_size_inches(50.5, 10.5)

    #pl.xaxis.set_major_locator( loc = WeekdayLocator(byweekday=MO, tz=tz) )
    wm = pl.get_current_fig_manager()
    #wm.resize(1400, 400)
    wm.window.wm_geometry("1400x400+5+5")

    pl.show()
    
    
def plotcomp( measp, measl ):
    #print meas['index']
    
    print('plots 2 scale',opts.scale)
    dolog = False
    if (opts.scale == 'log'): dolog=True
    if (opts.mode == 'todo' or opts.mode == 'in'):
        #These modes use real dates
        #ymax = maxrangepd(measp.date, measp.jall, measp.mall )
        if (opts.mode == 'todo'):        
            bx = measp.plot(y=['jall'],\
                color='navy',\
                #xlim=(datemin,datemax),\
                #ylim=(-0.5,1.1*ymax),\
                legend = True,\
                title="2018")
            measl.plot(ax=bx, y=['jall'],\
                color='red',\
                #xlim=(datemin,datemax),\
                #ylim=(-0.5,1.1*ymax),\
                legend = True,\
                title="last year")
            bx.legend(['this','1y ago'],\
                loc='upper center', bbox_to_anchor=(0.5, -0.07), ncol=2, fontsize=8)
            bx.set_ylabel("#mail to do")
        elif (opts.mode == 'in'):
            #ymax = maxrangepd(measp.date, measp.jin, measp.jout )
            bx = measp.plot(y=['jin'],\
                color='navy',\
                xlim=(datemin,datemax),\
                #ylim=(-0.5,1.1*ymax),\
                legend = True,\
                title="Huib's mail")
            measl.plot(ax=bx, y=['jin'],\
                color='red',\
                #xlim=(datemin,datemax),\
                #ylim=(-0.5,1.1*ymax),\
                legend = True,\
                title="last year")
            bx.legend(['this','1y ago'],\
                loc='upper center', bbox_to_anchor=(0.5, -0.07), ncol=2, fontsize=8) 
        else:
            print('STUB1')   
            
        shade = simpledusk2dawn(datemin, datemax)
        for i in range(len(shade)):
            #print 'shades:', shade[i]['start'],shade[i]['end']
            pl.axvspan(shade[i]['start'],shade[i]['end'],fc=shade[i]['color'],alpha=0.15, ec='none')

    box = bx.get_position()
    bx.set_position([box.x0-0.1*box.width, box.y0 + box.height * 0.2,\
                 1.2*box.width, box.height * 0.8])
    bx.set_yscale(opts.scale)

    #bx.set_size_inches(50.5, 10.5)

    #pl.xaxis.set_major_locator( loc = WeekdayLocator(byweekday=MO, tz=tz) )
    wm = pl.get_current_fig_manager()
    #wm.resize(1400, 400)
    wm.window.wm_geometry("1400x400+5+5")

    pl.show()

#---------------------------------------------------------------------------------------------------

print('Starting version {}'.format(version))
opts = GetArgs()
#print('Starting plots for {}, type: {} and noupdate={}'.format( opts.window, opts.mode, opts.noupdate))

if (not opts.noupdate and not opts.readdump):
    print('Running from host = {}'.format(host))
    if (host.lower() != 'maclangevelde5' ):
        command = 'rsync -av  langevelde@maclangevelde5.nfra.nl:Mailmon/ '+mondir
    else:
        command = 'rsync -av  '+rootdir+'/Mailmon/ '+ mondir
    print(command)
    os.system(command)
if debug: print('Done syncing')
if (opts.readdump):
    meas = pd.read_csv('mailstat.csv',parse_dates=[0], index_col=0)
    if debug: print('Finished reading dump')
else:
    # read raw data
    meas = readmonfiles()
    print('Read measurements: {} shape {}'.format(type(meas),meas.shape))
    if debug: print('Finished reading')

    # add total in and out
    accumdt( meas )
    if debug: print('Finished filter')

#print(meas.loc[:,['jall','mall','jin','min']].describe())

if (opts.dumpdata):
    meas.to_csv('mailstat.csv')
    if debug: print('Finished dump')
else:
    print(opts.window,meas.index.min(),meas.index.max())
    datemin, datemax = datewindow(opts.window,meas.index.min(),meas.index.max())
    #lastmin = datemin-dt.timedelta(days=365)
    #lastmax = datemax-dt.timedelta(days=365)
    mask = (meas.index > datemin) & (meas.index <= datemax)
    #mala = (meas.index > lastmin) & (meas.index <= lastmax)
    measp = meas.loc[mask]
    if (opts.yearcomp):
        meas2 = meas
        meas2.index = meas2.index.shift((52*7),'d')
        mask2 = (meas2.index > datemin) & (meas2.index <= datemax)
        measl = meas2.loc[mask2]
        #print measl.describe()
        print(measl.index.min())
        #print 'About to plot'
        plotcomp( measp, measl )
    #print(measp.loc[:,['jall','mall','jin','min']].describe())

    elif (opts.benchmark):
        print('Do a benchmark stat')
        statdates( measp )
    else:
        plotdates_pd( measp )




