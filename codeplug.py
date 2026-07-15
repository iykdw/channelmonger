import csv
from typing import Dict
from typing import List

from models import Channel
from models import ScanList
from models import TalkGroup
from models import Zone

def header2key(key: str):
    key = key.lower()

    replace_with_underscores = [" ", "/", "(", ")", "[", "]", "."]
    other_replaces = [("2", "two_"), ("5", "five_"), ("4", "four_")]

    for repval in replace_with_underscores:
        key = key.replace(repval, "_")

    for repset in other_replaces:
        key = key.replace(repset[0], repset[1])

    return key

def loads(path):
    codeplug = {}

    with open("input/Channel.CSV", "r") as f:
        channels: List[Channel] = []
        channelreader = csv.DictReader(f)
        for channel_dict in channelreader:
            dc_channel = {}
            for key in channel_dict.keys():
                dc_channel[header2key(key)] = channel_dict[key]

            channel = Channel.model_validate(dc_channel)

            channels.append(channel)

        codeplug["channels"] = channels

    with open("input/Zone.CSV", "r") as f:
        zones: Dict[str, Zone] = {} 
        zonereader = csv.DictReader(f)
        for zone_dict in zonereader:
            channels = zone_dict["Zone Channel Member"].split("|")
            rx_freqs = [float(freq) for freq in zone_dict["Zone Channel Member RX Frequency"].split("|")]
            tx_freqs = [float(freq) for freq in zone_dict["Zone Channel Member TX Frequency"].split("|")]

            zone_channels = []
            a_channel = None
            b_channel = None
            for i in range(len(channels)): # Compile the list of Channel objects
                for channel in codeplug["channels"]:
                    if channel is not None and channel.channel_name == channels[i] and channel.receive_frequency == rx_freqs[i] and channel.transmit_frequency == tx_freqs[i]:
                        zone_channels.append(channel)

                    if channel is not None and channel.channel_name == zone_dict["A Channel"] and channel.receive_frequency == float(zone_dict["A Channel RX Frequency"]) and channel.transmit_frequency == float(zone_dict["A Channel TX Frequency"]):
                        a_channel = channel
                    if channel is not None and channel.channel_name == zone_dict["B Channel"] and channel.receive_frequency == float(zone_dict["B Channel RX Frequency"]) and channel.transmit_frequency == float(zone_dict["B Channel TX Frequency"]):
                        b_channel = channel


            if len(zone_channels) != len (channels):
                print("Could not match all channels!")

            if a_channel is None:
                print(f"Could not find A Channel '{zone_dict['A Channel']}' for zone {zone_dict['Zone Name']}")
            if b_channel is None:
                print(f"Could not find B Channel '{zone_dict['B Channel']}' for zone {zone_dict['Zone Name']}")
        
            zone = Zone(no_ = zone_dict["No."],
                        zone_name = zone_dict["Zone Name"],
                        zone_members = zone_channels,
                        a_channel = a_channel,
                        b_channel = b_channel
                        )

            zones[zone.zone_name] = zone

        codeplug["zones"] = zones

    with open("input/ScanList.CSV", "r") as f:
        codeplug["scan_lists"]: Dict[str, ScanList] = {}
        slreader = csv.DictReader(f)
        for sl_dict in slreader:
            members = sl_dict["Scan Channel Member"].split("|")
            rx_freqs = [float(freq) for freq in sl_dict["Scan Channel Member RX Frequency"].split("|")]
            tx_freqs = [float(freq) for freq in sl_dict["Scan Channel Member TX Frequency"].split("|")]

            sl_channels = []
            p1_channel = None
            p2_channel = None
            for i in range(len(members)):
                for channel in codeplug["channels"]:
                    if channel is not None and channel.channel_name == members[i] and channel.receive_frequency == rx_freqs[i] and channel.transmit_frequency == tx_freqs[i]:
                        sl_channels.append(channel)

                    if channel is not None and channel.channel_name == sl_dict["Priority Channel 1"] and channel.receive_frequency == float(sl_dict["Priority Channel 1 RX Frequency"]) and channel.transmit_frequency == float(sl_dict["Priority Channel 1 TX Frequency"]):
                        p1_channel = channel
                    if channel is not None and channel.channel_name == sl_dict["Priority Channel 2"] and channel.receive_frequency == float(sl_dict["Priority Channel 2 RX Frequency"]) and channel.transmit_frequency == float(sl_dict["Priority Channel 2 TX Frequency"]):
                        p2_channel = channel


            if len(sl_channels) != len (members):
                print("Could not match all channels!")

            if p1_channel is None and sl_dict["Priority Channel 1"] != "Off":
                print(f"Could not find Priority Channel 1 '{sl_dict['Priority Channel 1']}' for sl {sl_dict['Scan List Name']}")
            if p2_channel is None and sl_dict["Priority Channel 2"] != "Off":
                print(f"Could not find Priority Channel 2 '{sl_dict['Priority Channel 2']}' for sl {sl_dict['Scan List Name']}")

            sl = ScanList(no_ = sl_dict["No."],
                          scan_list_name = sl_dict["Scan List Name"],
                          scan_list_members = sl_channels,
                          scan_mode = sl_dict["Scan Mode"],
                          priority_channel_select = sl_dict["Priority Channel Select"],
                          priority_channel_one = p1_channel,
                          priority_channel_two = p2_channel,
                          revert_channel = sl_dict["Revert Channel"],
                          look_back_time_a = sl_dict["Look Back Time A[s]"],
                          look_back_time_b = sl_dict["Look Back Time B[s]"],
                          dropout_delay_time = sl_dict["Dropout Delay Time[s]"],
                          dwell_time = sl_dict["Dwell Time[s]"]
                          )

            codeplug["scan_lists"][sl.scan_list_name] = sl

    with open("input/TalkGroups.CSV", "r") as f:
        codeplug["talkgroups"]: Dict[str, TalkGroup] = {}
        tgreader = csv.DictReader(f)
        for tg_dict in tgreader:
            tg = TalkGroup(num = tg_dict["No."],
                           radio_id = tg_dict["Radio ID"],
                           name = tg_dict["Name"],
                           call_type = tg_dict["Call Type"],
                           call_alert = tg_dict["Call Alert"]
                           )
                           
            codeplug["talkgroups"][tg.name] = tg

    return codeplug

def dumps(path, codeplug):
    with open("output/Channel.CSV", "w") as f:
        fieldnames = []
        fieldnames.append("No.")
        fieldnames.append("Channel Name")
        fieldnames.append("Receive Frequency")
        fieldnames.append("Transmit Frequency")
        fieldnames.append("Channel Type")
        fieldnames.append("Transmit Power")
        fieldnames.append("Band Width")
        fieldnames.append("CTCSS/DCS Decode")
        fieldnames.append("CTCSS/DCS Encode")
        fieldnames.append("Contact")
        fieldnames.append("Contact Call Type")
        fieldnames.append("Contact TG/DMR ID")
        fieldnames.append("Radio ID")
        fieldnames.append("Busy Lock/TX Permit")
        fieldnames.append("Squelch Mode")
        fieldnames.append("Optional Signal")
        fieldnames.append("DTMF ID")
        fieldnames.append("2Tone ID")
        fieldnames.append("5Tone ID")
        fieldnames.append("PTT ID")
        fieldnames.append("RX Color Code")
        fieldnames.append("Slot")
        fieldnames.append("Scan List")
        fieldnames.append("Receive Group List")
        fieldnames.append("PTT Prohibit")
        fieldnames.append("Reverse")
        fieldnames.append("Simplex TDMA")
        fieldnames.append("Slot Suit")
        fieldnames.append("AES Digital Encryption")
        fieldnames.append("Digital Encryption")
        fieldnames.append("Call Confirmation")
        fieldnames.append("Talk Around(Simplex)")
        fieldnames.append("Work Alone")
        fieldnames.append("Custom CTCSS")
        fieldnames.append("2TONE Decode")
        fieldnames.append("Ranging")
        fieldnames.append("Through Mode")
        fieldnames.append("APRS RX")
        fieldnames.append("Analog APRS PTT Mode")
        fieldnames.append("Digital APRS PTT Mode")
        fieldnames.append("APRS Report Type")
        fieldnames.append("Digital APRS Report Channel")
        fieldnames.append("Correct Frequency[Hz]")
        fieldnames.append("SMS Confirmation")
        fieldnames.append("Exclude channel from roaming")
        fieldnames.append("DMR MODE")
        fieldnames.append("DataACK Disable")
        fieldnames.append("R5toneBot")
        fieldnames.append("R5ToneEot")
        fieldnames.append("Auto Scan")
        fieldnames.append("Ana Aprs Mute")
        fieldnames.append("Send Talker Alias")
        fieldnames.append("AnaAprsTxPath")
        fieldnames.append("ARC4")
        fieldnames.append("ex_emg_kind")
        fieldnames.append("TxCC")
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for channel in codeplug["channels"]:
            out_dict = {}
            out_dict["No."] = channel.no_
            out_dict["Channel Name"] = channel.channel_name
            out_dict["Receive Frequency"] = channel.receive_frequency
            out_dict["Transmit Frequency"] = channel.transmit_frequency
            out_dict["Channel Type"] = channel.channel_type
            out_dict["Transmit Power"] = channel.transmit_power
            out_dict["Band Width"] = channel.band_width
            out_dict["CTCSS/DCS Decode"] = channel.ctcss_dcs_decode
            out_dict["CTCSS/DCS Encode"] = channel.ctcss_dcs_encode
            out_dict["Contact"] = channel.contact
            out_dict["Contact Call Type"] = channel.contact_call_type
            out_dict["Contact TG/DMR ID"] = channel.contact_tg_dmr_id
            out_dict["Radio ID"] = channel.radio_id
            out_dict["Busy Lock/TX Permit"] = channel.busy_lock_tx_permit
            out_dict["Squelch Mode"] = channel.squelch_mode
            out_dict["Optional Signal"] = channel.optional_signal
            out_dict["DTMF ID"] = channel.dtmf_id
            out_dict["2Tone ID"] = channel.two_tone_id
            out_dict["5Tone ID"] = channel.five_tone_id
            out_dict["PTT ID"] = channel.ptt_id
            out_dict["RX Color Code"] = channel.rx_color_code
            out_dict["Slot"] = channel.slot
            out_dict["Scan List"] = channel.scan_list
            out_dict["Receive Group List"] = channel.receive_group_list
            out_dict["PTT Prohibit"] = channel.ptt_prohibit
            out_dict["Reverse"] = channel.reverse
            out_dict["Simplex TDMA"] = channel.simplex_tdma
            out_dict["Slot Suit"] = channel.slot_suit
            out_dict["AES Digital Encryption"] = channel.aes_digital_encryption
            out_dict["Digital Encryption"] = channel.digital_encryption
            out_dict["Call Confirmation"] = channel.call_confirmation
            out_dict["Talk Around(Simplex)"] = channel.talk_around_simplex_
            out_dict["Work Alone"] = channel.work_alone
            out_dict["Custom CTCSS"] = channel.custom_ctcss
            out_dict["2TONE Decode"] = channel.two_tone_decode
            out_dict["Ranging"] = channel.ranging
            out_dict["Through Mode"] = channel.through_mode
            out_dict["APRS RX"] = channel.aprs_rx
            out_dict["Analog APRS PTT Mode"] = channel.analog_aprs_ptt_mode
            out_dict["Digital APRS PTT Mode"] = channel.digital_aprs_ptt_mode
            out_dict["APRS Report Type"] = channel.aprs_report_type
            out_dict["Digital APRS Report Channel"] = channel.digital_aprs_report_channel
            out_dict["Correct Frequency[Hz]"] = channel.correct_frequency_hz_
            out_dict["SMS Confirmation"] = channel.sms_confirmation
            out_dict["Exclude channel from roaming"] = channel.exclude_channel_from_roaming
            out_dict["DMR MODE"] = channel.dmr_mode
            out_dict["DataACK Disable"] = channel.dataack_disable
            out_dict["R5toneBot"] = channel.rfive_tonebot
            out_dict["R5ToneEot"] = channel.rfive_toneeot
            out_dict["Auto Scan"] = channel.auto_scan
            out_dict["Ana Aprs Mute"] = channel.ana_aprs_mute
            out_dict["Send Talker Alias"] = channel.send_talker_alias
            out_dict["AnaAprsTxPath"] = channel.anaaprstxpath
            out_dict["ARC4"] = channel.arcfour_
            out_dict["ex_emg_kind"] = channel.ex_emg_kind
            out_dict["TxCC"] = channel.txcc

            writer.writerow(out_dict)
