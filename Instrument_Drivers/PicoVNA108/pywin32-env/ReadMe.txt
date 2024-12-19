How to update ~\dist\PicoVNA108_server.exe:
	- make changes to PicoVNA108_server.py
	- win+R and type 'cmd', enters the termial
	- type 'cd C:\Users\Crow108\Documents\GitHub\Simple_DAQ\Instrument_Drivers\PicoVNA108\pywin32-env', change the path to this folder path or similar if position moved
	- type '.\python.exe -m PyInstaller --onefile PicoVNA108_server.py'
wait for completion