import io
import base64
import time
import output
import urllib.request
import os
import PIL

# nice one, found on stackoverflow
def resize_image(image_path, resize=None):
    if isinstance(image_path, str):
        img = PIL.Image.open(image_path)
    else:
        try:
            img = PIL.Image.open(io.BytesIO(base64.b64decode(image_path)))
        except Exception as e:
            data_bytes_io = io.BytesIO(image_path)
            img = PIL.Image.open(data_bytes_io)

    cur_width, cur_height = img.size
    if resize:
        new_width, new_height = resize
        scale = min(new_height/cur_height, new_width/cur_width)
        img = img.resize((int(cur_width*scale), int(cur_height*scale)),PIL.Image.LANCZOS)
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    del img
    return bio.getvalue()

def str2bool(value):
        return value.lower() in ("yes", "true", "t", "1", "y")

def display_message( sg , message , timeout = 5 ):
    message_layout = []
    msg_layout = []
    message_layout.append(sg.Text( message , key="-MSG-",  enable_events = True, pad=(1,1),auto_size_text = True,justification='center'))
    msg_layout.append(list(message_layout))
    window_msg = sg.Window('Elite PiDeck Message', msg_layout, location=(0,0), no_titlebar=False, element_justification='c', resizable=False).Finalize()
    time.sleep(timeout)
    window_msg.close()

# load buttons
def load_buttons(jdata):
    buttons_list = []
    buttons={
        'key_name': "",
        'key_text': "",
        'key_icon': "",
        'key_code': "",
        'key_event': "",
        'key_status': ""
    }
    for idx,i in enumerate(jdata['DeckButtons']):
        buttons['key_name'] = i['key_name']
        buttons['key_icon'] = i['key_icon']
        buttons['key_text'] = i['key_text']
        buttons['key_code'] = i['key_code']
        buttons['key_event'] = i['key_event']
        buttons['key_status'] = "disabled"
        buttons_list.append(dict(buttons))
    return buttons_list

# create layout
def create_layout( sg ,  btn_list , journal_list , general):
    layout = []
    title_list = []
    system_list = []
    buttons_list = []

    title_list.append(sg.Image(data=output.loadered, key="-JICON-", enable_events = True, pad=((35,35),(0,0))))
    title_list.append(sg.Text(text=journal_list[1], key="-JDATE-",  enable_events = True, pad=(1,1),auto_size_text = False, size=(10,2),font=general.font,justification='center'))
    title_list.append(sg.Text(text=journal_list[2], key="-JEVENT-",  enable_events = True, pad=(1,1), size=(20,3),font=general.font_bold,justification='center'))
    title_list.append(sg.Text(text=journal_list[3], key="-JTEXT-",  enable_events = True, pad=(1,1) ,size=(65,3), expand_x=True,font=general.font_bold,justification='left'))
    layout.append(title_list)

    # Create buttons
    for idx, i in enumerate(btn_list):
        key = i['key_name']
        image_filename = general.icons_path + i['key_icon'] + "-" + i['key_status'] + ".png"
        image_subsample = general.image_scale
        button_text = i['key_text']
        buttons_list.append(sg.Button(key = key, button_color = general.button_color, mouseover_colors=('white',sg.theme_background_color()), border_width=general.border_width, image_filename=image_filename, image_subsample = image_subsample, button_text = button_text, pad = general.pad, expand_x = general.button_resize))
        if (idx + 1 ) % general.row_max_buttons == 0:
            layout.append(list(buttons_list))
            buttons_list.clear()
    layout.append(list(buttons_list))

    system_list.append(sg.Image(data=output.loadered, key="A0",  enable_events = True, pad = 0))
    layout.append(system_list)
    return layout

def write_keycode(keycode):
    try:
        with open('/dev/hidg0', 'rb+') as fd:
            fd.write(keycode.encode())
            fd.close()
    except:
        display_message( sg , "Keboard interface not acvite!\nCable not connected?", 5 )

def update_buttons(btn_list, btn_list_prev, general,window):
    for idx,i in enumerate(btn_list):
        if i['key_status'] != btn_list_prev[idx]['key_status']:
            window[i['key_name']].update(image_filename = general.icons_path + i['key_icon'] + "-" + i['key_status'] + ".png" , button_color = general.button_color, image_subsample = general.image_scale)
            btn_list_prev[idx]['key_status'] = btn_list[idx]['key_status']

def update_journal(journal_list, last_journal, general, window):
    if(journal_list[0] != "0"):
        image_url = r'http://' + general.edd_addr + '/journalicons/' + journal_list[0] + '.png'
        file_name = "/tmp/" + journal_list[0] + ".png"
        if not os.path.exists(file_name):
            print("File " + file_name + " doesn't exist. Downloading")
            urllib.request.urlretrieve(image_url, file_name)
        window['-JICON-'].update(data=resize_image(file_name,resize=(50,50)))
    else:
        window["-JICON-"].update(output.loadered)

    journal_date = journal_list[1][:-1].replace("T","\n")
    window["-JDATE-"].update(journal_date,text_color=general.button_font_color)
    journal_event = "\n" + journal_list[2] if len(journal_list[2]) < 20 else journal_list[2]
    window["-JEVENT-"].update(journal_event, text_color=general.button_font_color)

    journal_message = "\n" + journal_list[3] if len(journal_list[3]) < 65 else journal_list[3]
    window["-JTEXT-"].update(journal_message,text_color=general.button_font_color)

def create_text(sg , general, text, size, pad=(5, 8)):
    return sg.Text(text, pad=pad, size = size, font=general.font_bold, background_color=general.button_font_color, text_color = "black", expand_x=True)

def create_key(sg, general, key, size, pad=(5, 8)):
    return sg.Input(default_text="None", pad=pad ,font=general.font, size=size, key=key, disabled_readonly_background_color="#000000", text_color=general.button_font_color, use_readonly_for_disable=True, readonly=True, expand_x=True)

def create_row(sg , general, text,key):
    return [ create_text(sg, general, text, (15,1)), create_key(sg, general, key, (45,1)) ]

def create_status_layout( sg , btn_list , journal_list , general):
    layout_status = [
        create_row(sg, general , "System Name","System"),
        create_row(sg ,general , "Visits","VisitCount"),
        [ sg.HSeparator(color=general.button_font_color, pad=(5,8)) ],
        create_row(sg, general , "Allegiance","Allegiance"),
        create_row(sg ,general , "Government","Gov"),
        create_row(sg, general , "Economy","Economy"),
        create_row(sg ,general , "Faction","Faction"),
        create_row(sg ,general , "Security","Security"),
        [ sg.HSeparator(color=general.button_font_color, pad=(5,8)) ],
        create_row(sg, general , "Ship","Ship"),
        [ create_text(sg, general , "Fuel",(4,1)), create_key(sg, general , "Fuel",(5,1)),
          create_text(sg, general , "Range",(5,1)), create_key(sg, general , "Range",(5,1)),
          create_text(sg, general , "Tank Size",(9,1)), create_key(sg, general , "TankSize",(5,1))],
        [ create_text(sg, general , "Micro Resources",(15,1)), create_key(sg, general , "MicroResources",(5,1)),
          create_text(sg, general , "Cargo",(5,1)), create_key(sg, general , "Cargo",(5,1))],
        [ create_text(sg, general , "Data",(15,1)), create_key(sg, general , "Data",(5,1)),
          create_text(sg, general , "Materials",(9,1)), create_key(sg, general , "Materials",(5,1))],
        [ sg.HSeparator(color=general.button_font_color, pad=(5,8))],
        [ sg.Text( "Travel" , pad=(5,(8,0)), size = (50,1),font=general.font_bold,background_color=general.button_font_color,text_color = "black", justification='c',expand_x=True)],
        [ create_text(sg, general , "Dist",(4,1),((5,0),(1,8))), create_key(sg, general , "Dist",(5,1),((0,0),(1,8))),
          create_text(sg, general , "Jumps",(5,1),((0,0),(1,8))), create_key(sg, general , "Jumps",(5,1),((0,0),(1,8))),
          create_text(sg, general , "Time",(4,1),((0,0),(1,8))), create_key(sg, general , "Time",(5,1),((0,5),(1,8)))]
    ]

    layout_controls = [
        create_row(sg, general , "Commander", "Commander"),
        create_row(sg, general , "Body Name", "Bodyname"),
        create_row(sg, general , "Credits", "Credits"),
        [ create_text(sg, general , "Game Mode",(8,1)), create_key(sg, general , "GameMode",(5,1)),
          create_text(sg, general , "Mode",(4,1)), create_key(sg, general , "Mode",(5,1))],
        [ sg.Text( "Distance" , pad=(5,(8,0)), size = (50,1),font=general.font_bold,background_color=general.button_font_color,text_color = "black", justification='c',expand_x=True)],
        [ create_text(sg, general , "Home",(4,1),((5,0),(1,8))), create_key(sg, general , "HomeDist",(5,1),((0,0),(1,8))),
          create_text(sg, general , "SOL",(3,1),((0,0),(1,8))), create_key(sg, general , "SolDist",(5,1),((0,5),(1,8)))]
    ]

    layout = [
        [sg.Column(layout_status, vertical_alignment='top'), sg.VSeparator(color=general.button_font_color), sg.Column(layout_controls, vertical_alignment='top')]
    ]

    return layout

def status_update(status, general, window):
        for i in [ 'System' , 'VisitCount' ]:
            if(window[i].get() != status.SystemData[i]):
                window[i].update(value=status.SystemData[i])

        for i in [ 'Allegiance' , 'Gov' , 'Economy' , 'Faction' , 'Security' ]:
            if(window[i].get() != status.EDDB[i]):
                window[i].update(value=status.EDDB[i])

        for i in [ 'Ship', 'Fuel', 'Range', 'TankSize', 'Cargo', 'Data', 'Materials', 'MicroResources' ]:
            if(window[i].get() != status.Ship[i]):
                window[i].update(value=status.Ship[i])

        for i in [ 'Dist' , 'Jumps' , 'Time' ]:
            if(window[i].get() != status.Travel[i]):
                window[i].update(value=status.Travel[i])

        for i in [ "Bodyname", "HomeDist", "SolDist", "GameMode", "Credits", "Commander", "Mode" ]:
            if(window[i].get() != status.Other[i]):
                window[i].update(value=status.Other[i])
