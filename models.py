from typing import Annotated
from typing import List
from typing import Union

from pydantic import BaseModel
from pydantic import BeforeValidator

from validators import tx_mhz_frequency_validator

class Channel(BaseModel):
    no_: int = -1,
    channel_name: str = "",
    receive_frequency: Annotated[float, BeforeValidator(float)] = 440.0,
    transmit_frequency: Annotated[float, BeforeValidator(tx_mhz_frequency_validator)] = 440.0,
    channel_type: str = "",
    transmit_power: str = "",
    band_width: str = "",
    ctcss_dcs_decode: Union[str|float] = 67.0,
    ctcss_dcs_encode: Union[str|float] = 67.0,
    contact: str = "",
    contact_call_type: str = "",
    contact_tg_dmr_id: int = 9,
    radio_id: str = "",
    busy_lock_tx_permit: str = "",
    squelch_mode: str = "",
    optional_signal: str = "",
    dtmf_id: int = 1,
    two_tone_id: int = 1,
    five_tone_id: int = 1,
    ptt_id: str = "",
    rx_color_code: int = 1
    slot: int = 1,
    scan_list: str = "",
    receive_group_list: str = "",
    ptt_prohibit: str = "",
    reverse: str = "",
    simplex_tdma: str = "",
    slot_suit: str = "",
    aes_digital_encryption: str = "",
    digital_encryption: str = "",
    call_confirmation: str = "",
    talk_around_simplex_: str = "",
    work_alone: str = "",
    custom_ctcss: float = 0,
    two_tone_decode: int = 1,
    ranging: str = "Off",
    through_mode: str = "",
    aprs_rx: str = "",
    analog_aprs_ptt_mode: str = "",
    digital_aprs_ptt_mode: str = "",
    aprs_report_type: str = "",
    digital_aprs_report_channel: int = 1,
    correct_frequency_hz_: int = 0,
    sms_confirmation: str = "",
    exclude_channel_from_roaming: int = 0,
    dmr_mode: int = 0,
    dataack_disable: int = 0,
    rfive_tonebot: int = 0,
    rfive_toneeot: int = 0,
    auto_scan: int = 0,
    ana_aprs_mute: int = 0,
    send_talker_alias: int = 0,
    anaaprstxpath: int = 0,
    arcfour_: int = 0,
    ex_emg_kind: int = 0,
    txcc: int = 0

class Zone(BaseModel):
    no_: int = -1,
    zone_name: str = "",
    zone_members: List[Channel] = [],
    a_channel: Channel = None,
    b_channel: Channel = None

class ScanList(BaseModel):
    no_: int = -1,
    scan_list_name: str = "",
    scan_list_members: List[Channel] = [],
    scan_mode: str = "Off",
    priority_channel_select: str = "Off",
    priority_channel_one: Union[Channel|None] = None,
    priority_channel_two: Union[Channel|None] = None,
    revert_channel: str = "Selected",
    look_back_time_a: float = 2.0,
    look_back_time_b: float = 2.0,
    dropout_delay_time: float = 3.1,
    dwell_time: float = 3.1

class TalkGroup(BaseModel):
    num: int = -1,
    radio_id: int = -1,
    name: str = "",
    call_type: str = "Group Call",
    call_alert: str = "None"
