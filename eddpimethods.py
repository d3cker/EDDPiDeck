from eddpiutils import str2bool

class Config():
    def __init__(self, jdata, sg):
        #this is so wrong ... can't find solution for now
        sg.theme(jdata['General']['deck_theme'])
        self.font = (jdata['General']['deck_font_name'],int(jdata['General']['deck_font_size']))
        self.font_bold = (jdata['General']['deck_font_name'],int(jdata['General']['deck_font_size']),"bold")
        self.row_max_buttons = int(jdata['General']['row_max_buttons'])
        self.image_scale = int(jdata['General']['image_scale'])
        self.icons_path = jdata['General']['icons_path'] + '/' + jdata['General']['icons_theme'] + '/'
        self.pad = (int(jdata['General']['button_pad_x']), int(jdata['General']['button_pad_y']))
        self.button_resize = str2bool(jdata['General']['button_resize'])
        self.border_width = int(jdata['General']['border_width'])
        self.button_color_overwrite = str2bool(jdata['General']['button_color_overwrite'])
        self.button_font_color =  jdata['General']['button_font_color']
        self.button_color = self.button_font_color + " on " + sg.theme_background_color() if self.button_color_overwrite else sg.theme_background_color()
        self.key_release_delay =  float(jdata['General']['key_release_delay'])
        self.edd_addr = jdata['General']['edd_addr']
        self.deck_theme = jdata['General']['deck_theme']


#    {'responsetype': 'status',
#    'entry': 4655, 
#    'SystemData': 
#        {'System': 'Njikan', 
#        'SystemAddress': 6405910172370, 
#        'PosX': '-104.78', 'PosY': '3.66', 'PosZ': '-20.81', 'EDSMID': '0', 
#        'VisitCount': 27}, 
#    'EDDB':
#        {'State': 'Boom', 
#        'Allegiance': 'Independent', 
#        'Gov': 'Democracy', 
#        'Economy': 'High Tech', 
#        'Faction': 'The Misfits Of The Galaxy', 
#        'Security': 'Medium Security', 'MarketID': 3226717696}, 
#    'Ship': 
#        {'Ship': 'DC-13A swarog Asp Explorer (1)', 
#        'Fuel': '40', 
#        'Range': '30,09ly', 
#        'TankSize': '40', 
#        'Cargo': '0/8', 
#        'Data': '51', 
#        'Materials': '34', 
#        'MicroResources': '9'}, 
#    'Travel': {'Dist': '', 'Jumps': '', 'Time': ''}, 
#    'Bodyname': 'Smeaton Port', 
#    'HomeDist': '0', 
#    'SolDist': '106,89', 
#    'GameMode': 'Open', 
#    'Credits': '95407640', 
#    'Commander': 'd3cker0x008a', 
#    'Mode': 'Docked'}

class Status():
    def __init__(self):
        self.SystemData = {
            "System": "",
            "VisitCount" : ""
        }
        self.EDDB = {
            "Allegiance":"",
            "Gov": "",
            "Economy": "",
            "Faction": "",
            "Security": ""
        }
        self.Ship = {
            "Ship": "",
            "Fuel": "",
            "Range": "",
            "TankSize": "",
            "Cargo": "",
            "Data": "",
            "Materials": "",
            "MicroResources": ""
        }
        self.Travel = {
            "Dist": "",
            "Jumps": "",
            "Time": ""
        }

        self.Other = {
            "Bodyname":"",
            "HomeDist": "",
            "SolDist": "",
            "GameMode": "",
            "Credits": "",
            "Commander": "",
            "Mode": ""
        }
        self.NeedsUpdate = False
    def update(self,status):
        for i in [ 'System' , 'VisitCount' ]:
            self.SystemData[i] = str(status['SystemData'][i])

        for i in [ 'Allegiance' , 'Gov' , 'Economy' , 'Faction' , 'Security' ]:
            self.EDDB[i] = str(status['EDDB'][i])

        for i in [ 'Ship', 'Fuel', 'Range', 'TankSize', 'Cargo', 'Data', 'Materials', 'MicroResources' ]:
            self.Ship[i] = str(status['Ship'][i])

        for i in [ 'Dist' , 'Jumps' , 'Time' ]:
            self.Travel[i] = str(status['Travel'][i])

        for i in [ "Bodyname", "HomeDist", "SolDist", "GameMode", "Credits", "Commander", "Mode" ]:
            self.Other[i] = str(status[i])

        self.NeedsUpdate = True

    def ClearUpdate(self):
        self.NeedsUpdate = False
