# Cura SingleNozzle
# Author:   Christian Koehlke
# Date:     September 08, 2019
#
# a postprocessing script for cura to use a single Nozzle
#
# Cura thinks, if you have two extruder you must have two heaters.
# So, if extruder should be activated, cura activates heater 2 and deactivates heater 1,
# which lead to cold extrusion.
# This script fixes this problem
#
#   How it works
# it searches for for every "M104 S0" command in the G-Code and deletes it.    
# Also, it searches for every M104 and changes it to M109 so the print doesnt pause, when the temp drops a little bit
# In the End it deletes every M104 regarding to a different nozzle than T0.

from ..Script import Script
from UM.Application import Application

class SingleNozzle(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "SingleNozzle",
            "key": "SingleNozzle",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "active":
                {
                    "label": "SingleNozzle",
                    "description": "When enabled, the script is enabled. Changes every M109 to M104. deletes all M106 and M104 in terms of non existing heaters T1,T2... deletes all lines where heater0 is set to 0",
                    "type": "bool",
                    "default_value": true
                },
                "deleteFirstM109":
                {
                    "label": "change first M109",
                    "description": "When enabled, the script will also change the first M109 to M104. Which should be used when heating the nozzle before the print. This value should be set on false",
                    "type": "bool",
                    "default_value": false
                },
                "deleteM109M104":
                {
                    "label": "delete further M109 M104",
                    "description": "When enabled, the script will also delete further M106 and M104 starting from layer 2. Cura will change the temperature of heater0 to its stanby-temperature. this will stop it.",
                    "type": "bool",
                    "default_value": false
                }
            }
        }"""

    def execute(self, data):
        
        active = self.getSettingValueByKey("active")
        deleteFirstM109 = self.getSettingValueByKey("deleteFirstM109")
        deleteM109M104 = self.getSettingValueByKey("deleteM109M104")
        
        first_Layer=0
        last_Layer=len(data)-1
        firstM109=False
        
        
        
        if active:
            for layer in data:
                
                
                
                layer_Index = data.index(layer)
                lines = layer.split("\n")
                
                if ((layer_Index != last_Layer)):
                    
                    for line in lines:
                        line_Index = lines.index(line)
                    
                        if (line.startswith("M109")):                                                           #Wait for temperature in midprint
                            if ((deleteFirstM109 == False) and (firstM109 == False)):
                                firstM109=True
                            else:
                                lines.remove(line)
                                line = line.replace("M109","M104")
                                lines.insert(line_Index,line)
                        
                        if ((line.startswith("M109")) or (line.startswith("M104"))):                            #Non existing Heater
                            T_Index=line.find("T")
                            if (T_Index>=0): 
                                if (line[T_Index+1].isdigit()):
                                    if (int(line[T_Index+1]) != 0):  
                                        lines.remove(line)
                                        line="; removed M104 or M109 Hotendtemperature for non existing Heater"
                                        lines.insert(line_Index,line)
                        
                        if (line.startswith("M104 T0 S0") or line.startswith("M109 T0 S0")):                    #Prevent Heater shutdown on T0
                            lines.remove(line)
                            line="; removed Hotendtemperature S0 for T0"
                            lines.insert(line_Index,line)

                        if ( (line.startswith("M109")) or (line.startswith("M104")) ) and (layer_Index>2) and (deleteM109M104):      #delete further M109 and M104
                            lines.remove(line)
                            line="; removed M104 or M109 Hotendtemperature"
                            lines.insert(line_Index,line)
                            
                        
                result = "\n".join(lines)
                data[layer_Index] = result

            
        return data
