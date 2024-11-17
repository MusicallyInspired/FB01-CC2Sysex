# FB01-CC2Sysex
This script reads MIDI message from an input port and passes them through to an output port. If CC messages are sent through that correspond to the (currently hardcoded) mapped CCs for setting voice, instrument, config, or system data parameters on the FB-01 it will convert the values of those intercepted CC messages into the proper sysex messages.

## Dependencies
* Mido
* Colorama

### Current State:
This script is currently still unfinished. Its basic functions work (please report any bugs if you run into any!) but right now it will start with a default blank slate "INIT" voice parameters. There isn't currently any implementation to let the FB-01 know that. Which means any modifications to parameters will be done in context with the "INIT" voice and you could see parameters reset to zero (or whatever the defaults are) that share sysex messages with other parameters that you modify. Meaning you'll have to set those again.

### Feature Wishlist
* Implement a voice dump request from the FB-01 on startup so that you can modify the voice currently selected on the FB-01 (this will require a second MIDI input port in addition to the MIDI controller input port so that dumped sysex data from the FB-01 can be read)
* Dedicate a MIDI CC to manually triggering a voice data dump from the FB-01 at any time (if you want to select a different voice on the FB-01 to modify, for instance)
* Dedicate a MIDI CC to sending an "INIT" voice dump _to_ the FB-01 so you can start from scratch again at any time
* Make it easier to make your own CC to Sysex assignments, including removing some Sysex messages you don't want or need to make room for others (there are technically more sysex messages than there are CC controllers to utilize)
* Possible RPN/NRPN implementation as an alternative when running out of CCs?

## Current Hardcoded CC Mapping
[Click here to view the full chart](mappingchart.md).

### Multi/DT2 Parameter Frequency Chart
CCs 39, 55, 74, and 90 are dedicated to changing each of the 4 Operators' frequency multiplier. It modifies both the Multi and DT2 (Fine Detune) parameters together to span the entire range of multiplier values available. Multi has 16 values and DT2 has 4 bringing a maximum range of 64. Below shows the frequency multiplier values that each CC value corresponds to:

CC Value | Multi       | DT2       | Multiple
:------: | :---------: | :-------: | :---:
0        | 0           | 0         | 0.50
1        | 0           | 1         | 0.71
2        | 0           | 2         | 0.78
3        | 0           | 3         | 0.87
4        | 1           | 0         | 1.00
5        | 1           | 1         | 1.41
6        | 1           | 2         | 1.57
7        | 1           | 3         | 1.73
8        | 2           | 0         | 2.00
9        | 2           | 1         | 2.82
10       | 3           | 0         | 3.00
11       | 2           | 2         | 3.14
12       | 2           | 3         | 3.46
13       | 4           | 0         | 4.00
14       | 3           | 1         | 4.24
15       | 3           | 2         | 4.71
16       | 5           | 0         | 5.00
17       | 3           | 3         | 5.19
18       | 4           | 1         | 5.65
19       | 6           | 0         | 6.00
20       | 4           | 2         | 6.28
21       | 4           | 3         | 6.92
22       | 7           | 0         | 7.00
23       | 5           | 1         | 7.07
24       | 5           | 2         | 7.85
25       | 8           | 0         | 8.00
26       | 6           | 1         | 8.48
27       | 5           | 3         | 8.65
28       | 9           | 0         | 9.00
29       | 6           | 2         | 9.42
30       | 7           | 1         | 9.89
31       | 10          | 0         | 10.00
32       | 6           | 3         | 10.38
33       | 7           | 2         | 10.99
34       | 11          | 0         | 11.00
35       | 8           | 1         | 11.30
36       | 12          | 0         | 12.00
37       | 7           | 3         | 12.11
38       | 8           | 2         | 12.56
39       | 9           | 1         | 12.72
40       | 13          | 0         | 13.00
41       | 8           | 3         | 13.84
42       | 14          | 0         | 14.00
43       | 10          | 1         | 14.10
44       | 9           | 2         | 14.13
45       | 15          | 0         | 15.00
46       | 11          | 1         | 15.55
47       | 9           | 3         | 15.57
48       | 10          | 2         | 15.70
49       | 12          | 1         | 16.96
50       | 11          | 2         | 17.27
51       | 10          | 3         | 17.30
52       | 13          | 1         | 18.37
53       | 12          | 2         | 18.84
54       | 11          | 3         | 19.03
55       | 14          | 1         | 19.78
56       | 13          | 2         | 20.41
57       | 12          | 3         | 20.76
58       | 15          | 1         | 21.20
59       | 14          | 2         | 21.98
60       | 13          | 3         | 22.49
61       | 15          | 2         | 23.55
62       | 14          | 3         | 24.22
63       | 15          | 3         | 25.95
