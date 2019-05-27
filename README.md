# euu_parlolarment
Fudged data explorer for EU parliamentary election results  
## Historically mixed labelling and changing schemas prevents true utility of the tool  
Very unlikely to be future updates to this, aside from some more basic function additions  
The tool will fetch and locally store the datasets required for the given question  
## Deps
Python 3.7+  
argparse  
json  
os  
requests  
## Usage
python eu_parlolarment.py -c $COUNTRY_CODE -q $QUESTION -y $YEAR  
  
- The default country code is UK  
- The default year is 2019  
    
Currently, following questions available:  
- turnout (default): returns EU total and $COUNTRY_CODE voter turnouts as percentage  
- votes: returns vote numbers for $COUNTRY CODE, including vote changes where the data/schema aren't broken  
## Issues
As the data are available, election iterations contain:  
- different identifier entries for the same party  
- different naming conventions for the same parties (and some parties change their names anyway)  
- different schema going back further than 2009  
  
This tool is not valuable enough to develop for accounting for these issues and is useful as a quick reference script for the next few weeks  
  
Turnout data are working going back to the first data in the series  
