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