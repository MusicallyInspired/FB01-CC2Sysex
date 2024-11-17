# FB01-CC2Sysex
This script reads MIDI message from an input port and passes them through to an output port. If CC messages are sent through that correspond to the (currently hardcoded) mapped CCs for setting voice, instrument, config, or system data parameters on the FB-01 it will convert the values of those intercepted CC messages into the proper sysex messages. My original intention for this script was for it to be run on a Raspberry Pi with a MIDI interface so I could control the FB-01 parameters with my MIDI controller and still be mobile without the need of a computer or laptop setup. But it works just as well if you don't have a Raspberry Pi.

## Dependencies
* Mido
* Colorama *(for console log output, possibly temporary)*

### Current State:
This script is currently still unfinished. Its basic functions work (please report any bugs if you run into any!) but right now it will start with a default blank slate "INIT" voice parameters. There isn't currently any implementation to let the FB-01 know that. Which means any modifications to parameters will be done in context with the "INIT" voice and you could see parameters reset to zero (or whatever the defaults are) that share sysex messages with other parameters that you modify. Meaning you'll have to set those again.

### Feature Wishlist
* Implement a voice dump request from the FB-01 on startup so that you can modify the voice currently selected on the FB-01 (this will require a second MIDI input port in addition to the MIDI controller input port so that dumped sysex data from the FB-01 can be read)
* Dedicate a MIDI CC to manually triggering a voice data dump from the FB-01 at any time (if you want to select a different voice on the FB-01 to modify, for instance)
* Dedicate a MIDI CC to sending an "INIT" voice dump _to_ the FB-01 so you can start from scratch again at any time
* Make it easier to make your own CC to Sysex assignments, including removing some Sysex messages you don't want or need to make room for others (there are technically more sysex messages than there are CC controllers to utilize)
* Possible RPN/NRPN implementation as an alternative when running out of CCs?

### CC/Sysex Mapping Chart
[Click here to view the full chart](mappingchart.md)

### Multi/DT2 Parameter Frequency Chart
[Click here to view the full chart](freqmultichart.md)
