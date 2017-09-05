
from functools import partial
def add_method(obj, func):
        'Bind a function and store it in an object'
        setattr(obj, func.__name__, partial(func, obj))

def plotfill(ax, x, y, *args, **kwargs):
    """plotfill(axes, x, y, *args, kwargs) -> plot curve and fill region (see below)

       x = list-like (iterable) of float
       y = list-like (iterable) of float
                   OR
       y = dictionary, either {'a':val, 'b':val, 'c':val } or { 'slope':val, 'point':(p,q) }

            If y is a dictionary, then it is used to draw the line that bounds the region, either
            using standard ax+by=c form or the point-slope equation of a line

            Valid dictionary forms for second argument are
                     dict( a = float, b = float, c = float)
                     dict( a = float, b = float)  # assumes c = 1
                     dict( m = float, b = float)
                     dict( m = float, intercept = float )
                     dict( slope = float, b = float)
                     dict( slope = float, intercept = float)
                     dict( slope = float, point = tuple(float)

       region = either 'above' or 'below' or 'to_zero' or 'above_zero' or float (default = 'above_zero')
       fillcolor = color for fill region (default = 'cyan')
       fillalpha = alpha for fill region (default = 1.0 )
       label = label FOR THE REGION (not the curve) ( default = None )
       hatched = boolean or int for if line pattern is used to fill the region
                 if True, then 40 hatch lines are drawn
                 if positive integer, then number of hatch lines to draw
                 REQUIRES y AS A DICTIONARY
       hatchoptions = None or dictionary of options for the hatch lines

       all other arguments and keyword arguments applied to curve

       NOTE: zorder of filled region is 0.5 less than zorder keyword argument
    """
    region = kwargs.pop('region', 'above_zero')
    edgecolor = kwargs.pop('edgecolor','black')
    fillcolor = kwargs.pop('fillcolor','cyan')
    if( 'color' in kwargs.keys() ):
        color = kwargs.pop('color','cyan')
        edgecolor = color
        fillcolor = color
    fzorder = 1
    if( 'zorder' in kwargs.keys() ):
        fzorder = kwargs['zorder'] - 0.5
    kwargs['color'] = edgecolor

    fillalpha = kwargs.pop('fillalpha', 0.2 )
    HasLabel  = kwargs.pop('label', False)
    hatched = kwargs.pop('hatched', False)
    hatchoptions = kwargs.pop('hatchoptions', dict() )

    # make sure x is an array
    x = np.array( [val for val in x])

    # Creat y if necessary
    if(type(y) == dict ):
        try:
            if( 'a' in y ):
                assert y['b'] != 0, 'Cannot plotfill a vertical line -- b must be non-zero'
                if( 'c' in y ):
                    c = y['c']
                else:
                    c = 1
                slope = -y['a']/y['b']
                intercept = c / y['b']
            else:
                if( 'm' in y):
                    slope = y['m']
                else:
                    slope = y['slope']
                if( 'intercept' in y ):
                    intercept = y['intercept']
                elif( 'point' in y):
                    intercept = y['point'][1] - slope*y['point'][0]
                else:
                    intercept = y['b']
        except:
            print("""Valid dictionary forms for second argument are
                     dict( a = float, b = float, c = float)
                     dict( a = float, b = float)  # assumes c = 1
                     dict( m = float, b = float)
                     dict( m = float, intercept = float )
                     dict( slope = float, b = float)
                     dict( slope = float, intercept = float)
                     dict( slope = float, point = tuple(float) """ )
            raise
        y = slope*x + intercept
    else:
        hatched = False

    # draw the curve
    curve = ax.plot(x, y, *args, **kwargs)

    # Get ybnd
    if( type(region) == str ):
        if( region == 'below' ):
            ybnd = ax.get_ylim()[0]
        elif( region == 'above' ):
            ybnd = ax.get_ylim()[1]
        else:
            ybnd = 0
    else:
        ybnd = region

    # either hatch or fill
    if( hatched ):
        xm, xM = min(x), max(x)
        if( type(hatched) == bool):
            nh = 40
        else:
            assert hatched > 0, "hatched must be a positive integer"
            nh = hatched

        # Create Sampling Points
        xm, xM = min(x), max(x)
        ym, yM = ax.get_ylim();
        ym = min(ym,ybnd,np.min(y))
        yM = max(yM,ybnd,np.max(y))

        if(slope >= 0 ):
            yb = min( ybnd, slope*xm  +  intercept )
            xb = xm - slope*(yM - yb)
            dx = (xM - xb)/nh
            xb += dx/2
            pts = [ (xb+i*dx,yM) for i in range(nh) ]
        else:
            yb = max( ybnd, slope*xm  +  intercept )
            xb = xm - slope*(ym - yb)
            dx = (xM - xb)/nh
            xb += dx/2
            pts = [ (xb+i*dx,ym) for i in range(nh) ]

        region = []
        endpts = []
        for pt in pts:
            #line through pt with slope -1/slope is y = ybdr - (x-xbdr)/slope
            xbdr, ybdr = pt
            #Intersections with ybnd and line, respectively
            xp = xbdr - slope*(ybnd - ybdr)
            yp = ybnd
            xq = (slope*(ybdr - intercept) +  xbdr)/(slope**2+1)
            yq = slope*xq+intercept

            if( xp < xm or xp > xM ):
                xp = max( xm, min(xp, xM))
                yp = ybdr - (xp - xbdr)/slope
            if( xq < xm or xq > xM ):
                xq = max( xm, min(xq, xM))
                yq = ybdr - (xq - xbdr)/slope

            # Plot if not already plotted
            if( not( (xp,yp) in endpts or (xq,yq) in endpts ) ):
                if(HasLabel):
                    region.append( ax.plot( [xp,xq], [yp,yq], color = fillcolor, alpha = fillalpha,
                                             zorder = fzorder, label = HasLabel, **hatchoptions ))
                    HasLabel = False
                else:
                    region.append( ax.plot( [xp,xq], [yp,yq], color = fillcolor, alpha = fillalpha,
                                             zorder = fzorder, **hatchoptions ))
            endpts.append((xp,yp))
            endpts.append((xq,yq))
    else:
        where = None
        if(region == 'above_zero'):
            where = [val >= 0 for val in y ]

        if(HasLabel):
            region = ax.fill_between(x, y, ybnd, color = fillcolor, alpha = fillalpha, where = where,
                                     zorder = fzorder, label = HasLabel)
        else:
            region = ax.fill_between(x, y, ybnd, color = fillcolor, alpha = fillalpha, where = where,
                                     zorder = fzorder)
    return curve, region

def xyspines(ax,xlabel = None, ylabel = None, **kwargs):
    """xyspines(ax) -> center the spines on the origin, with optional labels"""
    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero')

    if(xlabel):
        ax.text(ax.get_xlim()[1],  0, xlabel, va = 'bottom', **kwargs)
    if(ylabel):
        ax.text( 0, ax.get_ylim()[1], ' ' + ylabel, ha = 'left', **kwargs)


from matplotlib import rcParams
rcParams['axes.spines.right'] = False
rcParams['axes.spines.top'] = False

print( "imported add_method, plotfill, and xyspines" )