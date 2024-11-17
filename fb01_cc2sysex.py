# Yamaha FB-01 CC to SysEx conversion script
# Version 1.0
# by Brandon Blume, Nov 13, 2024
# shine62 _AT= gmail )DOT{ calm
#
# This script reads MIDI message from an input port and passes them through to an output port. If CC
# messages are sent through that correspond to the (currently hardcoded) mapped CCs for setting voice,
# instrument, config, or system data parameters on the FB-01 it will convert the values of those
# intercepted CC messages into the proper sysex messages.
#
# CURRENT STATE:
#
# This script is currently still unfinished. Its basic functions work (please report any bugs if you run 
# into any!) but further plans include sending an initial dump request for the currently selected voice
# on the FB-01 so that you can modify any voice you currently have already. Right now it will start with a
# default blank slate "INIT" voice but there isn't currently any implementation to let the FB-01 know that 
# either. Which means any modifications to parameters will be done in context with the "INIT" voice and you 
# could see parameters reset to zero (or whatever I set the defaults to) that share sysex messages with 
# other parameters that you modify. Meaning you'll have to set those again. Implementing a voice dump 
# request from the FB-01 means that there would need to be two MIDI input ports; one for the MIDI controller 
# and one to act as the return port for dumps from the FB-01.
#
# I also want to dedicate a MIDI CC# to manually triggering a dump from the FB-01 at any time and another
# CC# for sending the default blank slate "INIT" instrument to the FB-01 to guarantee that everything is
# in sync. There's no checking for any of this currently.
#
# The current hardcoded map for CC numbers to FB-01 parameter change sysex messages are listed below.
# CC's that the FB-01 already understands are marked with square brackets "[]". They are not converted and
# are passed "thru" without any additional processing directly to the FB-01. Notes and other MIDI messages 
# are also sent "thru" unchanged.
#
# CC #     |        FB-01 Parameter Sysex Message          |     Value range
# CC   0      System: Memory Protect (toggle)                  0 / 127 (0=off, 127=on)
# CC  [1]     [Mod Wheel]                                      0 ~ 127
# CC  [2]     [Breath]                                         0 ~ 127
# CC   3      Config: Combine Mode (toggle)                    0 / 127 (0=off, 127=on)
# CC  [4]     [Foot Controller]                                0 ~ 127
# CC  [5]     [Portamento Time]                                0 ~ 127
# CC   6      Config: Name (Char #1)                           0 ~ 127
# CC  [7]     [Channel Volume]                                 0 ~ 127
# CC   8      Config: Name (Char #2)                           0 ~ 127
# CC   9      Config: Name (Char #3)                           0 ~ 127
# CC [10]     [Pan]                                            0 / 63 / 127 (0=L, 64=LR, 127=R)
# CC  11      Config: Name (Char #4)                           0 ~ 127
# CC  12      Config: Name (Char #5)                           0 ~ 127
# CC  13      Config: Name (Char #6)                           0 ~ 127
# CC  14      Config: Name (Char #7)                           0 ~ 127
# CC  15      Config: Name (Char #8)                           0 ~ 127
# CC  16      Voice: Load LFO                                  0 / 127 (0=off, 127=on)
# CC  17      Voice: AMD                                       0 ~ 127
# CC  18      Voice: LFO Sync to Note On (toggle)              0 / 127 (0=off, 127=on)
# CC  19      Voice: PMD                                       0 ~ 127
# CC  20      Voice: Toggle Operator 1                         0 / 127 (0=off, 127=on)
# CC  21      Voice: Toggle Operator 2                         0 / 127 (0=off, 127=on)
# CC  22      Voice: Toggle Operator 3                         0 / 127 (0=off, 127=on)
# CC  23      Voice: Toggle Operator 4                         0 / 127 (0=off, 127=on)
# CC  24      Voice: Set Algorithm                             0 ~ 7
#                                                                     0 = 4 -> 3 -> 2 -> 1
#                                                                     1 = (4+3) -> 2 -> 1
#                                                                     2 = (4+(3 -> 2)) -> 1
#                                                                     3 = ((4 -> 3) +2) ->1
#                                                                     4 = (4 -> 3) + (2 -> 1)
#                                                                     5 = 4 -> (3+2+1)
#                                                                     6 = (4 -> 3)+2+1
#                                                                     7 = 4+3+2+1
# CC  25      Voice: Feedback Level                            0 ~ 7
# CC  26      Voice: PMS                                       0 ~ 7
# CC  27      Voice: AMS                                       0 ~ 3
# CC  28      Voice: Set LFO Waveform                          0 ~ 3 (0=Saw, 1=Sqr, 2=Tri, 3=Noise)
# CC  29      Voice: PMD Assign                                0 ~ 4 (0=None, 1=Aftertouch, 2=Mod Wheel, 3=Breath, 4=Foot Controller)
# CC  30      Voice: Transpose                                 -128 ~ +127 (signed, technically the values can be 0 ~ 255 but since CC values onyl go to 127 this script is programmed to interpret CC values 0 ~ 24 as "-24 ~ -1" and 25 ~ 49 as "0 ~ +24")
# CC  31      Voice: Pitch Bend Range                          0 ~ 12
# CC  32      Op1: TL (Total Level)                            0 ~ 127
# CC  33      Op1: Key Height/TL scaling type (-/+)            0 / 127 (0=off, 127=on)
# CC  34      Op1: Key Height/TL scaling type (Lin/Exp)        0 / 127 (0=off, 127=on)
# CC  35      Op1: Key Velocity/TL sensitivity                 0 ~ 7
# CC  36      Op1: Key Height/Envelope Lvl scaling dpth        0 ~ 15
# CC  37      Op1: TL Fine Adjust                              0 ~ 15
# CC  38      Op1: Detune 1 (Coarse)                           0 ~ 7 (0 & 4=0, 1~3 = -3 ~ -1, 5~7 = +1 ~ +3)
# CC  39      Op1: Freq Multiplier/Detune 2 (Fine)             0 ~ 63 (see Multi/DT2 Tuple table below for CC value/freq multiple reference)
# CC  40      Op1: Key Height/Envelope Rt scaling dpth         0 ~ 3
# CC  41      Op1: AR (Attack Rate)                            0 ~ 31
# CC  42      Op1: Toggle AM (Amplitude Modulation)            0 / 127 (0=off, 127=on)
# CC  43      Op1: Key Velocity/Attack Rate sensitivity        0 ~ 3
# CC  44      Op1: D1R (Decay 1 Rate)                          0 ~ 31
# CC  45      Op1: D2R (Decay 2 Rate)                          0 ~ 31
# CC  46      Op1: SL (Sustain Level)                          0 ~ 15
# CC  47      Op1: RR (Release Rate)                           0 ~ 15
# CC  48      Op2: TL (Total Level)                            0 ~ 127
# CC  49      Op2: Key Height/TL scaling type (-/+)            0 / 127 (0=off, 127=on)
# CC  50      Op2: Key Height/TL scaling type (Lin/Exp)        0 / 127 (0=off, 127=on)
# CC  51      Op2: Key Velocity/TL sensitivity                 0 ~ 7
# CC  52      Op2: Key Height/Envelope Lvl scaling dpth        0 ~ 15
# CC  53      Op2: TL Fine Adjust                              0 ~ 15
# CC  54      Op2: Detune 1 (Coarse)                           0 ~ 7
# CC  55      Op2: Freq Multi/Detune 2 (Fine)                  0 ~ 63 (see Multi/DT2 Tuple table below for CC value/freq multiple reference)
# CC  56      Op2: Key Height/Envelope Rt scaling dpth         0 ~ 15
# CC  57      Op2: AR (Attack Rate)                            0 ~ 31
# CC  58      Op2: Toggle AM (Amplitude Modulation)            0 / 127 (0=off, 127=on)
# CC  59      Op2: Key Velocity/Attack Rate sensitivity        0 ~ 3
# CC  60      Op2: D1R (Decay 1 Rate)                          0 ~ 31
# CC  61      Op2: D2R (Decay 2 Rate)                          0 ~ 31
# CC  62      Op2: SL (Sustain Level)                          0 ~ 15
# CC  63      Op2: RR (Release Rate)                           0 ~ 15
# CC [64]     [Damper Pedal on/off (Sustain)]                  0 / 127 (0=off, 127=on)
# CC [65]     [Portamento on/off              ]                0 / 127 (0=off, 127=on)
# CC [66]     [Sostenuto on/off]                               0 / 127 (0=off, 127=on)
# CC  67      Op3: TL (Total Level)                            0 ~ 127
# CC  68      Op3: Key Height/TL scaling type (-/+)            0 / 127 (0=off, 127=on)
# CC  69      Op3: Key Height/TL scaling type (Lin/Exp)        0 / 127 (0=off, 127=on)
# CC  70      Op3: Key Velocity/TL sensitivity                 0 ~ 7
# CC  71      Op3: Key Height/Envelope Lvl scaling dpth        0 ~ 15
# CC  72      Op3: TL Fine Adjust                              0 ~ 15
# CC  73      Op3: Detune 1 (Coarse)                           0 ~ 7
# CC  74      Op3: Freq Multiplier/Detune 2 (Fine)             0 ~ 63
# CC  75      Op3: Key Height/Envelope Rt scaling dpth         0 ~ 15
# CC  76      Op3: AR (Attack Rate)                            0 ~ 31
# CC  77      Op3: Toggle AM (Amplitude Modulation)            0 / 127 (0=off, 127=on)
# CC  78      Op3: Key Velocity/Attack Rate sensitivity        0 ~ 3
# CC  79      Op3: D1R (Decay 1 Rate)                          0 ~ 31
# CC  80      Op3: D2R (Decay 2 Rate)                          0 ~ 31
# CC  81      Op3: SL (Sustain Level)                          0 ~ 15
# CC  82      Op3: RR (Release Rate)                           0 ~ 15
# CC  83      Op4: TL (Total Level)                            0 ~ 127
# CC  84      Op4: Key Height/TL scaling type (-/+)            0 / 127 (0=off, 127=on)
# CC  85      Op4: Key Height/TL scaling type (Lin/Exp)        0 / 127 (0=off, 127=on)
# CC  86      Op4: Key Velocity/TL sensitivity                 0 ~ 7
# CC  87      Op4: Key Height/Envelope Lvl scaling dpth        0 ~ 15
# CC  88      Op4: TL Fine Adjust                              0 ~ 15
# CC  89      Op4: Detune 1 (Coarse)                           0 ~ 7
# CC  90      Op4: Freq Multiplier/Detune 2 (Fine)             0 ~ 63
# CC  91      Op4: Key Height/Envelope Rt scaling dpth         0 ~ 15
# CC  92      Op4: AR (Attack Rate)                            0 ~ 31
# CC  93      Op4: Toggle AM (Amplitude Modulation)            0 / 127 (0=off, 127=on)
# CC  94      Op4: Key Velocity/Attack Rate sensitivity        0 ~ 3
# CC  95      Op4: D1R (Decay 1 Rate)                          0 ~ 31
# CC  96      Op4: D2R (Decay 2 Rate)                          0 ~ 31
# CC  97      Op4: SL (Sustain Level)                          0 ~ 15
# CC  98      Op4: RR (Release Rate)                           0 ~ 15
# CC  99      Inst: # of notes                                 0 ~ 8
# CC 100      Inst: MIDI Channel                               0 ~ 15
# CC 101      Inst: KC Limit/L                                 0 ~ 127
# CC 102      Inst: KC Limit/H                                 0 ~ 127
# CC 103      Inst: Voice Bank                                 0 ~ 6
# CC 104      Inst: Voice #                                    0 ~ 47
# CC 105      Inst: Detune                                     0 ~ 127
# CC 106      Inst: Octave Transpose                           0 ~ 4 (-2 ~ +2)
# CC 107      Inst: Output Level                               0 ~ 127
# CC 108      Inst: Pan (L, L+R, R)                            0 ~ 127 (0=L, 64=LR, 127=R)
# CC 109      Inst: LFO Enable                                 0 / 127 (0=off, 127=on)
# CC 110      Inst: Pitch Bend Range                           0 ~ 12
# CC 111      System: Config Number                            0 ~ 19
# CC 112      System: Channel Number                           0 ~ 15
# CC 113      System: Master Detune                            0 ~ 127 (0~63 = 0~63, 64~127 = -64 ~ -1)
# CC 114          {currently unused}
# CC 115      Voice: LFO Speed                                 Relative Binary Offset (64 = 0, 64 + x = +x, 64 -x = -x)
# CC 116      Voice: Name (Char #1)                            0 ~ 127
# CC 117      Voice: Name (Char #2)                            0 ~ 127
# CC 118      Voice: Name (Char #3)                            0 ~ 127
# CC 119      Voice: Name (Char #4)                            0 ~ 127
# CC 120      Voice: Name (Char #5)                            0 ~ 127
# CC 121      Voice: Name (Char #6)                            0 ~ 127
# CC 122      Voice: Name (Char #7)                            0 ~ 127
# CC[123]     [All Notes Off]                                  0 / 127 (0=off, 127=on)
# CC 124      Voice: User Code                                 Relative Binary Offset (64 = 0, 64 + x = +x, 64 -x = -x)
# CC 125      System: Master Output Level                      0 ~ 127
# CC[126]     [Mono Mode on/Poly off/All Notes Off]            1
# CC[127]     [Poly Mode on/Mono off/All Notes Off]            0

from colorama import init, Fore, Back, Style
init()
import mido
from mido import Message
import time

# Tuple lookup table to determine linear consecutive frequencies for Multi/DT2 combined sysex messages (16 x 4)
freq_table = [
# Multi/DT2 Bytes   CC Value   Resulting Freq Multiple
    (0x00, 0x00),    #  0        x0.50
    (0x00, 0x04),    #  1        x0.71
    (0x00, 0x08),    #  2        x0.78
    (0x00, 0x0C),    #  3        x0.87
    (0x01, 0x00),    #  4        x1.00
    (0x01, 0x04),    #  5        x1.41
    (0x01, 0x08),    #  6        x1.57
    (0x01, 0x0C),    #  7        x1.73
    (0x02, 0x00),    #  8        x2.00
    (0x02, 0x04),    #  9        x2.82
    (0x03, 0x00),    # 10        x3.00
    (0x02, 0x08),    # 11        x3.14
    (0x02, 0x0C),    # 12        x3.46
    (0x04, 0x00),    # 13        x4.00
    (0x03, 0x04),    # 14        x4.24
    (0x03, 0x08),    # 15        x4.71
    (0x05, 0x00),    # 16        x5.00
    (0x03, 0x0C),    # 17        x5.19
    (0x04, 0x04),    # 18        x5.65
    (0x06, 0x00),    # 19        x6.00
    (0x04, 0x08),    # 20        x6.28
    (0x04, 0x0C),    # 21        x6.92
    (0x07, 0x00),    # 22        x7.00
    (0x05, 0x04),    # 23        x7.07
    (0x05, 0x08),    # 24        x7.85
    (0x08, 0x00),    # 25        x8.00
    (0x06, 0x04),    # 26        x8.48
    (0x05, 0x0C),    # 27        x8.65
    (0x09, 0x00),    # 28        x9.00
    (0x06, 0x08),    # 29        x9.42
    (0x07, 0x04),    # 30        x9.89
    (0x0A, 0x00),    # 31        x10.00
    (0x06, 0x0C),    # 32        x10.38
    (0x07, 0x08),    # 33        x10.99
    (0x0B, 0x00),    # 34        x11.00
    (0x08, 0x04),    # 35        x11.30
    (0x0C, 0x00),    # 36        x12.00
    (0x07, 0x0C),    # 37        x12.11
    (0x08, 0x08),    # 38        x12.56
    (0x09, 0x04),    # 39        x12.72
    (0x0D, 0x00),    # 40        x13.00
    (0x08, 0x0C),    # 41        x13.84
    (0x0E, 0x00),    # 42        x14.00
    (0x0A, 0x04),    # 43        x14.10
    (0x09, 0x08),    # 44        x14.13
    (0x0F, 0x00),    # 45        x15.00
    (0x0B, 0x04),    # 46        x15.55
    (0x09, 0x0C),    # 47        x15.57
    (0x0A, 0x08),    # 48        x15.70
    (0x0C, 0x04),    # 49        x16.96
    (0x0B, 0x08),    # 50        x17.27
    (0x0A, 0x0C),    # 51        x17.30
    (0x0D, 0x04),    # 52        x18.37
    (0x0C, 0x08),    # 53        x18.84
    (0x0B, 0x0C),    # 54        x19.03
    (0x0E, 0x04),    # 55        x19.78
    (0x0D, 0x08),    # 56        x20.41
    (0x0C, 0x0C),    # 57        x20.76
    (0x0F, 0x04),    # 58        x21.20
    (0x0E, 0x08),    # 59        x21.98
    (0x0D, 0x0C),    # 60        x22.49
    (0x0F, 0x08),    # 61        x23.55
    (0x0E, 0x0C),    # 62        x24.22
    (0x0F, 0x0C),    # 63        x25.95
]

input_ports = mido.get_input_names()
output_ports = mido.get_output_names()

print(f"\nMIDI Inputs:\n{input_ports}\n")
input_port = mido.open_input(input_ports[int(input("Select Controller Input: "))])

print(f"\nMIDI Outputs:\n{output_ports}\n")
output_port = mido.open_output(output_ports[int(input("Select Output: "))])

#print(f"\nInputs:\n{input_ports}\n")
#return_port = mido.open_input(input_ports[int(input("Select FB-01 Return: "))])

#print(f"\nController Input Port: {input_port}\nOutput Port: {output_port}\nFB-01 Return Port: {return_port}\n")

class SystemData: # System Functions
    def __init__(self):
        self.Channel = 0
        self.MemProtect = 0
        self.ConfigNum = 0 # 0 ~ 19
        self.Detune = 0 # Master detune (not documented), 0 ~ 63 = 0 ~ +63, 64 ~ 127 = -64 ~ -1
        self.TL = 127
    
        self.Config = self.ConfigData()
        
    class ConfigData: # Configuration block
        def __init__(self):
            namestring = "InitConf"
            self.Name = bytearray(namestring, "ascii")
            self.Combine = 0 # When on, Global config for last selected voice replaces Inst configuration
            self.LFOSpeed = 100
            self.AMD = 0
            self.PMD = 39
            self.Waveform = 2 # 0 = Saw, 1 = Square, 2 = Triangle, 3 = Noise
            self.KeyReceive = 0 # 0 = ALL, 1 = EVEN, 2 = ODD

class InstData: # Init inst parameters
    def __init__(self):
        self.Notes = 8 # 8 notes default (max)
        self.Channel = 0 # Channel 1 default
        self.KCLimitL = 0
        self.KCLimitH = 127
        self.Bank = 0 # max 7 (0 ~ 6)
        self.Voice = 0 # max 48 (0 ~ 47)
        self.Detune = 0 # 0 ~ 63 = positive, 64 ~ 127 = negative
        self.Octave = 2 # 0 ~ 4 (0 = -2, 1 = -1, 2 = 0, 3 = +1, 4 = +2)
        self.Output = 127
        self.Pan = 64 # 0 = L, 64 = C, 127 = R
        self.LFOEnable = 1 # 0 = PMS and AMS disabled, 1 = Use PMS and AMS from Voice Data
        self.PortTime = 0
        self.BendRange = 2 # 0 ~ 12 (semitones)
        self.Poly = 1
        self.PMDAssign = 0 # 0 ~ 4 (None, Aftertouch, Mod Wheel, Breath, Foot)

class VoiceData: # Init voice parameters
    def __init__(self):
        #self.LFOLoad = 0
        #self.AMD = 0
        #self.LFOSync = 0
        #self.PMD = 0
        #self.Feedback = 0
        #self.Algorithm = 0
        #self.PMS = 0
        #self.AMS = 0
        #self.Waveform = 0
        #self.TransposeSign = 0
        #self.Transpose = 0
        #self.PMDAssign = 2
        #self.PitchBendRange = 2
        
        #self.Op1 = self.Operator()
        #self.Op1.Enable = 1
        #self.Op1.TL = 127
        #self.Op2 = self.Operator()
        #self.Op3 = self.Operator()
        #self.Op4 = self.Operator()
        
        namestring = "init   "   
        self.Name = bytearray(namestring, "ascii")
        self.UserCode = [0, 0]
        self.LFOSpeed = [0x08, 0x0C] # 200 by default
        self.LFOLoad_AMD = [0, 0]
        self.LFOSync_PMD = [0, 0]
        self.OpsEnable = [0, 0b0100] # Enable Op1 by default
        self.Feedback_Algo = [0, 0]
        self.PMS_AMS = [0, 0b0011]
        self.Waveform = [0, 0]
        self.Transpose = [0, 0]
        self.Poly_Port = [0, 0]
        self.PMDAssign_BendRange = [0, 0]
        
        self.Op1 = self.Operator()
        self.Op1.TL = [0, 0] # Op1 TL set to 0 (max) by default
        self.Op2 = self.Operator()
        self.Op3 = self.Operator()
        self.Op4 = self.Operator()
    
    class Operator:
        def __init__(self):
            #self.Enable = 0
            #self.TL = 0
            #self.KeyLvlType = 0
            #self.TLVel = 0
            #self.KeyLvlDepth = 0
            #self.TLFine = 0
            #self.DT = 0
            #self.Multi = 1
            #self.KeyEnvRt = 0
            #self.AR = 31
            #self.AM = 0
            #self.ARVel = 0
            #self.D1R = 0
            #self.D2R = 0
            #self.SL = 0
            #self.RR = 15
            
            self.TL = [0b1111, 0b0111] # Set to 127 (min) by default
            self.TypeBit0_TLVel = [0, 0] # Bit #0 = positive/negative (0/1)
            self.KeyLvlDepth_TLFine = [0, 0]
            self.TypeBit1_DT1_Multi = [0b0001, 0] # Multi set to 1 by default, TypeBit1 set to 0 (lin/exp, 0/1), and DT1 set to 0 (longest)
            self.KeyEnvRt_AR = [0b1111, 0b0001] # AR set to 31 by default (fastest), KeyEnvRt set to 0
            self.AM_ARVel_D1R = [0, 0]
            self.DT2_D2R = [0, 0] # DT2 set to 0 by default (no modifying), D2R set to 0 by default (longest)
            self.SL_RR = [0b1111, 0] # SL set to 0 by default (longest/constant), RR set to 15 by default (fastest)

System = SystemData()
NewInst = InstData()
NewVoice = VoiceData()

#def get_voice():
    #sysex_data = [0x43, 0x75, 0x00, 0x28, 0x00, 0x00] # Sysex message to dump inst 1 voice data
    #sysex_msg = Message('sysex', data=sysex_data)
    
    #output_port.send(sysex_msg)
    #print("Voice dump requested")
    
    #response_sysex_data = []
    
    #while True:
        #msg = return_port.receive() # Wait for message
        #if msg.type == 'sysex':
            #response_sysex_data = msg.data
            #break
    
    #print(f"Received Sysex response: {len(response_sysex_data)}\n", response_sysex_data)
    #return response_sysex_data[26:-1]

def cc_to_sysex(control, value, channel):
    high_data = 0
    low_data = 0
    
    # Convert CC value to separate byte-split-and-swapped values if necessary

    sysex_data = [0x43]                     # Yamaha FB-01 manufacturer ID
    sysex_data += [0x75]                    # Sub-status
    sysex_data += [System.Channel]                    # System channel number (1 by default)
    # Determine sysex message type:
    match control:
        case 0 | 3 | 6 | 8 | 9 | 11 | 12 | 13 | 14 | 15 | 111 | 112 | 113 | 125:
            sysex_data += [0x10]                    # System/Config parameter
        case _:
            # Determine Inst voice to modify (channels 1~8 = insts 1~8, channels 8~15 = inst 1)
            match channel:
                case 0 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15:
                    sysex_data += [0x18]            # Instrument number (1) - Voice and Inst parameter
                case 1:
                    sysex_data += [0x19]            # Instrument number (2) - Voice and Inst parameter
                case 2:
                    sysex_data += [0x1A]            # Instrument number (3) - Voice and Inst parameter
                case 3:
                    sysex_data += [0x1B]            # Instrument number (4) - Voice and Inst parameter
                case 4:
                    sysex_data += [0x1C]            # Instrument number (5) - Voice and Inst parameter
                case 5:
                    sysex_data += [0x1D]            # Instrument number (6) - Voice and Inst parameter
                case 6:
                    sysex_data += [0x1E]            # Instrument number (7) - Voice and Inst parameter
                case 7:
                    sysex_data += [0x1F]            # Instrument number (8) - Voice and Inst parameter
    
    # Map CC values to sysex data bytes
    match control:
        # System: Memory Protect
        case 0:
            sysex_data += [0x21]                    # System parameter ($21 = memory protect)
            low_data = System.MemProtect
            
            if value == 0 and low_data != 0:
                low_data = 0
                System.MemProtect = low_data
            elif value == 127 and low_data != 1:
                low_data = 1
                System.MemProtect = low_data
        
        # Config: Combine Mode
        case 3:
            sysex_data += [0x08]                    # System parameter ($08 = Config: Combine Mode)
            low_data = System.Config.Combine
            
            if value == 0 and low_data != 0:
                low_data = 0
                System.Config.Combine = low_data
            elif value == 127 and low_data != 1:
                low_data = 1
                System.Config.Combine = low_data
        
        # Config Name (Char #1)
        case 6:
            sysex_data += [0x00]
            
            if value != 64 and 0 <= System.Config.Name[0] <= 127:
                System.Config.Name[0] += value - 64
            high_data = System.Config.Name[0] >> 4
            low_data = System.Config.Name[0] & 0x0F
        # Config Name (Char #2)
        case 8:
            sysex_data += [0x01]
            
            if value != 64 and 0 <= System.Config.Name[1] <= 127:
                System.Config.Name[1] += value - 64
            high_data = System.Config.Name[1] >> 4
            low_data = System.Config.Name[1] & 0x0F
        # Config Name (Char #3)
        case 9:
            sysex_data += [0x02]
            
            if value != 64 and 0 <= System.Config.Name[2] <= 127:
                System.Config.Name[2] += value - 64
            high_data = System.Config.Name[2] >> 4
            low_data = System.Config.Name[2] & 0x0F
        # Config Name (Char #4)
        case 11:
            sysex_data += [0x03]
            
            if value != 64 and 0 <= System.Config.Name[3] <= 127:
                System.Config.Name[3] += value - 64
            high_data = System.Config.Name[3] >> 4
            low_data = System.Config.Name[3] & 0x0F
        # Config Name (Char #5)
        case 12:
            sysex_data += [0x04]
            
            if value != 64 and 0 <= System.Config.Name[4] <= 127:
                System.Config.Name[4] += value - 64
            high_data = System.Config.Name[4] >> 4
            low_data = System.Config.Name[4] & 0x0F
        # Config Name (Char #6)
        case 13:
            sysex_data += [0x05]
            
            if value != 64 and 0 <= System.Config.Name[5] <= 127:
                System.Config.Name[5] += value - 64
            high_data = System.Config.Name[5] >> 4
            low_data = System.Config.Name[5] & 0x0F
        # Config Name (Char #7)
        case 14:
            sysex_data += [0x06]
            
            if value != 64 and 0 <= System.Config.Name[6] <= 127:
                System.Config.Name[6] += value - 64
            high_data = System.Config.Name[6] >> 4
            low_data = System.Config.Name[6] & 0x0F
        # Config Name (Char #8)
        case 15:
            sysex_data += [0x07]
            
            if value != 64 and 0 <= System.Config.Name[7] <= 127:
                System.Config.Name[7] += value - 64
            high_data = System.Config.Name[7] >> 4
            low_data = System.Config.Name[7] & 0x0F
        
        # Voice: LFOLoad
        case 16:
            sysex_data += [0x49]                    # Voice Parameter ($49 = LFO Load & AMD)
            low_data = NewVoice.LFOLoad_AMD[0]
            high_data = NewVoice.LFOLoad_AMD[1]
            
            if value == 0 and high_data & 0b1000 != 0:
                high_data = NewVoice.LFOLoad_AMD[1] & 0b111  # Unsets bit 3
                NewVoice.LFOLoad_AMD[1] = high_data
            elif value == 127 and high_data & 0b1000 == 0:
                high_data = NewVoice.LFOLoad_AMD[1] | 0b1000  # Sets bit 3
                NewVoice.LFOLoad_AMD[1] = high_data
        
        # Voice: AMD, amplitude modulation depth
        case 17:
            sysex_data += [0x49]                    # Voice parameter ($49 = LFO Load & AMD)
            low_data = NewVoice.LFOLoad_AMD[0]
            high_data = NewVoice.LFOLoad_AMD[1]
            
            high_data = (high_data & 0b1000) | (value >> 4)
            low_data = value & 0x0F
            
            NewVoice.LFOLoad_AMD = [low_data, high_data]
        
        # Voice: LFOSync
        case 18:
            sysex_data += [0x4A]                    # Voice parameter ($4A = LFO Sync & PMD)
            low_data = NewVoice.LFOSync_PMD[0]
            high_data = NewVoice.LFOSync_PMD[1]
            
            if value == 0 and high_data & 0b1000 != 0:
                high_data = NewVoice.LFOSync_PMD[1] & 0b111
                NewVoice.LFOSync_PMD = [low_data, high_data]
            if value == 127 and high_data & 0b1000 == 0:
                high_data = NewVoice.LFOSync_PMD[1] | 0b1000
                NewVoice.LFOSync_PMD = [low_data, high_data]
        
        # Voice: PMD, pitch modulation depth
        case 19:
            sysex_data += [0x4A]                    # Voice parameter ($4A = LFO Sync & PMD)
            low_data = NewVoice.LFOSync_PMD[0]
            high_data = NewVoice.LFOSync_PMD[1]
            
            high_data = (high_data & 0b1000) | (value >> 4)
            low_data = value & 0x0F
            
            NewVoice.LFOSync_PMD = [low_data, high_data]
        
        # Voice: Op1 Enable
        case 20:
            sysex_data += [0x4B]                    # Voice parameter ($4B = Toggle Op1, Op2, Op3, & Op4)
            low_data = NewVoice.OpsEnable[0]
            high_data = NewVoice.OpsEnable[1]
            
            if value == 0 and high_data & 0b0100 != 0:
                high_data = NewVoice.OpsEnable[1] & 0b0011
                NewVoice.OpsEnable[1] = high_data
            elif value == 127 and high_data & 0b0100 == 0:
                high_data = NewVoice.OpsEnable[1] | 0b0100
                NewVoice.OpsEnable[1] = high_data
        
        # Voice: Op2 Enable
        case 21:
            sysex_data += [0x4B]                    # Voice parameter ($4B = Toggle Op1, Op2, Op3, & Op4)
            low_data = NewVoice.OpsEnable[0]
            high_data = NewVoice.OpsEnable[1]
            
            if value == 0:
                high_data = NewVoice.OpsEnable[1] & 0b0101
                NewVoice.OpsEnable[1] = high_data
            elif value == 127 and high_data & 0b0010 == 0:
                high_data = NewVoice.OpsEnable[1] | 0b0010
                NewVoice.OpsEnable[1] = high_data
        
        # Voice: Op3 Enable
        case 22:
            sysex_data += [0x4B]                    # Voice parameter ($4B = Toggle Op1, Op2, Op3, & Op4)
            low_data = NewVoice.OpsEnable[0]
            high_data = NewVoice.OpsEnable[1]
            
            if value == 0 and high_data & 0b0001 != 0:
                high_data = NewVoice.OpsEnable[1] & 0b0110
                NewVoice.OpsEnable[1] = high_data
            elif value == 127 and high_data & 0b0001 == 0:
                high_data = NewVoice.OpsEnable[1] | 0b0001
                NewVoice.OpsEnable[1] = high_data
        
        # Voice: Op4 Enable
        case 23:
            sysex_data += [0x4B]                    # Voice parameter ($4B = Toggle Op1, Op2, Op3, & Op4)
            low_data = NewVoice.OpsEnable[0]
            high_data = NewVoice.OpsEnable[1]
            
            if value == 0 and low_data & 0b1000 != 0:
                low_data = 0
                NewVoice.OpsEnable[0] = low_data
            elif value == 127 and low_data & 0b1000 == 0:
                low_data = 0b1000
                NewVoice.OpsEnable[0] = low_data
        
        # Voice: Algorithm
        case 24:
            sysex_data += [0x4C]                    # Voice parameter ($4C = feedback level & algorithm)
            low_data = NewVoice.Feedback_Algo[0]
            high_data = NewVoice.Feedback_Algo[1]
            if 0 <= value <= 7:
                low_data = value
                # Apply Feedback
                low_data |= NewVoice.Feedback_Algo[0] & 0b1000
                high_data = NewVoice.Feedback_Algo[1] & 0x0F
                NewVoice.Feedback_Algo[0] = low_data
                NewVoice.Feedback_Algo[1] = high_data
        
        # Voice: Feedback Level
        case 25:
            sysex_data += [0x4C]                    # Voice parameter ($4C = feedback level & algorithm)
            low_data = NewVoice.Feedback_Algo[0]
            high_data = NewVoice.Feedback_Algo[1]
            if 0 <= value <= 7:
                high_data = value >> 1
                low_data = (value << 3) & 0x0F
                # Apply Algorithm
                low_data |= NewVoice.Feedback_Algo[0] & 0b0111
                NewVoice.Feedback_Algo[0] = low_data
                NewVoice.Feedback_Algo[1] = high_data
        
        # Voice: PMS
        case 26:
            sysex_data += [0x4D]                    # Voice parameter ($4D = PMS and AMS)
            high_data = NewVoice.PMS_AMS[1]
            
            if 0 <= value <= 7:
                high_data = value
                NewVoice.PMS_AMS[1] = high_data
            # Apply AMS
            low_data = NewVoice.PMS_AMS[0]
        
        # Voice: AMS
        case 27:
            sysex_data += [0x4D]                    # Voice parameter ($4D = PMS and AMS)
            low_data = NewVoice.PMS_AMS[0]
            
            if 0 <= value <= 3:
                low_data = value
                NewVoice.PMS_AMS[0] = low_data
            # Apply PMS
            high_data = NewVoice.PMS_AMS[1]
        
        # Voice: LFO Waveform
        case 28:
            sysex_data += [0x4E]                    # Voice parameter ($4E = LFO wave form)
            high_data = NewVoice.Waveform[1]
            if 0 <= value <= 3:
                high_data = value << 1
                NewVoice.Waveform[1] = high_data
        
        # Voice: PMD Assign
        case 29:
            sysex_data += [0x7B]                    # Voice parameter ($7B = PMD Assign & Pitchbend Range)
            high_data = NewVoice.PMDAssign_BendRange[1]
            low_data = NewVoice.PMDAssign_BendRange[0]
            if 0 <= value <= 5:
                high_data = value
                NewVoice.PMDAssign_BendRange[1] = high_data
        
        # Voice: Transpose
        case 30:
            sysex_data += [0x4F]                    # Voice parameter ($4F = Transpose)
            highvalue = value
            low_data = NewVoice.Transpose[0]
            high_data = NewVoice.Transpose[1]
            
            if 25 <= highvalue <= 49:
                highvalue -= 25
            elif 0 <= highvalue <= 24:
                highvalue += 231
                
            high_data = highvalue >> 4
            low_data = highvalue & 0x0F
            NewVoice.Transpose[0] = low_data
            NewVoice.Transpose[1] = high_data
        
        # Voice: Pitchbend Range
        case 31:
            sysex_data += [0x7B]                    # Voice parameter ($7B = PMD Assign & Pitchbend Range)
            low_data = NewVoice.PMDAssign_BendRange[0]
            high_data = NewVoice.PMDAssign_BendRange[1]
            if 0 <= value <= 15:
                low_data = value
                NewVoice.PMDAssign_BendRange[0] = high_data
                
        # Inst: # of notes
        case 99:
            sysex_data += [0x00]                   # Inst parameter ($00 = # of Notes)
            low_data = NewInst.Notes
            if low_data != value and 0 <= value <= 8:
                low_data = value
                NewInst.Notes = low_data
        
        # Inst: MIDI Channel
        case 100:
            sysex_data += [0x01]                   # Inst parameter ($01 = MIDI Channel
            low_data = NewInst.Channel
            if low_data != value and 0 <= value <= 15:
                low_data = value
                NewInst.Channel = low_data
        
        # Inst: KC# Limit (Lower)
        case 101:
            sysex_data += [0x03]                   # Inst parameter ($03 = KC# Limit/L)
            low_data = NewInst.KCLimitL
            if low_data != value:
                low_data = value
                NewInst.KCLimitL = low_data
        
        # Inst: KC# Limit (Upper)
        case 102:
            sysex_data += [0x02]                   # Inst parameter ($02 = KC# Limit/H)
            low_data = NewInst.KCLimitH
            if low_data != value:
                low_data = value
                NewInst.KCLimitH = low_data
        
        # Inst: Voice Bank #
        case 103:
            sysex_data += [0x04]                   # Inst parameter ($04 = Voice Bank #)
            low_data = NewInst.Bank
            if low_data != value and 0 <= value <= 6:
                low_data = value
                NewInst.Bank = low_data
        
        # Inst: Voice #
        case 104:
            sysex_data += [0x05]                   # Inst parameter ($05 = Voice #)
            low_data = NewInst.Voice
            if low_data != value and 0 <= value <= 47:
                low_data = value
                NewInst.Voice = low_data
        
        # Inst: Detune
        case 105:
            sysex_data += [0x06]                   # Inst parameter ($06 = Detune)
            low_data = NewInst.Detune
            # Accomodate signed value for negative range
            if 0 <= value <= 63:
                value += 64
            elif 64 <= value <= 127:
                value -= 64
            if low_data != value:
                low_data = value
                NewInst.Detune = low_data
        
        # Inst: Octave Transpose
        case 106:
            sysex_data += [0x07]                   # Inst parameter ($07 = Octave Transpose)
            low_data = NewInst.Octave
            if low_data != value and 0 <= value <= 4:
                low_data = value
                NewInst.Octave = low_data
        
        # Inst: Output Level
        case 107:
            sysex_data += [0x08]                   # Inst parameter ($08 = Output Level)
            low_data = NewInst.Output
            if low_data != value:
                low_data = value
                NewInst.Output = low_data
        
        # Inst: Pan
        case 108:
            sysex_data += [0x09]                   # Inst parameter ($09 = Pan)
            low_data = NewInst.Pan
            if low_data != value:
                low_data = value
                NewInst.Pan = low_data
        
        # Inst: LFO Enable
        case 109:
            sysex_data += [0x0A]                   # Inst parameter ($0A = LFO Enable)
            low_data = NewInst.LFOEnable
            if value == 0 and low_data != 0:
                low_data = 0
                NewInst.LFOEnable = low_data
            if value == 127 and low_data != 1:
                low_data = 1
                NewInst.LFOEnable = low_data
        
        # Inst: Pitch Bend Range
        case 110:
            sysex_data += [0x0C]                   # Inst parameter ($0C = Pitch Bend Range)
            low_data = NewInst.BendRange
            if low_data != value and 0 <= value <= 12:
                low_data = value
                NewInst.BendRange = low_data
        
        # System: Config Number
        case 111:
            sysex_data += [0x22]                   # System parmeter ($22 = Config #)
            low_data = System.ConfigNum
            if low_data != value and 0 <= value <= 19:
                low_data = value
                System.ConfigNum = low_data
        
        # System: Channel Number
        case 112:
            sysex_data += [0x20]                   # System parameter ($20 = set system MIDI channel)
            low_data = System.Channel
            if low_data != value and 0 <= value <= 15:
                low_data = value
                System.Channel = low_data
        
        # System: Master Detune
        case 113:
            sysex_data += [0x23]                   # System parameter ($23 = system master detune, not documented)
            low_data = System.Detune
            # Accomodate signed value for negative range
            if 0 <= value <= 63:
                value += 64
            elif 64 <= value <= 127:
                value -= 64
            if low_data != value:
                low_data = value
                System.Detune = low_data
        
        # Voice: LFO Speed (controller knob set to Relative Bit Offset)
        case 115:                                   # Voice Parameter ($48 = Voice LFO Speed)
            sysex_data += [0x48]
            low_data = NewVoice.LFOSpeed[0]
            high_data = NewVoice.LFOSpeed[1]
            
            LFOSpeed = (NewVoice.LFOSpeed[1] << 4) | (NewVoice.LFOSpeed[0] & 0x0F)
            
            if value != 64 and 0 <= LFOSpeed <= 255 and (LFOSpeed + value - 64) <= 255 and (LFOSpeed + value - 64) >= 0:
                LFOSpeed += value - 64
                low_data = LFOSpeed & 0x0F
                high_data = LFOSpeed >> 4
            NewVoice.LFOSpeed[0] = low_data
            NewVoice.LFOSpeed[1] = high_data
            
        # Voice Name Char 1
        case 116:
            sysex_data += [0x40]                    # Voice Parameter ($40 = Voice Name Char 1)
            highvalue = value
            if highvalue != 64 and 0 <= NewVoice.Name[0] <= 127:
                NewVoice.Name[0] += highvalue - 64
            high_data = NewVoice.Name[0] >> 4
            low_data = NewVoice.Name[0] & 0x0F
        # Voice Name Char 2
        case 117:
            sysex_data += [0x41]                    # Voice Parameter ($41 = Voice Name Char 2)
            
            if value != 64 and 0 <= NewVoice.Name[1] <= 127:
                NewVoice.Name[1] += value - 64
            high_data = NewVoice.Name[1] >> 4
            low_data = NewVoice.Name[1] & 0x0F
        # Voice Name Char 3
        case 118:
            sysex_data += [0x42]                    # Voice Parameter ($42 = Voice Name Char 3)
            
            if value != 64 and 0 <= NewVoice.Name[2] <= 127:
                NewVoice.Name[2] += value - 64
            high_data = NewVoice.Name[2] >> 4
            low_data = NewVoice.Name[2] & 0x0F
        # Voice Name Char 4
        case 119:
            sysex_data += [0x43]                    # Voice Parameter ($43 = Voice Name Char 4)
            
            if value != 64 and 0 <= NewVoice.Name[3] <= 127:
                NewVoice.Name[3] += value - 64
            high_data = NewVoice.Name[3] >> 4
            low_data = NewVoice.Name[3] & 0x0F
        # Voice Name Char 5
        case 120:
            sysex_data += [0x44]                    # Voice Parameter ($44 = Voice Name Char 5)
            
            if value != 64 and 0 <= NewVoice.Name[4] <= 127:
                NewVoice.Name[4] += value - 64
            high_data = NewVoice.Name[4] >> 4
            low_data = NewVoice.Name[4] & 0x0F
        # Voice Name Char 6
        case 121:
            sysex_data += [0x45]                    # Voice Parameter ($45 = Voice Name Char 6)
            
            if value != 64 and 0 <= NewVoice.Name[5] <= 127:
                NewVoice.Name[5] += value - 64
            high_data = NewVoice.Name[5] >> 4
            low_data = NewVoice.Name[5] & 0x0F
        # Voice Name Char 7
        case 122:
            sysex_data += [0x46]                    # Voice Parameter ($46 = Voice Name Char 7)
            
            if value != 64 and 0 <= NewVoice.Name[6] <= 127:
                NewVoice.Name[6] += value - 64
            high_data = NewVoice.Name[6] >> 4
            low_data = NewVoice.Name[6] & 0x0F
        
        # Voice User Code
        case 124:
            sysex_data += [0x07]                    # Voice Parameter ($07 = user code)
            
            if value != 64 and 0 <= NewVoice.UserCode <= 127:
                NewVoice.UserCode += value - 64
            high_data = NewVoice.UserCode >> 4
            low_data = NewVoice.UserCode & 0x0F
        
        # System: Master Output Level
        case 125:
            sysex_data += [0x24]                   # System parameter ($24 = system master output level)
            low_data = System.TL
            if low_data != value:
                low_data = value
                System.TL = low_data
        
        # Handle the duplicate commands for the 4 operators
        case _:
            opOffset = [0,16,35,51]
            for i in opOffset:
                # Op TL
                if control == 32 + i:
                    value = 127 - value
                    high_data = value >> 4
                    low_data = value & 0x0F
                    match i:
                        case 0: # Voice parameter ($68 = Op1 TL)
                            sysex_data += [0x68]
                            NewVoice.Op1.TL = value
                        case 16: # Voice parameter ($60 = Op2 TL)
                            sysex_data += [0x60]
                            NewVoice.Op2.TL = value
                        case 35: # Voice parameter ($58 = Op3 TL)
                            sysex_data += [0x58]
                            NewVoice.Op3.TL = value
                        case 51: # Voice parameter ($50 = Op4 TL)
                            sysex_data += [0x50]
                            NewVoice.Op4.TL = value
                
                # Op KeyLvlType (-/+ Toggle)
                if control == 33 + i:
                    match i:
                        case 0: # Voice parameter ($69 = Op1 Keyboard level scaling type bit #0 (-/+) and Velocity Sensitivity)
                            sysex_data += [0x69]
                            low_data = NewVoice.Op1.TypeBit0_TLVel[0]
                            high_data = NewVoice.Op1.TypeBit0_TLVel[1]
                            if value == 0:
                                high_data &= 0b0111
                            elif value == 127:
                                high_data |= 8
                                
                            if high_data != NewVoice.Op1.TypeBit0_TLVel[1]:
                                NewVoice.Op1.TypeBit0_TLVel[1] = high_data
                        case 16: # Voice parameter ($61 = Op2 Keyboard level scaling type bit #0 (-/+) and Velocity Sensitivity)
                            sysex_data += [0x61]
                            low_data = NewVoice.Op2.TypeBit0_TLVel[0]
                            high_data = NewVoice.Op2.TypeBit0_TLVel[1]
                            if value == 0:
                                high_data &= 0b0111
                            elif value == 127:
                                high_data |= 8
                                
                            if high_data != NewVoice.Op2.TypeBit0_TLVel[1]:
                                NewVoice.Op2.TypeBit0_TLVel[1] = high_data
                        case 35: # Voice parameter ($59 = Op3 Keyboard level scaling type bit #0 (-/+) and Velocity Sensitivity)
                            sysex_data += [0x59]
                            low_data = NewVoice.Op3.TypeBit0_TLVel[0]
                            high_data = NewVoice.Op3.TypeBit0_TLVel[1]
                            if value == 0:
                                high_data &= 0b0111
                            elif value == 127:
                                high_data |= 8
                                
                            if high_data != NewVoice.Op3.TypeBit0_TLVel[1]:
                                NewVoice.Op3.TypeBit0_TLVel[1] = high_data
                        case 51: # Voice parameter ($51 = Op4 Keyboard level scaling type bit #0 (-/+) and Velocity Sensitivity)
                            sysex_data += [0x51]
                            low_data = NewVoice.Op4.TypeBit0_TLVel[0]
                            high_data = NewVoice.Op4.TypeBit0_TLVel[1]
                            if value == 0:
                                high_data &= 0b0111
                            elif value == 127:
                                high_data |= 8
                                
                            if high_data != NewVoice.Op4.TypeBit0_TLVel[1]:
                                NewVoice.Op4.TypeBit0_TLVel[1] = high_data
                
                # Op KeyLvlType (Lin/Exp Toggle)
                if control == 34 + i:
                    match i:
                        case 0: # Voice parameter ($6B = Op1 Keyboard level scaling type bit #1 (Lin/Exp) and Velocity Sensitivity)
                            sysex_data += [0x6B]
                            low_data = NewVoice.Op1.TypeBit1_DT1_Multi[0]
                            high_data = NewVoice.Op1.TypeBit1_DT1_Multi[1]
                            if value == 0:
                                high_data &= 0b0111
                            elif value == 127:
                                high_data |= 8
                                
                            if high_data != NewVoice.Op1.TypeBit1_DT1_Multi[1]:
                                NewVoice.Op1.TypeBit1_DT1_Multi[1] = high_data
                        case 16: # Voice parameter ($63 = Op2 Keyboard level scaling type bit #1 (Lin/Exp) and Velocity Sensitivity)
                            sysex_data += [0x63]
                            low_data = NewVoice.Op2.TypeBit1_DT1_Multi[0]
                            high_data = NewVoice.Op2.TypeBit1_DT1_Multi[1]
                            if value == 0:
                                high_data &= 0b0111
                            elif value == 127:
                                high_data |= 8
                                
                            if high_data != NewVoice.Op2.TypeBit1_DT1_Multi[1]:
                                NewVoice.Op2.TypeBit1_DT1_Multi[1] = high_data
                        case 35: # Voice parameter ($5B = Op3 Keyboard level scaling type bit #1 (Lin/Exp) and Velocity Sensitivity)
                            sysex_data += [0x5B]
                            low_data = NewVoice.Op3.TypeBit1_DT1_Multi[0]
                            high_data = NewVoice.Op3.TypeBit1_DT1_Multi[1]
                            if value == 0:
                                high_data &= 0b0111
                            elif value == 127:
                                high_data |= 8
                                
                            if high_data != NewVoice.Op3.TypeBit1_DT1_Multi[1]:
                                NewVoice.Op3.TypeBit1_DT1_Multi[1] = high_data
                        case 51: # Voice parameter ($53 = Op4 Keyboard level scaling type bit #1 (Lin/Exp) and Velocity Sensitivity)
                            sysex_data += [0x53]
                            low_data = NewVoice.Op4.TypeBit1_DT1_Multi[0]
                            high_data = NewVoice.Op4.TypeBit1_DT1_Multi[1]
                            if value == 0:
                                high_data &= 0b0111
                            elif value == 127:
                                high_data |= 8
                                
                            if high_data != NewVoice.Op4.TypeBit1_DT1_Multi[1]:
                                NewVoice.Op4.TypeBit1_DT1_Multi[1] = high_data
                
                # Op TLVel
                if control == 35 + i:
                    if 0 <= value < 8:
                        high_data = value
                        match i:
                            case 0: # Voice parameter ($69 = Op1 Keyboard level scaling type bit #0 and Velocity Sensitivity)
                                sysex_data += [0x69]
                                high_data = NewVoice.Op1.TypeBit0_TLVel[1]
                                if 0 <= value <= 7 and NewVoice.Op1.TypeBit0_TLVel[1] & 0b0111 != value:
                                    high_data |= value & 0b0111
                                    NewVoice.Op1.TypeBit0_TLVel[1] = high_data
                            case 16: # Voice parameter ($61 = Op2 Keyboard level scaling type bit #0 and Velocity Sensitivity)
                                sysex_data += [0x61]
                                high_data = NewVoice.Op2.TypeBit0_TLVel[1]
                                if 0 <= value <= 7 and NewVoice.Op2.TypeBit0_TLVel[1] & 0b0111 != value:
                                    high_data |= value & 0b0111
                                    NewVoice.Op2.TypeBit0_TLVel[1] = high_data
                            case 35: # Voice parameter ($59 = Op3 Keyboard level scaling type bit #0 and Velocity Sensitivity)
                                sysex_data += [0x59]
                                high_data = NewVoice.Op3.TypeBit0_TLVel[1]
                                if 0 <= value <= 7 and NewVoice.Op3.TypeBit0_TLVel[1] & 0b0111 != value:
                                    high_data |= value & 0b0111
                                    NewVoice.Op3.TypeBit0_TLVel[1] = high_data
                            case 51: # Voice parameter ($51 = Op4 Keyboard level scaling type bit #0 and Velocity Sensitivity)
                                sysex_data += [0x51]
                                high_data = NewVoice.Op4.TypeBit0_TLVel[1]
                                if 0 <= value <= 7 and NewVoice.Op4.TypeBit0_TLVel[1] & 0b0111 != value:
                                    high_data |= value & 0b0111
                                    NewVoice.Op4.TypeBit0_TLVel[1] = high_data
                
                # Op KeyLvlDepth
                if control == 36 + i:
                    if 0 <= value < 16:
                        high_data = value
                        match i:
                            case 0: # Voice parameter ($6A = Op1 Keyboard level scaling depth and TL adjust)
                                sysex_data += [0x6A]
                                low_data = NewVoice.Op1.KeyLvlDepth_TLFine[0]
                                high_data = NewVoice.Op1.KeyLvlDepth_TLFine[1]
                                if 0 <= value <= 15 and NewVoice.Op1.KeyLvlDepth_TLFine[1] != value:
                                    high_data = value
                                    NewVoice.Op1.KeyLvlDepth_TLFine[1] = high_data
                            case 16: # Voice parameter ($62 = Op2 Keyboard level scaling depth and TL adjust)
                                sysex_data += [0x62]
                                low_data = NewVoice.Op2.KeyLvlDepth_TLFine[0]
                                high_data = NewVoice.Op2.KeyLvlDepth_TLFine[1]
                                if 0 <= value <= 15 and NewVoice.Op2.KeyLvlDepth_TLFine[1] != value:
                                    high_data = value
                                    NewVoice.Op2.KeyLvlDepth_TLFine[1] = high_data
                            case 35: # Voice parameter ($5A = Op3 Keyboard level scaling depth and TL adjust)
                                sysex_data += [0x5A]
                                low_data = NewVoice.Op3.KeyLvlDepth_TLFine[0]
                                high_data = NewVoice.Op3.KeyLvlDepth_TLFine[1]
                                if 0 <= value <= 15 and NewVoice.Op3.KeyLvlDepth_TLFine[1] != value:
                                    high_data = value
                                    NewVoice.Op3.KeyLvlDepth_TLFine[1] = high_data
                            case 51: # Voice parameter ($52 = Op4 Keyboard level scaling depth and TL adjust)
                                sysex_data += [0x52]
                                low_data = NewVoice.Op4.KeyLvlDepth_TLFine[0]
                                high_data = NewVoice.Op4.KeyLvlDepth_TLFine[1]
                                if 0 <= value <= 15 and NewVoice.Op4.KeyLvlDepth_TLFine[1] != value:
                                    high_data = value
                                    NewVoice.Op4.KeyLvlDepth_TLFine[1] = high_data
                
                # Op TLFine
                if control == 37 + i:
                    if 0 <= value < 16:
                        low_data = value
                        match i:
                            case 0: # Voice parameter ($6A = Op1 Keyboard level scaling depth and TL adjust)
                                sysex_data += [0x6A]
                                low_data = NewVoice.Op1.KeyLvlDepth_TLFine[0]
                                high_data = NewVoice.Op1.KeyLvlDepth_TLFine[1]
                                if 0 <= value <= 15 and NewVoice.Op1.KeyLvlDepth_TLFine[0] != value:
                                    low_data = value
                                    NewVoice.Op1.KeyLvlDepth_TLFine[0] = low_data
                            case 16: # Voice parameter ($62 = Op2 Keyboard level scaling depth and TL adjust)
                                sysex_data += [0x62]
                                low_data = NewVoice.Op2.KeyLvlDepth_TLFine[0]
                                high_data = NewVoice.Op2.KeyLvlDepth_TLFine[1]
                                if 0 <= value <= 15 and NewVoice.Op2.KeyLvlDepth_TLFine[0] != value:
                                    low_data = value
                                    NewVoice.Op2.KeyLvlDepth_TLFine[0] = low_data
                            case 35: # Voice parameter ($5A = Op3 Keyboard level scaling depth and TL adjust)
                                sysex_data += [0x5A]
                                low_data = NewVoice.Op3.KeyLvlDepth_TLFine[0]
                                high_data = NewVoice.Op3.KeyLvlDepth_TLFine[1]
                                if 0 <= value <= 15 and NewVoice.Op3.KeyLvlDepth_TLFine[0] != value:
                                    low_data = value
                                    NewVoice.Op3.KeyLvlDepth_TLFine[0] = low_data
                            case 51: # Voice parameter ($52 = Op4 Keyboard level scaling depth and TL adjust)
                                sysex_data += [0x52]
                                low_data = NewVoice.Op4.KeyLvlDepth_TLFine[0]
                                high_data = NewVoice.Op4.KeyLvlDepth_TLFine[1]
                                if 0 <= value <= 15 and NewVoice.Op4.KeyLvlDepth_TLFine[0] != value:
                                    low_data = value
                                    NewVoice.Op4.KeyLvlDepth_TLFine[0] = low_data
                
                # Op DT1 (Coarse/Inharmonic)
                if control == 38 + i:
                    # CC value 3 sets DT1 value to 0 which has already been done when 'high_data' was first initialized
                    # DT1 value 4 = DT1 value 0 so we don't need to have a condition for it
                    
                    # CC values 0-2 map to inverted DT1 sysex values 7-5 respectively (-3 to -1)
                    if value < 3:
                        high_data = 7 - value
                    # CC values 4-6 map to DT1 sysex values 1-3 respectively (+1 to +3)
                    elif 3 < value < 7:
                        high_data = value - 3
                    
                    match i:
                        case 0: # Voice parameter ($6B = Op1 Keyboard level scaling type bit #1, DT1, and Multiple)
                            sysex_data += [0x6B]
                            low_data = NewVoice.Op1.TypeBit1_DT1_Multi[0]
                            high_data |= NewVoice.Op1.TypeBit1_DT1_Multi[1] & 0b1000
                            if high_data != NewVoice.Op1.TypeBit1_DT1_Multi[1]:
                                NewVoice.Op1.TypeBit1_DT1_Multi[1] = high_data
                        case 16: # Voice parameter ($63 = Op2 Keyboard level scaling type bit #1, DT1, and Multiple)
                            sysex_data += [0x63]
                            low_data = NewVoice.Op2.TypeBit1_DT1_Multi[0]
                            high_data |= NewVoice.Op2.TypeBit1_DT1_Multi[1] & 0b1000
                            if high_data != NewVoice.Op2.TypeBit1_DT1_Multi[1]:
                                NewVoice.Op2.TypeBit1_DT1_Multi[1] = high_data
                        case 35: # Voice parameter ($5B = Op3 Keyboard level scaling type bit #1, DT1, and Multiple)
                            sysex_data += [0x5B]
                            low_data = NewVoice.Op3.TypeBit1_DT1_Multi[0]
                            high_data |= NewVoice.Op3.TypeBit1_DT1_Multi[1] & 0b1000
                            if high_data != NewVoice.Op3.TypeBit1_DT1_Multi[1]:
                                NewVoice.Op3.TypeBit1_DT1_Multi[1] = high_data
                            
                        case 51: # Voice parameter ($53 = Op4 Keyboard level scaling type bit #1, DT1, and Multiple)
                            sysex_data += [0x53]
                            low_data = NewVoice.Op4.TypeBit1_DT1_Multi[0]
                            high_data |= NewVoice.Op4.TypeBit1_DT1_Multi[1] & 0b1000
                            if high_data != NewVoice.Op4.TypeBit1_DT1_Multi[1]:
                                NewVoice.Op4.TypeBit1_DT1_Multi[1] = high_data
                
                # Op Multi and DT2 (Fine) -- PART ONE of two separate sysex messages
                if control == 39 + i:
                    if 0 <= value <= 63:
                        low_data, _ = freq_table[value]
                    match i:
                        case 0: # Voice parameter ($6B = Op1 Keyboard level scaling type Bit 1, DT1, and Multiple)
                            sysex_data += [0x6B]
                            high_data = NewVoice.Op1.TypeBit1_DT1_Multi[1]
                            if NewVoice.Op1.TypeBit1_DT1_Multi[0] != low_data:
                                NewVoice.Op1.TypeBit1_DT1_Multi[0] = low_data
                        case 16: # Voice parameter ($63 = Op2 Keyboard level scaling type Bit 1, DT1, and Multiple)
                            sysex_data += [0x63]
                            high_data = NewVoice.Op2.TypeBit1_DT1_Multi[1]
                            if NewVoice.Op2.TypeBit1_DT1_Multi[0] != low_data:
                                NewVoice.Op2.TypeBit1_DT1_Multi[0] = low_data
                        case 35: # Voice parameter ($5B = Op3 Keyboard level scaling type Bit 1, DT1, and Multiple)
                            sysex_data += [0x5B]
                            high_data = NewVoice.Op3.TypeBit1_DT1_Multi[1]
                            if NewVoice.Op3.TypeBit1_DT1_Multi[0] != low_data:
                                NewVoice.Op3.TypeBit1_DT1_Multi[0] = low_data
                        case 51: # Voice parameter ($53 = Op4 Keyboard level scaling type Bit 1, DT1, and Multiple)
                            sysex_data += [0x53]
                            high_data = NewVoice.Op4.TypeBit1_DT1_Multi[1]
                            if NewVoice.Op4.TypeBit1_DT1_Multi[0] != low_data:
                                NewVoice.Op4.TypeBit1_DT1_Multi[0] = low_data
                
                # Op KeyEnvRt
                if control == 40 + i:
                    match i:
                        case 0: # Voice parameter ($6C = Op1 Keyboard rate scaling depth and AR)
                            sysex_data += [0x6C]
                            low_data = NewVoice.Op1.KeyEnvRt_AR[0]
                            high_data = NewVoice.Op1.KeyEnvRt_AR[1]
                            if 0 <= value <= 3 and NewVoice.Op1.KeyEnvRt_AR[1] & 0b1100 != (value << 2):
                                high_data = (value << 2) | (high_data & 0b0001)
                                NewVoice.Op1.KeyEnvRt_AR[1] = high_data
                        case 16: # Voice parameter ($64 = Op2 Keyboard rate scaling depth and AR)
                            sysex_data += [0x64]
                            low_data = NewVoice.Op2.KeyEnvRt_AR[0]
                            high_data = NewVoice.Op2.KeyEnvRt_AR[1]
                            if 0 <= value <= 3 and NewVoice.Op2.KeyEnvRt_AR[1] & 0b1100 != (value << 2):
                                high_data = (value << 2) | (high_data & 0b0001)
                                NewVoice.Op1.KeyEnvRt_AR[1] = high_data
                        case 35: # Voice parameter ($5C = Op3 Keyboard rate scaling depth and AR)
                            sysex_data += [0x5C]
                            low_data = NewVoice.Op3.KeyEnvRt_AR[0]
                            high_data = NewVoice.Op3.KeyEnvRt_AR[1]
                            if 0 <= value <= 3 and NewVoice.Op3.KeyEnvRt_AR[1] & 0b1100 != (value << 2):
                                high_data = (value << 2) | (high_data & 0b0001)
                                NewVoice.Op1.KeyEnvRt_AR[1] = high_data
                        case 51: # Voice parameter ($54 = Op4 Keyboard rate scaling depth and AR)
                            sysex_data += [0x54]
                            low_data = NewVoice.Op4.KeyEnvRt_AR[0]
                            high_data = NewVoice.Op4.KeyEnvRt_AR[1]
                            if 0 <= value <= 3 and NewVoice.Op4.KeyEnvRt_AR[1] & 0b1100 != (value << 2):
                                high_data = (value << 2) | (high_data & 0b0001)
                                NewVoice.Op1.KeyEnvRt_AR[1] = high_data
                
                # Op AR
                if control == 41 + i:
                    match i:
                        case 0: # Voice parameter ($6C = Op1 Keyboard rate scaling depth and AR)
                            sysex_data += [0x6C]
                            low_data = NewVoice.Op1.KeyEnvRt_AR[0]
                            high_data = NewVoice.Op1.KeyEnvRt_AR[1]
                            if 0 <= value <= 31:
                                low_data = value & 0x0F
                                if value > 15:
                                    high_data |= 1
                                elif value <= 15:
                                    high_data &= 0b1110
                                if NewVoice.Op1.KeyEnvRt_AR[0] != low_data:
                                    NewVoice.Op1.KeyEnvRt_AR[0] = low_data
                                if NewVoice.Op1.KeyEnvRt_AR[1] != high_data:
                                    NewVoice.Op1.KeyEnvRt_AR[1] = high_data
                        case 16: # Voice parameter ($64 = Op2 Keyboard rate scaling depth and AR)
                            sysex_data += [0x64]
                            low_data = NewVoice.Op2.KeyEnvRt_AR[0]
                            high_data = NewVoice.Op2.KeyEnvRt_AR[1]
                            if 0 <= value <= 31:
                                low_data = value & 0x0F
                                if value > 15:
                                    high_data |= 1
                                elif value <= 15:
                                    high_data &= 0b1110
                                if NewVoice.Op2.KeyEnvRt_AR[0] != low_data:
                                    NewVoice.Op2.KeyEnvRt_AR[0] = low_data
                                if NewVoice.Op2.KeyEnvRt_AR[1] != high_data:
                                    NewVoice.Op2.KeyEnvRt_AR[1] = high_data
                        case 35: # Voice parameter ($5C = Op3 Keyboard rate scaling depth and AR)
                            sysex_data += [0x5C]
                            low_data = NewVoice.Op3.KeyEnvRt_AR[0]
                            high_data = NewVoice.Op3.KeyEnvRt_AR[1]
                            if 0 <= value <= 31:
                                low_data = value & 0x0F
                                if value > 15:
                                    high_data |= 1
                                elif value <= 15:
                                    high_data &= 0b1110
                                if NewVoice.Op3.KeyEnvRt_AR[0] != low_data:
                                    NewVoice.Op3.KeyEnvRt_AR[0] = low_data
                                if NewVoice.Op3.KeyEnvRt_AR[1] != high_data:
                                    NewVoice.Op3.KeyEnvRt_AR[1] = high_data
                        case 51: # Voice parameter ($54 = Op4 Keyboard rate scaling depth and AR)
                            sysex_data += [0x54]
                            low_data = NewVoice.Op4.KeyEnvRt_AR[0]
                            high_data = NewVoice.Op4.KeyEnvRt_AR[1]
                            if 0 <= value <= 31:
                                low_data = value & 0x0F
                                if value > 15:
                                    high_data |= 1
                                elif value <= 15:
                                    high_data &= 0b1110
                                if NewVoice.Op4.KeyEnvRt_AR[0] != low_data:
                                    NewVoice.Op4.KeyEnvRt_AR[0] = low_data
                                if NewVoice.Op4.KeyEnvRt_AR[1] != high_data:
                                    NewVoice.Op4.KeyEnvRt_AR[1] = high_data
                
                # Op AM
                if control == 42 + i:
                    match i:
                        case 0: # Voice parameter ($6D = Op1 AM, Velocity sensitivity (AR), and D1R)
                            sysex_data += [0x6D]
                            low_data = NewVoice.Op1.AM_ARVel_D1R[0]
                            high_data = NewVoice.Op1.AM_ARVel_D1R[1]
                            if value == 0 and NewVoice.Op1.AM_ARVel_D1R[1] & 0b1000 != 0:
                                high_data &= 0b0111
                                NewVoice.Op1.AM_ARVel_D1R[1] = high_data
                            if value == 127 and NewVoice.Op1.AM_ARVel_D1R[1] & 0b1000 != 8:
                                high_data |= 8
                                NewVoice.Op1.AM_ARVel_D1R[1] = high_data
                        case 16: # Voice parameter ($65 = Op2 AM, Velocity sensitivity (AR), and D1R)
                            sysex_data += [0x65]
                            low_data = NewVoice.Op2.AM_ARVel_D1R[0]
                            high_data = NewVoice.Op2.AM_ARVel_D1R[1]
                            if value == 0 and NewVoice.Op2.AM_ARVel_D1R[1] & 0b1000 != 0:
                                high_data &= 0b0111
                                NewVoice.Op2.AM_ARVel_D1R[1] = high_data
                            if value == 127 and NewVoice.Op2.AM_ARVel_D1R[1] & 0b1000 != 8:
                                high_data |= 8
                                NewVoice.Op2.AM_ARVel_D1R[1] = high_data
                        case 35: # Voice parameter ($5D = Op3 AM, Velocity sensitivity (AR), and D1R)
                            sysex_data += [0x5D]
                            low_data = NewVoice.Op3.AM_ARVel_D1R[0]
                            high_data = NewVoice.Op3.AM_ARVel_D1R[1]
                            if value == 0 and NewVoice.Op3.AM_ARVel_D1R[1] & 0b1000 != 0:
                                high_data &= 0b0111
                                NewVoice.Op3.AM_ARVel_D1R[1] = high_data
                            if value == 127 and NewVoice.Op3.AM_ARVel_D1R[1] & 0b1000 != 8:
                                high_data |= 8
                                NewVoice.Op3.AM_ARVel_D1R[1] = high_data
                        case 51: # Voice parameter ($55 = Op4 AM, Velocity sensitivity (AR), and D1R)
                            sysex_data += [0x55]
                            low_data = NewVoice.Op4.AM_ARVel_D1R[0]
                            high_data = NewVoice.Op4.AM_ARVel_D1R[1]
                            if value == 0 and NewVoice.Op4.AM_ARVel_D1R[1] & 0b1000 != 0:
                                high_data &= 0b0111
                                NewVoice.Op4.AM_ARVel_D1R[1] = high_data
                            if value == 127 and NewVoice.Op4.AM_ARVel_D1R[1] & 0b1000 != 8:
                                high_data |= 8
                                NewVoice.Op4.AM_ARVel_D1R[1] = high_data
                
                # Op ARVel
                if control == 43 + i:
                    match i:
                        case 0: # Voice parameter ($6D = Op1 AM, Velocity sensitivity (AR), and D1R)
                            sysex_data += [0x6D]
                            low_data = NewVoice.Op1.AM_ARVel_D1R[0]
                            high_data = NewVoice.Op1.AM_ARVel_D1R[1]
                            if 0 <= value <= 3 and NewVoice.Op1.AM_ARVel_D1R[1] != value << 1:
                                high_data |= value << 1
                                NewVoice.Op1.AM_ARVel_D1R[1] = high_data
                        case 16: # Voice parameter ($65 = Op2 AM, Velocity sensitivity (AR), and D1R)
                            sysex_data += [0x65]
                            low_data = NewVoice.Op2.AM_ARVel_D1R[0]
                            high_data = NewVoice.Op2.AM_ARVel_D1R[1]
                            if 0 <= value <= 3 and NewVoice.Op2.AM_ARVel_D1R[1] != value << 1:
                                high_data |= value << 1
                                NewVoice.Op2.AM_ARVel_D1R[1] = high_data
                        case 35: # Voice parameter ($5D = Op3 AM, Velocity sensitivity (AR), and D1R)
                            sysex_data += [0x5D]
                            low_data = NewVoice.Op3.AM_ARVel_D1R[0]
                            high_data = NewVoice.Op3.AM_ARVel_D1R[1]
                            if 0 <= value <= 3 and NewVoice.Op3.AM_ARVel_D1R[1] != value << 1:
                                high_data |= value << 1
                                NewVoice.Op3.AM_ARVel_D1R[1] = high_data
                        case 51: # Voice parameter ($55 = Op4 AM, Velocity sensitivity (AR), and D1R)
                            sysex_data += [0x55]
                            low_data = NewVoice.Op4.AM_ARVel_D1R[0]
                            high_data = NewVoice.Op4.AM_ARVel_D1R[1]
                            if 0 <= value <= 3 and NewVoice.Op4.AM_ARVel_D1R[1] != value << 1:
                                high_data |= value << 1
                                NewVoice.Op4.AM_ARVel_D1R[1] = high_data
                
                # Op D1R
                if control == 44 + i:
                    match i:
                        case 0: # Voice parameter ($6D = Op1 AM, Velocity sensitivity (AR), and D1R)
                            sysex_data += [0x6D]
                            low_data = NewVoice.Op1.AM_ARVel_D1R[0]
                            high_data = NewVoice.Op1.AM_ARVel_D1R[1]
                            if 0 <= value <= 31:
                                low_data = value & 0x0F
                                if value > 15:
                                    high_data |= 1
                                elif value <= 15:
                                    high_data &= 0b1110
                                if NewVoice.Op1.AM_ARVel_D1R[0] != low_data:
                                    NewVoice.Op1.AM_ARVel_D1R[0] = low_data
                                if NewVoice.Op1.AM_ARVel_D1R[1] != high_data:
                                    NewVoice.Op1.AM_ARVel_D1R[1] = high_data
                        case 16: # Voice parameter ($65 = Op2 AM, Velocity sensitivity (AR), and D1R)
                            sysex_data += [0x65]
                            low_data = NewVoice.Op2.AM_ARVel_D1R[0]
                            high_data = NewVoice.Op2.AM_ARVel_D1R[1]
                            if 0 <= value <= 31:
                                low_data = value & 0x0F
                                if value > 15:
                                    high_data |= 1
                                elif value <= 15:
                                    high_data &= 0b1110
                                if NewVoice.Op2.AM_ARVel_D1R[0] != low_data:
                                    NewVoice.Op2.AM_ARVel_D1R[0] = low_data
                                if NewVoice.Op2.AM_ARVel_D1R[1] != high_data:
                                    NewVoice.Op2.AM_ARVel_D1R[1] = high_data
                        case 35: # Voice parameter ($5D = Op3 AM, Velocity sensitivity (AR), and D1R)
                            sysex_data += [0x5D]
                            low_data = NewVoice.Op3.AM_ARVel_D1R[0]
                            high_data = NewVoice.Op3.AM_ARVel_D1R[1]
                            if 0 <= value <= 31:
                                low_data = value & 0x0F
                                if value > 15:
                                    high_data |= 1
                                elif value <= 15:
                                    high_data &= 0b1110
                                if NewVoice.Op3.AM_ARVel_D1R[0] != low_data:
                                    NewVoice.Op3.AM_ARVel_D1R[0] = low_data
                                if NewVoice.Op3.AM_ARVel_D1R[1] != high_data:
                                    NewVoice.Op3.AM_ARVel_D1R[1] = high_data
                        case 51: # Voice parameter ($55 = Op4 AM, Velocity sensitivity (AR), and D1R)
                            sysex_data += [0x55]
                            if 0 <= value <= 31:
                                low_data = value & 0x0F
                                if value > 15:
                                    high_data |= 1
                                elif value <= 15:
                                    high_data &= 0b1110
                                if NewVoice.Op4.AM_ARVel_D1R[0] != low_data:
                                    NewVoice.Op4.AM_ARVel_D1R[0] = low_data
                                if NewVoice.Op4.AM_ARVel_D1R[1] != high_data:
                                    NewVoice.Op4.AM_ARVel_D1R[1] = high_data
                
                # Op D2R
                if control == 45 + i:
                    match i:
                        case 0: # Voice parameter ($6E = Op1 DT2 and D2R)
                            sysex_data += [0x6E]
                            low_data = NewVoice.Op1.DT2_D2R[0]
                            high_data = NewVoice.Op1.DT2_D2R[1]
                            if 0 <= value <= 31:
                                low_data = value & 0x0F
                                if value > 15:
                                    high_data |= 1
                                elif value <= 15:
                                    high_data &= 0b1110
                                if NewVoice.Op1.DT2_D2R[0] != low_data:
                                    NewVoice.Op1.DT2_D2R[0] = low_data
                                if NewVoice.Op1.DT2_D2R[1] != high_data:
                                    NewVoice.Op1.DT2_D2R[1] = high_data
                        case 16: # Voice parameter ($66 = Op2 DT2 and D2R)
                            sysex_data += [0x66]
                            low_data = NewVoice.Op2.DT2_D2R[0]
                            high_data = NewVoice.Op2.DT2_D2R[1]
                            if 0 <= value <= 31:
                                low_data = value & 0x0F
                                if value > 15:
                                    high_data |= 1
                                elif value <= 15:
                                    high_data &= 0b1110
                                if NewVoice.Op2.DT2_D2R[0] != low_data:
                                    NewVoice.Op2.DT2_D2R[0] = low_data
                                if NewVoice.Op2.DT2_D2R[1] != high_data:
                                    NewVoice.Op2.DT2_D2R[1] = high_data
                        case 35: # Voice parameter ($5E = Op3 DT2 and D2R)
                            sysex_data += [0x5E]
                            low_data = NewVoice.Op3.DT2_D2R[0]
                            high_data = NewVoice.Op3.DT2_D2R[1]
                            if 0 <= value <= 31:
                                low_data = value & 0x0F
                                if value > 15:
                                    high_data |= 1
                                elif value <= 15:
                                    high_data &= 0b1110
                                if NewVoice.Op3.DT2_D2R[0] != low_data:
                                    NewVoice.Op3.DT2_D2R[0] = low_data
                                if NewVoice.Op3.DT2_D2R[1] != high_data:
                                    NewVoice.Op3.DT2_D2R[1] = high_data
                        case 51: # Voice parameter ($56 = Op4 DT2 and D2R)
                            sysex_data += [0x56]
                            low_data = NewVoice.Op4.DT2_D2R[0]
                            high_data = NewVoice.Op4.DT2_D2R[1]
                            if 0 <= value <= 31:
                                low_data = value & 0x0F
                                if value > 15:
                                    high_data |= 1
                                elif value <= 15:
                                    high_data &= 0b1110
                                if NewVoice.Op4.DT2_D2R[0] != low_data:
                                    NewVoice.Op4.DT2_D2R[0] = low_data
                                if NewVoice.Op4.DT2_D2R[1] != high_data:
                                    NewVoice.Op4.DT2_D2R[1] = high_data
                
                # Op SL
                if control == 46 + i:
                    match i:
                        case 0: # Voice parameter ($6F = Op1 SL and RR)
                            sysex_data += [0x6F]
                            low_data = NewVoice.Op1.SL_RR[0]
                            high_data = NewVoice.Op1.SL_RR[1]
                            if 0 <= value <= 15 and NewVoice.Op1.SL_RR[1] != value:
                                high_data = value
                                NewVoice.Op1.SL_RR[1] = high_data
                        case 16: # Voice parameter ($67 = Op2 SL and RR)
                            sysex_data += [0x67]
                            low_data = NewVoice.Op2.SL_RR[0]
                            high_data = NewVoice.Op2.SL_RR[1]
                            if 0 <= value <= 15 and NewVoice.Op2.SL_RR[1] != value:
                                high_data = value
                                NewVoice.Op2.SL_RR[1] = high_data
                        case 35: # Voice parameter ($5F = Op3 SL and RR)
                            sysex_data += [0x5F]
                            low_data = NewVoice.Op3.SL_RR[0]
                            high_data = NewVoice.Op3.SL_RR[1]
                            if 0 <= value <= 15 and NewVoice.Op3.SL_RR[1] != value:
                                high_data = value
                                NewVoice.Op3.SL_RR[1] = high_data
                        case 51: # Voice parameter ($57 = Op4 SL and RR)
                            sysex_data += [0x57]
                            low_data = NewVoice.Op4.SL_RR[0]
                            high_data = NewVoice.Op4.SL_RR[1]
                            if 0 <= value <= 15 and NewVoice.Op4.SL_RR[1] != value:
                                high_data = value
                                NewVoice.Op4.SL_RR[1] = high_data
                
                # Op RR
                if control == 47 + i:
                    match i:
                        case 0: # Voice parameter ($6F = Op1 SL and RR)
                            sysex_data += [0x6F]
                            low_data = NewVoice.Op1.SL_RR[0]
                            high_data = NewVoice.Op1.SL_RR[1]
                            if 0 <= value <= 15 and NewVoice.Op1.SL_RR[0] != value:
                                low_data = value
                                NewVoice.Op1.SL_RR[0] = low_data
                        case 16: # Voice parameter ($67 = Op2 SL and RR)
                            sysex_data += [0x67]
                            low_data = NewVoice.Op2.SL_RR[0]
                            high_data = NewVoice.Op2.SL_RR[1]
                            if 0 <= value <= 15 and NewVoice.Op2.SL_RR[0] != value:
                                low_data = value
                                NewVoice.Op2.SL_RR[0] = low_data
                        case 35: # Voice parameter ($5F = Op3 SL and RR)
                            sysex_data += [0x5F]
                            low_data = NewVoice.Op3.SL_RR[0]
                            high_data = NewVoice.Op3.SL_RR[1]
                            if 0 <= value <= 15 and NewVoice.Op3.SL_RR[0] != value:
                                low_data = value
                                NewVoice.Op3.SL_RR[0] = low_data
                        case 51: # Voice parameter ($57 = Op4 SL and RR)
                            sysex_data += [0x57]
                            low_data = NewVoice.Op4.SL_RR[0]
                            high_data = NewVoice.Op4.SL_RR[1]
                            if 0 <= value <= 15 and NewVoice.Op4.SL_RR[0] != value:
                                low_data = value
                                NewVoice.Op4.SL_RR[0] = low_data
    
    # Inject low and high data values taken from CC initial value
    match control:
        case 6 | 8 | 9 | 11 | 12 | 13 | 14 | 15 | 99 | 100 | 101 | 102 | 103 | 104 | 105 | 106 | 107 | 108 | 109 | 110:
            sysex_data += [low_data] # For System, Config, and Inst sysex messages we only need one data byte
        case _:        
            sysex_data += [low_data, high_data] # 2 nibblized data bytes for Voice param sysex messages
    
    f_control = str(control).zfill(3)
    f_value = str(value).zfill(3)
    hex_sysex_data = ' '.join(f'{byte:02X}' for byte in sysex_data)
    print(Style.BRIGHT + Fore.GREEN + f"{f_control}" + Fore.RESET + "/" + Fore.RED + f"{f_value}" + Fore.RESET + " | " + Style.RESET_ALL + Fore.RED + "F0 " + Fore.RESET + Style.BRIGHT + f"{hex_sysex_data} " + Style.RESET_ALL + Fore.RED + "F7" + Style.RESET_ALL)
    #print(f"sysex_data = {sysex_data}")

    return Message('sysex', data=sysex_data)

def cc_2nd_sysex(control, value, channel):
    high_data = 0
    low_data = 0
    
    # Convert CC value to separate byte-split-and-swapped values
    #print(f"CC#, Value: {control},{value}")

    sysex_data = [0x43]                     # Yamaha FB-01 manufacturer ID
    sysex_data += [0x75]                    # Sub-status
    sysex_data += [System.Channel]          # System channel number (1 by default)
    
    match channel:
        case 0 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15:
            sysex_data += [0x18]                    # Instrument number (1)
        case 1:
            sysex_data += [0x19]                    # Instrument number (2)
        case 2:
            sysex_data += [0x1A]                    # Instrument number (3)
        case 3:
            sysex_data += [0x1B]                    # Instrument number (4)
        case 4:
            sysex_data += [0x1C]                    # Instrument number (5)
        case 5:
            sysex_data += [0x1D]                    # Instrument number (6)
        case 6:
            sysex_data += [0x1E]                    # Instrument number (7)
        case 7:
            sysex_data += [0x1F]                    # Instrument number (8)
    
    opOffset = [0,16,35,51]
    
    for i in opOffset:
        # Op Multi and DT2 (Fine) -- PART TWO of two separate sysex messages
        if control == 39 + i:
            if 0 <= value <= 63:
                _, high_data = freq_table[value]
            match i:
                case 0: # Voice parameter ($6E = Op1 DT2 and D2R)
                    sysex_data += [0x6E]
                    high_data |= NewVoice.Op1.DT2_D2R[1] & 0b0001
                    low_data = NewVoice.Op1.DT2_D2R[0]
                    if NewVoice.Op1.DT2_D2R[1] != high_data:
                        NewVoice.Op1.DT2_D2R[1] = high_data
                case 16: # Voice parameter ($66 = Op2 DT2 and D2R)
                    sysex_data += [0x66]
                    high_data |= NewVoice.Op2.DT2_D2R[1] & 0b0001
                    low_data = NewVoice.Op2.DT2_D2R[0]
                    if NewVoice.Op2.DT2_D2R[1] != high_data:
                        NewVoice.Op2.DT2_D2R[1] = high_data
                case 35: # Voice parameter ($5E = Op3 DT2 and D2R)
                    sysex_data += [0x5E]
                    high_data |= NewVoice.Op3.DT2_D2R[1] & 0b0001
                    low_data = NewVoice.Op3.DT2_D2R[0]
                    if NewVoice.Op3.DT2_D2R[1] != high_data:
                        NewVoice.Op3.DT2_D2R[1] = high_data
                case 51: # Voice parameter ($56 = Op4 DT2 and D2R)
                    sysex_data += [0x56]
                    high_data |= NewVoice.Op4.DT2_D2R[1] & 0b0001
                    low_data = NewVoice.Op4.DT2_D2R[0]
                    if NewVoice.Op4.DT2_D2R[1] != high_data:
                        NewVoice.Op4.DT2_D2R[1] = high_data
    
    sysex_data += [low_data, high_data]
    
    f_control = str(control).zfill(3)
    f_value = str(value).zfill(3)
    hex_sysex_data = ' '.join(f'{byte:02X}' for byte in sysex_data)
    print(Style.BRIGHT + Fore.BLUE + "2nd sysex:" + Style.RESET_ALL + Fore.RED + "F0 " + Fore.RESET + Style.BRIGHT + f"{hex_sysex_data} " + Style.RESET_ALL + Fore.RED + "F7" + Style.RESET_ALL)
    
    return Message('sysex', data=sysex_data)

try:
    #voicebuffer = get_voice()
    #print(f"voicebuffer ({len(voicebuffer)}) = {voicebuffer}")
    #VoiceData.LFOLoad = voicebuffer[2] >> 3
    #VoiceData.AMD = ((voicebuffer[2] << 4) & 0x70) | voicebuffer[1]
    
    print("Listening for MIDI messages. Press Ctrl+C to quit.\n\n CC/Val | Sysex String\n=======================")

    while True:
    # Listen for control change messages
        for msg in input_port.iter_pending():
            if msg.type == 'control_change':
                match msg.control:
                    # Pre-implemented controller events
                    case 1 | 2 | 4 | 5 | 7 | 10 | 64 | 65 | 66 | 123 | 126 | 127:
                        output_port.send(msg)
                        print(f"Passing through already implemented CC: {msg}")
                    # Multi-sysex controlled events
                    case 39 | 55 | 74 | 90:
                        sysex_msg = cc_to_sysex(msg.control, msg.value, msg.channel)
                        sysex_msg2 = cc_2nd_sysex(msg.control, msg.value, msg.channel)
                        if len(sysex_msg.data) == 7:
                            output_port.send(sysex_msg)
                            #print(f"Translated CC {msg.control} with value {msg.value} to Sysex: {sysex_msg}")
                        else:
                            print("Invalid sysex length.")
                        if len(sysex_msg2.data) == 7:
                            output_port.send(sysex_msg2)
                            #print(f"Translated CC {msg.control} with value {msg.value} to Sysex: {sysex_msg2}")
                        else:
                            print("Invalid sysex length.")
                    # Normal single-sysex controlled events
                    case _:
                        sysex_msg = cc_to_sysex(msg.control, msg.value, msg.channel)
                        #print(f"{len(sysex_msg.data)}")
                        if 6 <= len(sysex_msg.data) <= 7:
                            output_port.send(sysex_msg)
                            #print(f"Translated CC {msg.control} with value {msg.value} to SysEx: {sysex_msg}")
                            #time.sleep(1)
                            #voicebuffer = get_voice()
                        else:
                            print("Invalid sysex length.")
            else:
                output_port.send(msg)
                print(f"Passing through: {msg}")

        time.sleep(0.01)  # Small delay to prevent 100% CPU usage

except KeyboardInterrupt:
    print("Script interrupted by user.")

finally:
    output_port.send(mido.Message('control_change', control=123, value=0))
    print("All Notes Off message sent.")
    input_port.close()
    output_port.close()
    return_port.close()
    print("MIDI ports closed.")
