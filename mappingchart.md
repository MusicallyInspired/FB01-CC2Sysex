# CC/Sysex Mapping Chart (currently hardcoded)
CCs that the FB-01 already understands are marked with square brackets "[]". They are not converted and are passed "thru" without any additional processing directly to the FB-01. Notes and other MIDI messages are also sent "thru" unchanged.

Currently, the sysex messages that control the Voice LFO Speed and Voice "User Code" (which both have a maximum value of 255, too high for a standard CC MIDI message's value range) is handled by interpreting the corresponding CC's values in "Relative Binary Offset" or "RBOff" mode. I'm using an M-Audio Axiom Air 49 MIDI controller and its pot encoders can be set to multiple modes including RBOff. So for this particular parameter data change message I've coded it so that any CC value greater than or less than 64 is interpretted as a value increment or decrement determined by its offset value to 64 (ie- 64 + x = current LFO Speed + x).</br>**NOTE:** The FB-01 itself does not support RBOff values. The actual setting value is calculated and stored internally in the script which sets the appropriate value in the sysex message during translation.

Please refer to the original FB-01 documentation itself for parameter descriptions.

CC #  | Param Type     | Parameter                             | CC Range        | Notes
:---: | -------------: | ------------------------------------- | :-------------: | -------------------
0     | System         | Memory Protect (toggle)               | 0 / 127         | *0 = off, 127 = on*
[1]   |                | [Mod Wheel]                           | 0 ~ 127         | *implemented*
[2]   |                | [Breath]                              | 0 ~ 127         | *implemented*
3     | Config         | Combine Mode (toggle)                 | 0 / 127         | *0 = off, 127 = on*
[4]   |                | [Foot Controller]                     | 0 ~ 127         | *implemented*
[5]   |                | [Portamento Time]                     | 0 ~ 127         | *implemented*
6     | Config         | Name (Char #1)                        | 0 ~ 127         | 
[7]   |                | [Channel Volume]                      | 0 ~ 127         | 
8     | Config         | Name (Char #2)                        | 0 ~ 127         | 
9     | Config         | Name (Char #3)                        | 0 ~ 127         | 
[10]  |                | [Pan]                                 | 0 / 64 / 127    | *0 = L</br>64 = LR</br>127 = R*
11    | Config         | Name (Char #4)                        | 0 ~ 127         | 
12    | Config         | Name (Char #5)                        | 0 ~ 127         | 
13    | Config         | Name (Char #6)                        | 0 ~ 127         | 
14    | Config         | Name (Char #7)                        | 0 ~ 127         | 
15    | Config         | Name (Char #8)                        | 0 ~ 127         | 
16    | Voice          | Load LFO                              | 0 / 127         | *0 = off, 127 = on*
17    | Voice          | AMD                                   | 0 ~ 127         | 
18    | Voice          | LFO Sync to Note On (toggle)          | 0 / 127         | *0 = off, 127 = on*
19    | Voice          | PMD                                   | 0 ~ 127         | 
20    | Voice          | Toggle Operator 1                     | 0 / 127         | *0 = off, 127 = on*
21    | Voice          | Toggle Operator 2                     | 0 / 127         | *0 = off, 127 = on*
22    | Voice          | Toggle Operator 3                     | 0 / 127         | *0 = off, 127 = on*
23    | Voice          | Toggle Operator 4                     | 0 / 127         | *0 = off, 127 = on*
24    | Voice          | Set Algorithm                         | 0 ~ 7           | *0 = 4→3→2→1</br>1 = (`4+3`)→2→1</br>2 = (`4+(3→2)`)→1</br>3 = (`(4→3)+2`)→1</br>4 = (`4→3`)+(`2→1`)</br>5 = 4→(`3+2+1`)</br>6 = (`4→3`)+2+1</br>7 = 4+3+2+1*
25    | Voice          | Feedback Level                        | 0 ~ 7           | 
26    | Voice          | PMS                                   | 0 ~ 7           | 
27    | Voice          | AMS                                   | 0 ~ 3           | 
28    | Voice          | Set LFO Waveform                      | 0 ~ 3           | *0 = Saw</br>1 = Square</br>2 = Triangle</br>3 = Noise*
29    | Voice          | PMD Assign                            | 0 ~ 4           | *0 = None</br>1 = Aftertouch</br>2 = Mod Wheel</br>3 = Breath</br>4 = Foot Controller*
30    | Voice          | Transpose                             | 0 ~ 49          | *0 ~ 24 = "-24 ~ -1"</br>25 ~ 49 = "0 ~ +24"
31    | Voice          | Pitch Bend Range                      | 0 ~ 12          | 
32    | Op1            | TL (Total Level)                      | 0 ~ 127         | 
33    | Op1            | Key Height/TL scaling type (-/+)      | 0 / 127         | *0 = off, 127 = on*
34    | Op1            | Key Height/TL scaling type (Lin/Exp)  | 0 / 127         | *0 = off, 127 = on*
35    | Op1            | Key Velocity/TL sensitivity           | 0 ~ 7           | 
36    | Op1            | Key Height/Envelope Lvl scaling dpth  | 0 ~ 15          | 
37    | Op1            | TL Fine Adjust                        | 0 ~ 15          | 
38    | Op1            | Detune 1 (Coarse)                     | 0 ~ 7           | *0 / 4 = 0</br>1 ~ 3 = -3 ~ -1</br>5 ~ 7 = +1 ~ +3*
39    | Op1            | Freq Multiplier/Detune 2 (Fine)       | 0 ~ 63          | *[see Multi/DT2 frequency chart](freqmultichart.md)*
40    | Op1            | Key Height/Envelope Rt scaling dpth   | 0 ~ 3           | 
41    | Op1            | AR (Attack Rate)                      | 0 ~ 31          | 
42    | Op1            | Toggle AM (Amplitude Modulation)      | 0 / 127         | *0 = off, 127 = on*
43    | Op1            | Key Velocity/Attack Rate sensitivity  | 0 ~ 3           | 
44    | Op1            | D1R (Decay 1 Rate)                    | 0 ~ 31          | 
45    | Op1            | D2R (Decay 2 Rate)                    | 0 ~ 31          | 
46    | Op1            | SL (Sustain Level)                    | 0 ~ 15          | 
47    | Op1            | RR (Release Rate)                     | 0 ~ 15          | 
48    | Op2            | TL (Total Level)                      | 0 ~ 127         | 
49    | Op2            | Key Height/TL scaling type (-/+)      | 0 / 127         | *0 = off, 127 = on*
50    | Op2            | Key Height/TL scaling type (Lin/Exp)  | 0 / 127         | *0 = off, 127 = on*
51    | Op2            | Key Velocity/TL sensitivity           | 0 ~ 7           | 
52    | Op2            | Key Height/Envelope Lvl scaling dpth  | 0 ~ 15          |  
53    | Op2            | TL Fine Adjust                        | 0 ~ 15          | 
54    | Op2            | Detune 1 (Coarse)                     | 0 ~ 7           | *0 / 4 = 0</br>1 ~ 3 = -3 ~ -1</br>5 ~ 7 = +1 ~ +3*
55    | Op2            | Freq Multi/Detune 2 (Fine)            | 0 ~ 63          | *[see Multi/DT2 frequency chart](freqmultichart.md)*
56    | Op2            | Key Height/Envelope Rt scaling dpth   | 0 ~ 15          | 
57    | Op2            | AR (Attack Rate)                      | 0 ~ 31          | 
58    | Op2            | Toggle AM (Amplitude Modulation)      | 0 / 127         | *0 = off, 127 = on*
59    | Op2            | Key Velocity/Attack Rate sensitivity  | 0 ~ 3           | 
60    | Op2            | D1R (Decay 1 Rate)                    | 0 ~ 31          | 
61    | Op2            | D2R (Decay 2 Rate)                    | 0 ~ 31          | 
62    | Op2            | SL (Sustain Level)                    | 0 ~ 15          | 
63    | Op2            | RR (Release Rate)                     | 0 ~ 15          | 
[64]  |                | [Damper Pedal on/off (Sustain)]       | 0 / 127         | *0 = off, 127 = on*
[65]  |                | [Portamento on/off]                   | 0 / 127         | *0 = off, 127 = on*
[66]  |                | [Sostenuto on/off]                    | 0 / 127         | *0 = off, 127 = on*
67    | Op3            | TL (Total Level)                      | 0 ~ 127         | 
68    | Op3            | Key Height/TL scaling type (-/+)      | 0 / 127         | *0 = off, 127 = on*
69    | Op3            | Key Height/TL scaling type (Lin/Exp)  | 0 / 127         | *0 = off, 127 = on*
70    | Op3            | Key Velocity/TL sensitivity           | 0 ~ 7           | 
71    | Op3            | Key Height/Envelope Lvl scaling dpth  | 0 ~ 15          | 
72    | Op3            | TL Fine Adjust                        | 0 ~ 15          | 
73    | Op3            | Detune 1 (Coarse)                     | 0 ~ 7           | *0 / 4 = 0</br>1 ~ 3 = -3 ~ -1</br>5 ~ 7 = +1 ~ +3*
74    | Op3            | Freq Multiplier/Detune 2 (Fine)       | 0 ~ 63          | *[see Multi/DT2 frequency chart](freqmultichart.md)*
75    | Op3            | Key Height/Envelope Rt scaling dpth   | 0 ~ 15          | 
76    | Op3            | AR (Attack Rate)                      | 0 ~ 31          | 
77    | Op3            | Toggle AM (Amplitude Modulation)      | 0 / 127         | *0 = off, 127 = on*
78    | Op3            | Key Velocity/Attack Rate sensitivity  | 0 ~ 3           | 
79    | Op3            | D1R (Decay 1 Rate)                    | 0 ~ 31          | 
80    | Op3            | D2R (Decay 2 Rate)                    | 0 ~ 31          | 
81    | Op3            | SL (Sustain Level)                    | 0 ~ 15          | 
82    | Op3            | RR (Release Rate)                     | 0 ~ 15          | 
83    | Op4            | TL (Total Level)                      | 0 ~ 127         | 
84    | Op4            | Key Height/TL scaling type (-/+)      | 0 / 127         | *0 = off, 127 = on*
85    | Op4            | Key Height/TL scaling type (Lin/Exp)  | 0 / 127         | *0 = off, 127 = on*
86    | Op4            | Key Velocity/TL sensitivity           | 0 ~ 7           | 
87    | Op4            | Key Height/Envelope Lvl scaling dpth  | 0 ~ 15          | 
88    | Op4            | TL Fine Adjust                        | 0 ~ 15          | 
89    | Op4            | Detune 1 (Coarse)                     | 0 ~ 7           | *0 / 4 = 0</br>1 ~ 3 = -3 ~ -1</br>5 ~ 7 = +1 ~ +3*
90    | Op4            | Freq Multiplier/Detune 2 (Fine)       | 0 ~ 63          | *[see Multi/DT2 frequency chart](freqmultichart.md)*
91    | Op4            | Key Height/Envelope Rt scaling dpth   | 0 ~ 15          | 
92    | Op4            | AR (Attack Rate)                      | 0 ~ 31          | 
93    | Op4            | Toggle AM (Amplitude Modulation)      | 0 / 127         | *0 = off, 127 = on*
94    | Op4            | Key Velocity/Attack Rate sensitivity  | 0 ~ 3           | 
95    | Op4            | D1R (Decay 1 Rate)                    | 0 ~ 31          | 
96    | Op4            | D2R (Decay 2 Rate)                    | 0 ~ 31          | 
97    | Op4            | SL (Sustain Level)                    | 0 ~ 15          | 
98    | Op4            | RR (Release Rate)                     | 0 ~ 15          | 
99    | Inst           | # of notes                            | 0 ~ 8           | 
100   | Inst           | MIDI Channel                          | 0 ~ 15          | 
101   | Inst           | KC Limit/L                            | 0 ~ 127         | 
102   | Inst           | KC Limit/H                            | 0 ~ 127         | 
103   | Inst           | Voice Bank                            | 0 ~ 6           | 
104   | Inst           | Voice #                               | 0 ~ 47          | 
105   | Inst           | Detune                                | 0 ~ 127         | 
106   | Inst           | Octave Transpose                      | 0 ~ 4           | *-2 ~ +2*
107   | Inst           | Output Level                          | 0 ~ 127         | 
108   | Inst           | Pan                                   | 0 / 64 / 127    | *0 = L</br>64 = LR</br>127 = R*
109   | Inst           | LFO Enable                            | 0 / 127         | *0 = off, 127 = on*
110   | Inst           | Pitch Bend Range                      | 0 ~ 12          | 
111   | System         | Config Number                         | 0 ~ 19          | 
112   | System         | Channel Number                        | 0 ~ 15          | 
113   | System         | Master Detune                         | 0 ~ 127         | *0 ~ 63 = 0 ~ 63</br>64 ~ 127 = -64 ~ -1*
114   | -              | ***{currently unused}***              | -               | -
115   | Voice          | LFO Speed                             | RBOff           | *64 = 0</br>64 + x = +x</br>64 -x = -x*
116   | Voice          | Name (Char #1)                        | 0 ~ 127         | 
117   | Voice          | Name (Char #2)                        | 0 ~ 127         | 
118   | Voice          | Name (Char #3)                        | 0 ~ 127         | 
119   | Voice          | Name (Char #4)                        | 0 ~ 127         | 
120   | Voice          | Name (Char #5)                        | 0 ~ 127         | 
121   | Voice          | Name (Char #6)                        | 0 ~ 127         | 
122   | Voice          | Name (Char #7)                        | 0 ~ 127         | 
[123] |                | [All Notes Off]                       | 0 / 127         | *0 = off, 127 = on*
124   | Voice          | User Code                             | RBOff           | *64 = 0</br>64 + x = +x</br>64 -x = -x*
125   | System         | Master Output Level                   | 0 ~ 127         | 
[126] |                | [Mono Mode on/Poly off/All Notes Off] | 1               | 
[127] |                | [Poly Mode on/Mono off/All Notes Off] | 0               | 
