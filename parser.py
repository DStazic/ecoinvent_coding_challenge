# -*- coding: utf-8 -*-

from collections import defaultdict
import xml.etree.ElementTree as ET

class parseXML(object):
    
    NAMESPACE =  '{http://www.EcoInvent.org/EcoSpold02}'
    
    def __init__(self, file_):
        self.file = file_
        
        self.TECHNOSPHERE = {"input" : defaultdict(int),
                             "output" : defaultdict(int)
                            }
        self.ENVIRONMENT = {"input" : defaultdict(int),
                            "output" : defaultdict(int)
                           }
        
        self.UNITS = dict()
        
        
    def parseFile(self):
        """
        Loads a XML file and iterates over each element. Each element is passed to applyFilter method
        """
        tree = ET.parse(self.file)       # build element tree
        for element in tree.iter():      # iterate over the document
            self.applyFilter(element)
            
    
    def applyFilter(self,element):
        """
        Takes a XML element as input. If the element tag matches any key in the MAPPING dict,
        the corresponding filter function is invoked.
        
        element: xml.etree.ElementTree element object 
        """
        
        MAPPING = {self.NAMESPACE + "intermediateExchange" : self.technosphereFilter,      #products, techosphere input
                   self.NAMESPACE + "elementaryExchange" : self.environmentFilter,         #input environment, emission 
                   self.NAMESPACE + "activityName" : self.activityFilter,                  #name of activity
                   self.NAMESPACE + "geography" : self.geographyFilter                     #location identifier
                  }
        try:
            MAPPING[element.tag](element)
        except KeyError:
            pass
               
                
    def mergeSameType(self,exchange_group,exchange_name,quantity,unit_name):
        """
        Checks if an exchange name is already present in the corresponding exchange group dictionary. If included,
        quantities of present exchange and exchange of interest are summed up and stored using the key "exchange name,
        combined". The present exchange is removed from the dictionary.
        If not included, the exchange of interest is added to the dictionary using the name as key and quantity as value.
        If a new key is defined, the UNITS dictionary is updated with the new key and the corresponding unit name as value.
        
        exchange_group: dictionary referencing an exchange group (e.g. Technosphere input)
        exchange_name: name describing an exchange (string; e.g. electricity)
        quantity: quantity of exchange (float)
        unit_name: unit name of the quantity (string)
        """
        
        for k in exchange_group.keys():
            if exchange_name == k:
                return False
            
            if exchange_name.split(",")[0] in k:
                #check 1: not the same type of exchange but overlapping parts of name
                #--> e.g., "urea formaldehyde resin" vs. "urea, as N"
                if len(exchange_name.split(",")) != len(k.split(",")):
                    return False
                
                if self.UNITS[exchange_name] == self.UNITS[k]:
                    new_name = "{}, combined".format(exchange_name.split(",")[0])
                    self.UNITS[new_name] = unit_name
                    if new_name in exchange_group.keys():
                        exchange_group[new_name] += quantity
                        return True
                    else:
                        #exchange_group[new_name] = round((exchange_group[k]+quantity),4)
                        exchange_group[new_name] = exchange_group[k]+quantity
                        del exchange_group[k] 
                        return True
                        
        
    def parseMetadata(self,element):  
        """
        Takes a XML element that describes an exchange as input and returns the exchange name, 
        exchange amount (1 type of quantity), amount unit name. 
        If applicable, inputGroup or outputGroup (child elements) type is returned, otherwise None is returned.
        
        element: xml.etree.ElementTree element object
        """
        
        name = ",".join(element.find(self.NAMESPACE + "name").text.split(",")[:2]) # hierarchical order in name string; use name only
        unit_name = element.find(self.NAMESPACE + "unitName").text
        self.UNITS[name] = unit_name 
        amount = float(element.attrib["amount"])
        
        
        try:
            input_group = element.find(self.NAMESPACE + "inputGroup").text
        except AttributeError:
            input_group = None
        try:    
            output_group = element.find(self.NAMESPACE + "outputGroup").text
        except AttributeError:
            output_group = None
            
        return name,amount,unit_name,input_group,output_group   
    
    def addExchange(self,exchange_group,exchange_name,quantity,unit_name):
        """
        Adds an exchange name to the corresponding exchange group or updates the exchange group if type of exchange
        is already present (combines same exchange types).
        
        exchange_group: dictionary referencing an exchange group (e.g. Technosphere input)
        exchange_name: name describing an exchange (string; e.g. electricity)
        quantity: quantity of exchange (float)
        unit_name: unit name of the quantity (string)
        """
        if not self.mergeSameType(exchange_group,exchange_name,quantity,unit_name):# and quantity != 0.:
            exchange_group[exchange_name] += quantity
        
            
    
    def technosphereFilter(self,element):
        """
        Takes an XML element that was classified as a member of the TECHNOSPHERE main group and
        adds the cognate exchange to the relevant TECHNOSPHERE dictionary (input/output). 
        
        element: xml.etree.ElementTree element object
        """
        name, amount, unit_name,input_group, output_group = self.parseMetadata(element)
        
        if input_group == "5":
            self.addExchange(self.TECHNOSPHERE["input"],name,amount,unit_name)

        #add reference product
        if output_group == "0":
            volume = round(float(element.attrib["productionVolumeAmount"]),4)
            self.REFERENCE_PRODUCT = {name: volume}
            
        #add byproducts
        elif output_group == "2":   
            volume = float(element.attrib["productionVolumeAmount"])
            self.addExchange(self.TECHNOSPHERE["output"],name,volume,unit_name)
                
            
            
    def environmentFilter(self, element):
        """
        Takes an XML element that was classified as a member of the ENVIRONMENT main group and
        adds the cognate exchange to the relevant ENVIRONMENT dictionary (input/output). 
        
        element: xml.etree.ElementTree element object
        """
        name,amount,unit_name, input_group, output_group = self.parseMetadata(element)
        # from environment
        if input_group == "4":  
            self.addExchange(self.ENVIRONMENT["input"],name,amount,unit_name)
        # to environment
        if output_group == "4":   
            self.addExchange(self.ENVIRONMENT["output"],name,amount,unit_name)
                    
        
    
    def activityFilter(self,element):
        """
        Takes the XML element that stores information about the activity/production and returns the 
        corresponding name
        
        element: xml.etree.ElementTree element object
        """
        self.ACTIVITY = ",".join(element.text.split(",")[:2])
                
    
    def geographyFilter(self,element):
        """
        Takes the XML element that stores information about the geographic location and returns the 
        corresponding name
        
        element: xml.etree.ElementTree element object
        """
        self.GEOGRAPHY = element.find(self.NAMESPACE+"shortname").text
    
   
    
    def filterResults(self):
        """
        Rounds values of each exchange group to 4 digits and filters each exchange groups to include 5 elements max
        """
        MAPPING = {"TECHNOSPHERE_IN" : self.TECHNOSPHERE["input"],
                   "TECHNOSPHERE_OUT" : self.TECHNOSPHERE["output"],
                   "ENVIRONMENT_IN" : self.ENVIRONMENT["input"],
                   "ENVIRONMENT_OUT" : self.ENVIRONMENT["output"]}
        
        for key,exchange_group in MAPPING.items():
            
            tmp = {(k,round(v,4)) for k,v in exchange_group.items()} #round exchange values
            exchange_group.update(tmp)
            sorted_group = sorted([(k,v) for k,v in exchange_group.items()], key = lambda x: x[1])     
            max_number = 4 if key == "TECHNOSPHERE_OUT" else 5   
                
            while len(exchange_group) > max_number:
                to_remove = sorted_group.pop(0)[0] #take key of smallest quantity exchange
                del exchange_group[to_remove]
            

    def process(self):
        """
        Invokes parsing
        """
        self.parseFile()  #extract all data
        self.filterResults()
