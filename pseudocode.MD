### pseudocode

**parse XML file**

1. initialize instance of parser class with empty dictionaries TECHNOSPHERE -, ENVIRONMENT -, UNITS as object variables (TECHNOSPHERE -, ENVIRONMENT dicts each store two sets of dictionaries specifying input/output exchange groups)
2. iterate over each element in file 
3. use element tag name to check if an element corresponds to a relevant textbox used in the figure 
   - "intermediateExchange" = Technosphere input, Reference product, Byproducts (technosphere group) 
   - "elementaryExchange" = Input, output from, to environment (environment group)
   - "activityName" = Type of activity/production
   - "geography" = name of location   
4. if element tag is "activityName"
        - set the element text as ACTIVITY var 
        (Activity textbox in the figure)
        
5. if element tag is "geography" 
        - find the child element "shortname" and set the child element text as GEOGRAPHY 
        (Geography short-name textbox in the figure)
        
6. if element corresponds to technosphere or environment main group
        - get exchange name (child element), unit name (parent element attr), quantity (amount or volume; parent
        element attr), group-type (inputGroup vs. outputGroup; child element, only one type per parent element) 
        - add unit name to UNITS dict
        
        if element describes technosphere main group  
            if outputGroup is child element and text is 0
                - round quantity to 4 digits
                - set REFERENCE_PRODUCT dict with exchange name as key and quantity (volume) as value
                
            if outputGroup is child element and text is 2
                - Byproduct identified
                - apply merge/add method
                
            if inputGroup is child element and text is 5
                - Technosphere input identified
                - apply merge/add method  
                
                
        if element describes environment main group 
            if inputGroup is child element and text is 4
                - Input from environment identified
                - apply merge/add method
            
            if outputGroup is child element and text is 4
                - Output to environment identified
                - apply merge/add method
             
        merge/add method 
        if exchange is not present in dict (TECHOSPHERE vs. ENVIRONMENT)
            - add parent element text to dict as key and quantity as value
            - add parent element text to UNITS dict as key and unit name as value 
        elif exchange is already present in dict
            - add "parent element text, combined" to the dictionary as key and summed quantities as value
            - add the new key to UNITS dict
            - delete already present exchange from dictionary            
7. Following parsing, iterate over each set of key value pairs in the TECHNOSPHERE input/output and ENVIRONMENT
    input/output dictionaries
8. round each value to 4 digits
9. set sorted_group list and add "key,value" pairs (tuple) sorted according to value in descending order 
10. if dictionary is TECHNOSPHERE output
        - set number of max entries to 4
    else 
        - set number of max entries to 5
11. while dictionary length is bigger than corresponding max number
        - remove the (key,value) tuple with the smallest value (first item) from sorted_group
        - use the key from the removed item to specifically delete the cognate entry from the corresponding dictionary 
        

**plot figure**

1. initialize plotting class instance with parser object (parser class instance) as object variable
2. initialize matplotlib figure and axes object 
3. set text_ACTIVITY var to store Activity/production name and the geographic location
   set the textbox for text_ACTIVITY, assign colored bounding box to highlight the text and add to figure
4. set the MAPPING dictionary to define the textbox parameters for all other textboxes (Technosphere input, output;
    From, to environment; Reference product) as well as coordinates of arrow object that will be used to display the
    flow of exchange groups
    - for arrow relevant to display flow of Reference product, Byproduct use bounding box coordinates of text_ACTIVITY textbox to define arrow coordinates relative to the text_ACTIVITY width 
5. for each non-empty exchange group dictionary (not always all exchange groups present)
        - set text list
        - iterate over each key value pair
            use the key to access the value unit name via parser.UNITS dictionary 
            combine key, value, unit name as a string and format as follows: "quantity unit of exchange name\n" 
            add formated string to text list
            
        - set the textbox with text list and add to figure
        - set the relevant arrow object and add to figure
6. return figure 

**pipeline**
1. pass folder name storing all spold files, parserXML class and plotting class as pipeline function arguments
2. for each spold file
     - set path variable to reference file 
     - instantiate parseXML class with the path var as argument
     - initiate parsing of the file
     - instantiate plotting class with parser object as argument
     - initiate plotting
     - save figure in same folder 