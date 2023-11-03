from PIL import Image, ImageTk, ImageSequence
from eddpiutils import resize_image,str2bool, display_message,load_buttons,create_layout
from eddpiconfig import Config
import PySimpleGUI as sg
import time
import json
import websocket
import _thread
import rel
import urllib.request
import output
import os
import copy

def write_keycode(keycode):
    try:
        with open('/dev/hidg0', 'rb+') as fd:
            fd.write(keycode.encode())
            fd.close()
    except:
        display_message( sg , "Keboard interface not acvite!\nCable not connected?", 5 )

#++Rcv decoded: fin=1 opcode=1 data=b'{"responsetype":"indicatorpush","ShipType":"MainShip","Mode":"MainShipDockedStarPort","GUIFocus":"NoFocus","Pips":[2.0,4.0,0.0],"ValidPips":true,"Lights":false,"Firegroup":1,"HasLatLong":false,"Position":[-999999.0,-999999.0,-999999.0,-999999.0],"ValidPosition":false,"ValidAltitude":false,"ValidHeading":false,"AltitudeFromAverageRadius":false,"PlanetRadius":-999999.0,"ValidPlanetRadius":false,"Docked":true,"Landed":false,"LandingGear":true,"ShieldsUp":true,"Supercruise":false,"FlightAssist":false,"HardpointsDeployed":false,"InWing":false,"CargoScoopDeployed":false,"SilentRunning":false,"ScoopingFuel":false,"SrvHandbrake":false,"SrvTurret":false,"SrvUnderShip":false,"SrvDriveAssist":false,"SrvHighBeam":false,"FsdMassLocked":true,"FsdCharging":false,"FsdCooldown":false,"FsdJump":false,"LowFuel":false,"OverHeating":false,"IsInDanger":false,"BeingInterdicted":false,"HUDInAnalysisMode":true,"NightVision":false,"GlideMode":false,"LegalState":"Clean","BodyName":null,"AimDownSight":false,"BreathableAtmosphere":false,"Oxygen":-1.0,"Gravity":-1.0,"Health":-1.0,"Temperature":-1.0,"TemperatureState":"Normal","SelectedWeapon":null,"SelectedWeaponLocalised":""}'

def on_message(ws, message):
    global journal_list
    global indicator_dict
    global btn_list
    gui_events = ["TargetPanel", "CommsPanel", "RolePanel", "SystemPanel", "SystemMap", "GalaxyMap", "FSSMode", "FSD", "None"]
    fsd_events = ["Supercruise", "FsdCharging", "FsdJump"]
    eddm = json.loads(message[0:])
    if eddm["responsetype"] == "journalpush":
        for row in eddm["rows"]:
            journal_list = row.copy()

    if eddm["responsetype"] in ["indicatorpush","indicator"]:
        journal_dict = eddm.copy()
        for idx,i in enumerate(btn_list):
            if i['key_event'] not in gui_events:
                btn_list[idx]['key_status']="active" if eddm[i['key_event']] else "normal"
            elif i['key_event'] in gui_events:
                btn_list[idx]['key_status']="active" if eddm["GUIFocus"]==i['key_event'] else "normal"
            else:
                btn_list[idx]['key_status']="normal"
            for j in fsd_events:
                if eddm[j] and i['key_event'] == "FSD":
                    btn_list[idx]['key_status']="active"



def on_error(ws, error):
    display_message( sg, "Unable to connect to EDDiscovery.\n[ "+ str(error) + " ]\n\nReconnecting...\n", 3 )
    print(error)

def on_close(ws, close_status_code, close_msg):
    display_message( sg, "Connection to EDDiscovery closed\n", 3 )
    print("### closed ###")

def on_open(ws):
    for i in btn_list:
        i['key_status']="normal"
    display_message( sg , "Connected to EDDiscovery\n", 2 )
    print("Opened connection")
    status_request = b'{\"requesttype\":\"status\",\"entry\":-1}'
    ws.send(status_request)
    indicator_request = b'{\"requesttype\":\"indicator\"}'
    ws.send(indicator_request)

def update_buttons(btn_list, btn_list_prev):
    for idx,i in enumerate(btn_list):
        if i['key_status'] != btn_list_prev[idx]['key_status']:
            window[i['key_name']].update(image_filename = general.icons_path + i['key_icon'] + "-" + i['key_status'] + ".png" , button_color = general.button_color, image_subsample = general.image_scale)
            print(i['key_status'] + " - " + btn_list_prev[idx]['key_status'])
            btn_list_prev[idx]['key_status'] = btn_list[idx]['key_status']

def update_journal(journal_list, last_journal):
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


NULL_CHAR = chr(0)
# Empty layout lists
journal_list = ["0", "0000-00-00T00:00:00Z", "Awaiting Events", "No Messages", ""]
indicator_dict = {}
layout = []

# Read config
f = open('config.json')
jdata = json.load(f)

# Load theme 

general = Config(jdata , sg)
print(general.deck_theme)
sg.theme(str(general.deck_theme))

#load buttons
btn_list = load_buttons(jdata)
btn_list_prev = copy.deepcopy(btn_list)

#create layout
create_layout(sg, layout , btn_list, journal_list, general)

# Create Main Window, Enable titlebar and resize option for X11 support
window = sg.Window('Elite PiDeck', layout, no_titlebar=False, element_justification='c', resizable=True).Finalize()
window.move(0,10)
window.Maximize()
window.TKroot["cursor"] = "none"

lasttime = time.time()

websocket.enableTrace(True)
websocket.setdefaulttimeout(1)

ws = websocket.WebSocketApp("ws://" + general.edd_addr +"/",subprotocols=["EDDJSON"],on_open=on_open,on_message=on_message,on_error=on_error,on_close=on_close)
ws.run_forever(dispatcher=rel, reconnect=5)  # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
rel.signal(2, rel.abort)  # Keyboard Interrupt

#indicator_request = b'{\"requesttype\":\"status\",\"entry\":-1}'




last_journal = []


while True:
    update_buttons(btn_list, btn_list_prev)
    curtime = time.time()
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
        update_journal(journal_list, last_journal)
        last_journal = journal_list.copy()
# websocket update
    try:
        rel.loop()
    except:
        display_message( sg , "Unknown error. \nEDDiscovery disconnected?", 5 )

window.close()

