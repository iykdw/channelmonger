from __future__ import annotations

import json

from texttable import Texttable

import codeplug as plug
from add_repeater import add_repeater
from models import Channel

def main():
    codeplug = plug.loads("input/")

    with open("defaults.json", "r") as f:
        defaults = json.loads(f.read())


    print("""Welcome to Channelmonger!

    Please select from the menu:
    1) View Channels
    2) View Zones
    3) View Scan Lists
    4) Add Repeater

    """)
    choice = input().strip()
    if choice == "1":
        t = Texttable()
        t.add_rows([["Number", "Name", "RX Freq", "TX Freq", "Type"]]+[[channel.no_, channel.channel_name, channel.receive_frequency, channel.transmit_frequency, channel.channel_type] for channel in codeplug["channels"] if channel is not None])
        print(t.draw())
    elif choice == "4":
        new_channel = Channel.model_validate(defaults["channel"], strict=True)
        codeplug = add_repeater(codeplug, new_channel)
        plug.dumps("output", codeplug)

if __name__ == "__main__":
    main()
