import io
import base64
import PIL
import time
import output

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
def create_layout( sg , layout , btn_list , journal_list , general):
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
