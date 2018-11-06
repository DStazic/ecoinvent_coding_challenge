# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

from matplotlib.patches import BoxStyle

class plotting(object):
             
    
    def __init__(self,parser):
        self.parser = parser
        
    
    def plotResults(self):
        """
        Initiates a figure canvas and adds activity/production name, geographic location, exchange groups
        and the relevant arrows denoting the flow of exchange groups
        """
        # figure object, axes object 
        fig,ax = self.canvas() 
        # bounding box setting 
        box = dict(boxstyle='round', facecolor='blue', alpha=0.8,pad=1)
        # set textbox for activity/production/geographic location element
        text_ACTIVITY = "ACTIVITY: "+self.formatText(self.parser.ACTIVITY)+"\n"+"GEOGRAPHY: "+self.parser.GEOGRAPHY 
        textbox=ax.text(0.4, 0.55, text_ACTIVITY,  fontsize=22, color="white", verticalalignment='center',bbox=box)
        # transformed coordinates of the bounding box
        box_bounds = self.transform(textbox,ax) #x0,y0; x1,y1
        # set text, arrow parameter for other exchange groups 
        self.MAPPING = { "TECHOSPHERE_IN":{"type":self.parser.TECHNOSPHERE["input"],"text" : [0.05, 0.55], 
                                            "arrow":[0.3, 0.55, 0.05, 0], "align":"top"},
                "TECHOSPHERE_OUT":{"type":self.parser.TECHNOSPHERE["output"],"text":[box_bounds[1][0]+0.08, 0.5], 
                                   "arrow":[box_bounds[1][0]+0.02, 0.52, 0.03, -0.02],"align":"top"},
                "ENVIRONMENT_IN":{"type":self.parser.ENVIRONMENT["input"],"text":[0.4, 0.37], 
                                  "arrow":[0.45, 0.4, 0., 0.05],"align":"top"},
                "ENVIRONMENT_OUT":{"type":self.parser.ENVIRONMENT["output"],"text":[0.4, 0.72],
                                   "arrow":[0.45, 0.64, 0., 0.05],"align":"bottom"},
                "REFERENCE":{"type":self.parser.REFERENCE_PRODUCT,"text" : [box_bounds[1][0]+0.08, 0.63], 
                             "arrow" : [box_bounds[1][0]+0.02, 0.58, 0.03, 0.02],"align":"top"}}
        
        for key,setting in self.MAPPING.items():
            exchange_group = setting["type"]
            
            if  exchange_group != {}:
                text = self.formatText(exchange_group)
                text_coord, arrow_coord = self.getCoordinates(setting)
                
                ax.text(text_coord[0],text_coord[1], text, fontsize=22, verticalalignment=setting["align"])
                ax.arrow(arrow_coord[0],arrow_coord[1],arrow_coord[2],arrow_coord[3], 
                         head_width=0.02, head_length=0.01, fc='k', ec='k') 
        
        return fig
        
                
                
        
    def formatText(self,exchange_group):
        """
        Takes an exchange group dictionary as input. Combines all exchange names into following formated 
        text string that is returned: "quantity unit of exchange name 1\nquantity unit of exchange name 2\n..."
        
        exchange_group: dictionary referencing an exchange group (e.g. Technosphere input)
        """
        text = []
        try:
            for exchange,val in exchange_group.items():
                if len(exchange.split()) >= 4:
                    processed = "\n".join([" ".join(exchange.split()[:2])," ".join(exchange.split()[2:])])
                    text.append("- {0} {1} of {2}".format(val,self.parser.UNITS[exchange],processed))
                else:    
                    text.append("- {0} {1} of {2}".format(val,self.parser.UNITS[exchange],exchange))
        except AttributeError:
                if len(exchange_group) >= 35:
                    processed = ",\n".join([exchange_group.split(",")[0],exchange_group.split(",")[1]])
                    text.append(processed)
                else:
                    text.append(exchange_group)
        return "\n".join(text)
                
        
       
    def getCoordinates(self,setting):
        """
        Takes the parameter dictionary (see MAPPING) of an exchange group and returns the text, arrow coordinates
        
        setting: parameter dictionary
        """
        text_coord = setting["text"]
        arrow_coord = setting["arrow"]
        return text_coord, arrow_coord
        
        
    def transform(self, text_object, axes_object):
        """
        Transforms display coordinates of a text object into corresponding data coordinates
        
        text_object: text object (defined via ax.text())
        axes_object: axes object (defined via fig, ax = plt.subplots()) 
        """
        fig = plt.figure(figsize=(38, 15))
        inv = axes_object.transData.inverted()
        renderer = fig.canvas.get_renderer()
        bounding_box = text_object.get_window_extent(renderer=renderer)
        return inv.transform(bounding_box._points)
        

    def canvas(self):
        """
        Initializes and returns a matplotlib pyplot figure object, axes object
        """
        fig, ax = plt.subplots(figsize=(38, 15))
        plt.axis('off')
        
        return fig,ax
