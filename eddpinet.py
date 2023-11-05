from eddpiutils import display_message
import PySimpleGUI as sg
import json
import copy

def request_status(ws):
    status_request = b'{\"requesttype\":\"status\",\"entry\":-1}'
    ws.send(status_request)
    indicator_request = b'{\"requesttype\":\"indicator\"}'
    ws.send(indicator_request)


def on_message(ws, message, btn_list, journal_list, status, indicator):
    gui_events = ["TargetPanel", "CommsPanel", "RolePanel", "SystemPanel", "SystemMap", "GalaxyMap", "FSSMode", "FSD", "None"]
    fsd_events = ["Supercruise", "FsdCharging", "FsdJump"]
    eddm = json.loads(message[0:])
    if eddm["responsetype"] == "journalpush":
#this should be list of lists but for now just use the lastone
        for row in eddm["rows"]:
            for idx,i in enumerate(row):
                journal_list[idx] = i

    if eddm["responsetype"] in ["indicatorpush","indicator"]:
        indicator.update(eddm)
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

    if eddm["responsetype"] in ["status"]:
        status.update(eddm)

def on_error(ws, error):
    display_message( sg, "Unable to connect to EDDiscovery.\n[ "+ str(error) + " ]\n\nReconnecting...\n", 3 )
    print(error)

def on_close(ws, close_status_code, close_msg):
    display_message( sg, "Connection to EDDiscovery closed\n", 3 )
    print("### closed ###")

def on_open(ws, btn_list):
    for i in btn_list:
        i['key_status']="normal"
    display_message( sg , "Connected to EDDiscovery\n", 2 )
    print("Opened connection")
    request_status(ws)