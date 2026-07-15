from __future__ import annotations

import json

import inquirer
import requests
from termcolor import colored

from models import Channel
from validators import inquirer_mhz_frequency_validator

def get_schema(name):
    with open(f"form_schemas/{name}.json", "r") as f:
        return json.load(f)
    


def add_repeater(codeplug, channel):
    callsign = input("Repeater Callsign: ").strip()

    codeplug["channels"].sort(key=lambda x: x.no_)

    response_data = None
    try:
        response = requests.get(f'https://api-beta.rsgb.online/callsign/{callsign.lower()}', timeout=2)
        try:
            if response.json()["data"] is not None:
                response_data = response.json()["data"][0]
                if "ctcss" in response_data:
                    response_data["ctcss"] = str(response_data["ctcss"])
                response_data["rx"] = str(response_data["rx"])
                response_data["tx"] = str(response_data["tx"])
        except requests.exceptions.JSONDecodeError:
            pass
        
    except requests.exceptions.ConnectTimeout:
        pass

    if response_data: # Define defaults
        cont = True
        if response_data["status"] == "NOT OPERATIONAL":
            print(colored("Repeater is reported as 'not operational'. Skip? [Y/n]", 'red'), end=" ")
            if input().strip().lower() != "n": cont = False
        elif response_data["status"] == "REDUCED OUTPUT":
            print(colored("Repeater is reported as 'reduced output'. Continue? [Y/n]", 'yellow'), end=" ")
            if input().strip().lower() != "n": cont = True

        if "A" not in response_data["modeCodes"] and not any(mode.startswith("M") for mode in response_data["modeCodes"]):
            print(colored("Repeater is not listed as supporting FM or DMR. Skip? [Y/n]", 'red'), end=" ")
            if input().strip().lower() != "n": cont = False

        if not cont:
            return codeplug

        default_channel_name = f"{response_data['repeater'].upper()} {response_data['town'].capitalize()}"
        default_receive_frequency = float(response_data['tx'])/1000000
        default_transmit_frequency = float(response_data["rx"])/1000000
        
        if "A" in response_data["modeCodes"] and any(mode.startswith("M") for mode in response_data["modeCodes"]):
            default_channel_type = "A+D TX A"
        elif "A" in response_data["modeCodes"]:
            default_channel_type = "A-Analog"
        else:
            default_channel_type = "D-Digital"

        default_transmit_power = "Mid"
        default_band_width = f"{response_data['txbw']}K"

        questions = [
            inquirer.Text("channel_name", 
                          message="Channel Name", 
                          default=default_channel_name,
                          ),

            # These next two are flipped - the radio's rx freq is the transmitter's tx, and vice versa
            inquirer.Text("receive_frequency",
                          message="Repeater's Transmit Freq. (MHz)",
                          default=default_receive_frequency,
                          validate=inquirer_mhz_frequency_validator
                          ),
            inquirer.Text("transmit_frequency",
                          message="Repeater's Receive Freq. (MHz)",
                          default=default_transmit_frequency,
                          validate=inquirer_mhz_frequency_validator
                          ),

            inquirer.List("channel_type",
                          message="Mode",
                          choices=[("Analogue", "A-Analog"), ("Digital", "D-Digital"), ("Analogue & Digital, TX on Analogue", "A+D TX A"), ("Digital and Analogue, TX on Digital", "D+A TX D")],
                          default=default_channel_type
                          ),

            inquirer.List("transmit_power",
                          message="Transmit Power",
                          choices=[("Low (1W)", "Low"),
                                     ("Medium (2.5W)", "Mid"),
                                     ("High (5W)", "High"), 
                                     ("Turbo (6W UHF/7W VHF)", "Turbo")],
                          default=default_transmit_power,
                          ),

            inquirer.List("band_width",
                          message="Bandwidth",
                          choices=["12.5K", "25K"],
                          default=default_band_width,
                          ),

            inquirer.Text("ctcss_dcs_decode",
                          message="CTCSS/DCS Decode",
                          default=response_data["ctcss"],
                          ),

            inquirer.Text("ctcss_dcs_encode",
                          message="CTCSS/DCS Encode",
                          default="{ctcss_dcs_decode}",
                          ),

            inquirer.Checkbox("zones",
                              message="Zones",
                              choices=[{"const": zone.zone_name, "title": f"{zone.no_}. {zone.zone_name}"} for zone in codeplug["zones"].values()] + [{"const": "", "title": "None"}],
                              default=[""],
                              ),

            inquirer.Checkbox("scan_list",
                              message="Scan List",
                              choices=[{"const": sl.scan_list_name, "title": f"{sl.no_}. {sl.scan_list_name}"} for sl in codeplug["scan_lists"].values()] + [{"const": "", "title": "None"}],
                              default=[""],
                              ),

            inquirer.Text("no_",
                          message="Channel Number",
                          default = codeplug["channels"][-3].no_ +1,
                          )

        ]

    answers = inquirer.prompt(questions)
    print(answers)

    new_channel = Channel()

    for key in [key for key in answers.keys() if key in str_qs and key != "zones"]:
        setattr(new_channel, key, answers[key])
    for key in [key for key in answers.keys() if key in int_qs]:
        setattr(new_channel, key, int(answers[key]))
    for key in [key for key in answers.keys() if key in float_qs]:
        setattr(new_channel, key, float(answers[key]))
    for key in [key for key in answers.keys() if key in bool_qs]:
        setattr(new_channel, key, answers[key])

    for channel in [ch for ch in codeplug["channels"] if ch.no_ >= new_channel.no_ and ch.no_ < 4001]:
        channel.no_ += 1

    codeplug["channels"].append(new_channel)
    codeplug["channels"].sort(key=lambda x: x.no_)

    return codeplug
