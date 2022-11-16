# Simple_DAQ
# acquire data from common instrument in lab

Apps:
1. Simple_DAQ_beta.py: Main UI
2. Visa_troubleshooting.py: test connection with single instrument
3. Datafile editor.py: contatenate same format data in the folder,
			comparing different tempstamp to match data

Instrument_Drivers:
Instrument_dict.py: Includes names and function of following instrument

requirements.txt: contains the relying package

----------------------------------------------------------------------------

To add more instrument/Functions:
1. Edit/add funtion in Instrument_Drivers folder
2. if new driver added:
	mport the new driver in format:
		from [your driver name] import *
3. if new driver/ function added:
	change the get_value(), set_value() function accordingly
