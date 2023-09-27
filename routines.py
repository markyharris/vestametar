from metar import Metar # https://github.com/python-metar


# Lists
template = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    ]
    
arrow_a = [
    [00,00,69,00,00],
    [00,00,69,00,00],
    [69,00,69,00,69],
    [00,69,69,69,00],
    [00,00,69,00,00]
    ]

arrow_b = [
    [00,00,00,00,69],
    [00,00,00,69,00],
    [69,00,69,00,00],
    [69,69,00,00,00],    
    [69,69,69,00,00]
    ]

arrow_c = [
    [00,00,69,00,00],
    [00,69,00,00,00],
    [69,69,69,69,69],
    [00,69,00,00,00],    
    [00,00,69,00,00]
    ]

arrow_d = [
    [69,69,69,00,00],
    [69,69,00,00,00],
    [69,00,69,00,00],
    [00,00,00,69,00],    
    [00,00,00,00,69]
    ]

arrow_e = [
    [00,00,69,00,00],
    [00,69,69,69,00],
    [69,00,69,00,69],
    [00,00,69,00,00],    
    [00,00,69,00,00]
    ]

arrow_f = [
    [00,00,69,69,69],
    [00,00,00,69,69],
    [00,00,69,00,69],
    [00,69,00,00,00],    
    [69,00,00,00,00]
    ]

arrow_g = [
    [00,00,69,00,00],
    [00,00,00,69,00],
    [69,69,69,69,69],
    [00,00,00,69,00],    
    [00,00,69,00,00]
    ]

arrow_h = [
    [69,00,00,00,00],
    [00,69,00,00,00],
    [00,00,69,00,69],
    [00,00,00,69,69],    
    [00,00,69,69,69]
    ]

arrow_i = [
    [00,00,69,00,00],
    [00,69,69,69,00],
    [69,69,69,69,69],
    [00,69,69,69,00],    
    [00,00,69,00,00]
    ]


# Functions 
def get_decoded_metar(rawtext):
    rawtext = rawtext.strip()
    obs = Metar.Metar(rawtext) # Initialize a Metar object with the coded report
#    return(obs.string())
    
    station_id = str(obs.station_id)
    time = str(obs.time)        
    wind_dir = str(obs.wind_dir)
    wind_speed = str(obs.wind_speed)
    wind_gust = str(obs.wind_gust)
    vis = str(obs.vis)
    temp = str(obs.temp)
    dewpt = str(obs.dewpt)
    press = str(obs.press)
    weather = str(obs.weather)
    sky = obs.sky
    len_sky = len(obs.sky)
    _remarks = str(obs._remarks)

    return(station_id,time,wind_dir,wind_speed,wind_gust,vis,temp,dewpt,press,weather,sky,len_sky,_remarks)


def winddir(wndir=0): #8 arrows representing 45 degrees each around the compass.
    if (wndir >= 338 and wndir <= 360) or (wndir >= 1 and wndir <= 22): 
        return arrow_a                              # wind blowing from the north (pointing down)
    elif wndir >= 23 and wndir <= 67:
        return arrow_b                              # wind blowing from the north-east (pointing lower-left)
    elif wndir >= 68 and wndir <= 113:
        return arrow_c                              # wind blowing from the east (pointing left)
    elif wndir >= 114 and wndir <= 159:
        return arrow_d                              # wind blowing from the south-east (pointing upper-left)
    elif wndir >= 160 and wndir <= 205:
        return arrow_e                              # wind blowing from the south (pointing up)
    elif wndir >= 206 and wndir <= 251:
        return arrow_f                              # wind blowing from the south-west (pointing upper-right)
    elif wndir >= 252 and wndir <= 297:
        return arrow_g                              # wind blowing from the west (pointing right)
    elif wndir >= 298 and wndir <= 337:
        return arrow_h                              # wind blowing from the north-west (pointing lower-right)
    else:
        return arrow_i                              # Generic arrow returned
    
    
def get_wind_speed_direction(rawtext):
    obs = Metar.Metar(rawtext) # Initialize a Metar object with the coded report
    
    if obs.wind: # The wind() method summarizes the visibility observation.
        wind = obs.wind().split()
        windspeed = obs.wind_speed
        winddir = obs.wind_dir
        return(windspeed, winddir)
    else:
        return("NOWX")
    
    
def determine_flight_category(rawtext): # pass metar raw text string to get flight category returned
    # from METAR Library found here; https://github.com/python-metar
    #Flight Category Definitions. (https://www.aviationweather.gov/taf/help?page=plot)
    #+--------------------------------------+---------------+-------------------------------+-------+----------------------------+
    #|Category                              |Color          |Ceiling                        |       |Visibility                  |
    #|--------------------------------------+---------------+-------------------------------+-------+----------------------------+
    #|VFR   Visual Flight Rules             |Green          |greater than 3,000 feet AGL    |and    |greater than 5 miles        |
    #|MVFR  Marginal Visual Flight Rules    |Blue           |1,000 to 3,000 feet AGL        |and/or |3 to 5 miles                |
    #|IFR   Instrument Flight Rules         |Red            |500 to below 1,000 feet AGL    |and/or |1 mile to less than 3 miles |
    #|LIFR  Low Instrument Flight Rules     |Magenta        |       below 500 feet AGL      |and-or |less than 1 mile            |
    #+--------------------------------------+---------------+-------------------------------+-------+----------------------------+
    global ceil,vis
    temp_lst = []
    
    # Routine requires Metar package from; https://github.com/python-metar
    obs = Metar.Metar(rawtext) # Initialize a Metar object with the coded report
    
    print(rawtext) # debug
    
    if obs.vis: # The visibility() method summarizes the visibility observation.
        visibility = obs.visibility().split()
    else:
        return("NOWX")
    
    if obs.sky_conditions: # The sky_conditions() method summarizes the cloud-cover observations.
        ceiling = obs.sky_conditions().split()
        print(ceiling) # debug
    else:
        return("NOWX")
    
    # Pull ceilings from list if broken or overcast
    if 'broken' in ceiling:
        alt_index = ceiling.index('broken')+3
        ceil = int(ceiling[alt_index])
    elif 'overcast' in ceiling:
        alt_index = ceiling.index('overcast')+2
        ceil = int(ceiling[alt_index])
    elif 'indefinite' in ceiling:
        alt_index = ceiling.index('indefinite')+5
        ceil = int(ceiling[alt_index])
    elif 'few' in ceiling:
        ceil = 5000
    elif 'clear' in ceiling:
        ceil = 5000
    elif 'scattered' in ceiling:
        ceil = 5000
        
    else: # find int value in response as a last resort.
        for value in ceiling:
            try:
                temp_lst.append(int(value))
            except ValueError:
                continue            
        print("--->",temp_lst,"<---") # debug

    if "/" in visibility[0] or "less" in visibility: # Grab visibility. Set to .5 mile if fractional distance reported
        vis = .5
    else:
        vis = int(visibility[0])
        
    # Compare vis and ceil to standards to determine Flight Category
    if ceil > 3000 and vis > 5:
        return "VFR"
    elif ceil >= 1000 and ceil <= 3000 and vis >= 3 and vis <= 5:
        return "MVFR"
    elif ceil >= 1000 and ceil <= 3000 and vis >=3:
        return "MVFR"
    elif vis >= 3 and vis <= 5:
        return "MVFR"
    elif ceil >= 500 and ceil < 1000:
        return "IFR"
    elif vis >= 1 and vis < 3:
        return "IFR"
    else:
        return "LIFR"


def flight_cat_to_color(flight_cat):
    GREEN = '66'
    BLUE = '67'
    RED = '63'
    MAGENTA = '68'
    
    if flight_cat == 'VFR':
        return GREEN
    elif flight_cat == 'MVFR':
        return BLUE
    elif flight_cat == 'IFR':
        return RED
    else:
        return MAGENTA
    
    
def clear_to_color(vboard,color=0):
    screen_color = [
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        ]
    
    for j in range(6):
        for k in range(22):
            screen_color[j][k] = color
            
    vboard.raw(screen_color) # print to board

    
    