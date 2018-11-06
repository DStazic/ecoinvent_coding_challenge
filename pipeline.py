# -*- coding: utf-8 -*-

import os
import re
from parser import *
from plotter import *

def pipeline(folder_name,parseXML,plotting):
    """
    Takes the folder name where the spold files are stored, parseXML class and plotting class as input.
    For each file, parsing and plotting is invoked. The figure is saved in png format in the same folder.
    """
    # take only spold files to avoid downstream errors
    folder = [f for f in os.listdir(os.path.join(os.getcwd(),"files")) if re.search(r"\bspold\b", f)]
    
    for file_ in folder:
        path = os.path.join(os.getcwd(),"files",file_)
        #parsing
        parser = parseXML(path)
        parser.process()
        
        # plotting
        plotter = plotting(parser)
        figure = plotter.plotResults() 

        figure.savefig(os.path.join(os.getcwd(),folder_name,"{}_figure.png".format(file_)))
        
        
if __name__ == "__main__":        
    pipeline("files",parseXML,plotting) 