import PySimpleGUI as sg
import time
import json
import websocket
import _thread
import rel
import output
import copy
import functools

from PIL import Image, ImageTk, ImageSequence
from eddpiutils import resize_image,str2bool, display_message, load_buttons, create_layout, update_buttons, write_keycode, update_journal,create_status_layout,status_update
from eddpinet import on_error, on_close, on_message, on_open, request_status
from eddpimethods import Config,Status

if __name__ == '__main__':
    NULL_CHAR = chr(0)
    # Empty layout lists
    journal_list = ["0", "0000-00-00T00:00:00Z", "Awaiting Events", "No Messages", ""]
    last_journal = []
    indicator_dict = {}
    layout = []
    status_layout=[]

    # Read config
    f = open('config.json')
    jdata = json.load(f)

    # Load config and apply theme
    general = Config(jdata , sg)

    #load buttons
    btn_list = load_buttons(jdata)
    btn_list_prev = copy.deepcopy(btn_list)

    #create layout
    layout = create_layout(sg, btn_list, journal_list, general)

    # Create Main Window, Enable titlebar and resize option for X11 support
    window = sg.Window('Elite PiDeck Keys', layout, location=(0,10),no_titlebar=False, element_justification='c', resizable=True).Finalize()
    window.Maximize()
    window.TKroot["cursor"] = "none"

    status_layout = create_status_layout(sg, btn_list, journal_list, general)
    window_status = sg.Window('Elite PiDeck Status', status_layout, location=(1024,10),no_titlebar=False, element_justification='c', resizable=True).Finalize()
    window_status.Maximize()
    window_status.TKroot["cursor"] = "none"

    status = Status()

    # EDDiscovery websocket connection
    websocket.enableTrace(True)
    websocket.setdefaulttimeout(1)
    ws = websocket.WebSocketApp("ws://" + general.edd_addr +"/",subprotocols=["EDDJSON"],
                on_open=functools.partial(on_open,btn_list=btn_list),
                on_message=functools.partial(on_message, btn_list=btn_list, journal_list=journal_list,status=status),
                on_error=on_error,
                on_close=on_close)
    ws.run_forever(dispatcher=rel, reconnect=5)  # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
    rel.signal(2, rel.abort)  # Keyboard Interrupt

    lasttime = time.time()
#    last_status = time.time()
    while True:
        curtime = time.time()
#        if (curtime - last_status) > 1:
#            request_status(ws)
#            last_status = curtime

        update_buttons(btn_list, btn_list_prev,general,window)
        if(status.NeedsUpdate):
            status_update(status,general,window_status)
            status.ClearUpdate()

        event, values = window.read(timeout=100)
        for i in btn_list:
            if event == i['key_name']:
                write_keycode(NULL_CHAR*2 + chr(int(i['key_code'],16))+NULL_CHAR*5)
                time.sleep(general.key_release_delay)
                write_keycode(NULL_CHAR*8)
                lasttime = time.time()
        if event in (sg.WIN_CLOSED, 'A0', 'A1', 'A2'):
            break
        if(curtime - lasttime < 0.5):
            window["A0"].UpdateAnimation(output.loadered, time_between_frames=1)
        elif lasttime != 0 and (curtime - lasttime) > 0.5:
            window["A0"].update(output.loadered)
            lasttime = 0
        if(journal_list[0] == "0"):
            window["-JICON-"].UpdateAnimation(output.loadered, time_between_frames=1)
        if last_journal != journal_list:
            update_journal(journal_list, last_journal, general, window)
            last_journal = journal_list.copy()
    # websocket update
        try:
            rel.loop()
        except:
            display_message(sg, "Unknown error. \nEDDiscovery disconnected?", 5)

    window_status.close()
    window.close()

