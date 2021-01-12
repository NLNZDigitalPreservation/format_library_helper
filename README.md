# Format Library Helper

This tool is designed to help digital preservation file format researchers by:- 

1. Amalgamating several file format information sources (Currently PRONOM, Wikidata, LOC and NARA format information). 
2. Provide a place for local data keeping per format (file count, collection / depositor source count, technical notes, risk measurement)
3. Generate shareable JSON files per format that supports information sharing and reuse. 
4. A structured system for storing documentation, specifications, technical notes and other useful data. 

The tool requires python (v3.4 or greater), and access to some external tools (noted below) - these provide the underlying data layer that has been cross walked and linked via the tool. 

# Install Notes. 

Download and unpack this repository into a convenient location. This location forms the root folder of this tool. Any new folders are inside this root folder. 

e.g. `c:\tools\format_library_helper`

## Steps

1. Get a harvest of the PRONOM dataset via ROY

There is a copy included in this download, this is the method of refreshing that copy should you require an updated version.

https://www.itforarchivists.com/siegfried

From commandline:

"roy harvest"

look in the default location (C:\Users\your_user_name\siegfried) for the folder called PRONOM, 
and copy it into the folder called "sources" that is in the same folder as ui.py

e.g `c:\tools\format_library_helper\sources\pronom`

The first time you run it, it will take a couple of minutes to complete. Behind the scenes its making a backup file in the folder  `c:\tools\format_library_helper\pickles`

2. Get a harvest of the LOC Digital Formats Descriptions as XML (fddXML)

https://www.loc.gov/preservation/digital/formats/fdd/fdd_xml_info.shtml

//www.loc.gov/preservation/digital/formats/fddXML.zip  

Unpack the zip into a folder in sources called "fddXML"

e.g `c:\tools\format_library_helper\sources\fddXML`

3. Populate `formats_breakdown.csv`

The build starts with this file empty. It’s a simple csv file, that uses two columns. 

Format ID (as PUID used in PRONON, e.g. fmt/1 or x-fmt/100), and the number of files you have of that format. It doesn't matter if you don't have this information, the UI still works as a knowledgebase. 

4. Populate `rosetta_collections_per_format.csv`

The build starts with this file empty. 
Its a simple csv file, that uses two columns. 

Format ID (as PUID used in PRONON, e.g. fmt/1 or x-fmt/100), and the number of files collections/producers that have deposited that format. 

This data is a higher granularity than straight file count and tries to group the number of sources of a given file type you have in your archive. This data is included because it adds an interesting extra perspective that broadens any understanding we might have of the "ubiquity" of a given format within our archives and collections. 

It doesn't matter if you don't have this information, the UI still works as a knowledgebase.

5. Set the local variables for data sources.

Line #14
`format_library_nodes = "format_library_nodes"`

This is the storage folder that holds all the local data. 

Its set to be inside the project folder by default (e.g. `c:\tools\format_library_helper\format_library_nodes` however, this could be anywhere visible to your machine. If you want to share this data within your team / organisation, set this to a shared/networked folder.

When a file format is worked on with the tool, a node is created in this folder. Its labelled as the puid - so fmt/3 is labelled as `fmt_3` and it contains four folders that you can use to store format related information. 

E.g. `c:\tools\format_library_helper\format_library_nodes\fmt_3`

### local_data

This is where the file format specific JSON is keep and maintained. This is the sharable unit that can be exchanged with other users. It’s also the data source that’s used to provide collection level analysis (these tools will be released as they are built). 

### other_resources

This is a general storage folder for any data you must manage along with this file format

### specifications

This is intended to be where any formal documentation is stored.

### web-pages

Sometimes the only data we can find is informal or 'unofficial' web-pages. This location is intended for warc files/mhtml archives of any web pages that are identified as being useful for understanding this file format. 

We have used other folders in this location for other useful information types, future version may increase the data folders accordingly.

Line #15
`test_set_location = r"E:\testSet"`

This is a pointer to a collection of files of any given file format - we have a copy of a small number of files of all PUIDs organised by PUID label 

e.g. 
`E:\testSet\fmt_3`
`E:\testSet\fmt_4`
`E:\testSet\fmt_5`
etc. 

This isn’t needed to run the tool but is very useful additional resource to aid collection analysis and file format research. 


# Tour of the features

The tool comprises 4 information panes. 

It is designed to float on top of all other windows so it’s always visible. This can be turned off (if you're using a small screen, or a single screen) by finding the line (#806) 

`form = ui.FlexForm(layout, no_titlebar=True, keep_on_top=True, grab_anywhere=True, return_keyboard_events=True)`

and changing the `keep_on_top` argument to `False`: 

`form = ui.FlexForm(layout, no_titlebar=True, keep_on_top=False, grab_anywhere=True, return_keyboard_events=True)`

The tool is also designed to be "grabbed" or clicked on anywhere, so it can be easily moved around the screen if it is in the way. This feature can be changed in the same line (#806).

`form = ui.FlexForm(layout, no_titlebar=True, keep_on_top=True, grab_anywhere=True, return_keyboard_events=True)`

and changing the `grab_anywhere` argument to `False` and `no_titlebar` to `False`: 

`form = ui.FlexForm(layout, no_titlebar=False, keep_on_top=True, grab_anywhere=False, return_keyboard_events=True)`

With these changes, it behaves like a typical windowed application. 

## Pane #1 - Search / PRONOM Helper

The leftmost pane is for search. There are 4 search methods, available in the four entry boxes. The results are shown in the large scrolling box at the bottom. 

### Search PUID

Enter any puid into this box, (e.g. "fmt/43") and the result box shows the PRONOM MIME and registered extensions

### Search extension

Enter any file extension into this box (e.g. wav) and the results box shows all the PUIDs that have that extension registered with PRONOM. 

### Search MIME

Enter any MIME into this box (e.g. image/gif) and the results box shows all the PUIDs that have that MIME registered with PRONOM

### Search keyword

Enter any text into this box (e.g. audio) and the results box shows all the PUIDs that have that text included in its PRONOM description


The Red button at the bottom of this pane copies all the contents of the results box into the clipboard so it can be pasted into other documents. 

Any PUID in the results pane can be double clicked to be highlighted, and if the `left alt` key is pressed, its passed to the next pane as a populated PUID. 

## Pane #2 - Populated PUID

This pane is the main information source for any puid. Any PUID can be populated via the 'Search PUID' entry box, and pressing the enter key, or the "go" button. 

The file format name, and version is populated at the top of the pane when a PUID is resolved.

### Qty

This is how many files you have recorded as being in your collection via the `formats_breakdown.csv` file.

### Collection Count

This is how many collections/sources/depositors you have recorded as being sources of this file format via the `rosetta_collections_per_format.csv` file

The middle section lists the various informational units recorded for the file format. There are some right-click mouse options (resolve / copy) for some of the informational units. Copy adds the information to the clipboard, resolve opens a browser window and directs the browser to the corresponding webpage. 

E.g. for PUID fmt/4, we can get to 

https://www.nationalarchives.gov.uk/pronom/fmt/4
https://www.wikidata.org/wiki/Q27526739
https://www.loc.gov/preservation/digital/formats/fdd/fdd000133.shtml
https://github.com/usnationalarchives/digital-preservation (NARA doesn't currently have endpoints for its format identifiers, so the user is directed to the source page for the NARA risk assessments. 

In the bottom section, there are two buttons. 

### Go To Node for Access Docs

Pressing this button opens a file explorer window at the information node for this PUID. E.g. `c:\tools\format_library_helper\format_library_nodes\fmt_3`

### Go To TestSet

Pressing this button opens a file explorer window at the TestSet node for this PUID. E.g.`E:\testSet\fmt_3`

## Pane #3 - Documentation

This pane is intended to be manually addressed to record your local / organisational resources for a given file format. 

### Have formal specification

This checkbox is intended to record if you have a copy of a format spec in the local node (e.g. in `c:\tools\format_library_helper\format_library_nodes\fmt_3\specifications`) 

### Have used formal specification

This checkbox is intended to record if you have used a copy of a format spec to work on file format. Usage of a specification helps to inform on the quality of documentation, and to record previous work. 

### Know formal specification

This checkbox is intended to record if you have a know of a format specification but do not have a local copy. This is especially important information for specifications that you have identified but been unable to procure. 

### Notes

This is a freetext box that is used to capture any notes on documentation (e.g. names/sources of specifications that you do not have access to, or local notes around the usage/experience of a specification). 

### Have informal technical notes

This checkbox is intended to record if you have a copy of any informal notes. Not really used - likely to change in the future. 

### Have used informal technical notes

This checkbox is intended to record if you have used the copy of any informal notes. Not really used - likely to change in the future. 

### Notes

This is a freetext box that is used to capture any notes on informal notes. Not really used - likely to change in the future.  

### Have other org notes

This checkbox is intended to record if you have a copy of any other organisations notes. Not really used - likely to change in the future. 

### Have other org notes

This checkbox is intended to record if you have used the copy of any other organisations notes. Not really used - likely to change in the future. 

### Notes

This is a freetext box that is used to capture any notes on other orgs notes. Not really used - likely to change in the future.  

### Update Local Data

This button is used to record/update the data from the UI and store it in the JSON file in the node. E.g. `c:\tools\format_library_helper\format_library_nodes\fmt_3\local_data\fmt_3.json`

All check boxes and freetext boxes are recorded. 


## Pane #4 - Render

This pane is intended to capture useful data around renders used with any file format. 

### Render in Rosetta?

This tool is built to support our Rosetta format library, this is not linked to Rosetta - this checkbox is set manually if we have a renderer in Rosetta for this format. The label can be changed to your DPS on line #775

### Access in Rosetta via DC?

In Rosetta we have delivery concept of derivative copies for some formats (e.g. high resolution uncompressed TIFFs might have a smaller JPEG that’s provided to a requester). It is useful data to know if access if provided via the master object, or a derivative. 

### DC PUID

This is intended to record what format the derivative copy is delivered as. 

### Renderer

This is intended to record what renderer tool/plugin is used to deliver the file format (not DC). 

### Render on standard machine?

This is intended to record if a user might expect to accurately consume a file on a "standard" build machine, via common software (e.g. MS office etc). 

The textbox below is intended to record what that software is. 

### Render on specialist machine?

This is intended to record if a user might expect to accurately consume a file on a "specialist" build machine, via uncommon software or requiring enhanced permissions etc.  

The textbox below is intended to record what that software is. 

### Notes

This textbox is intended to record any notes about render. 

### Initial Risk Assessment

This is a small textbox intended to record a local sense of risk for this file format. We are using Low/Med/High and have set this value for each format based on our local understanding and context. This data is then used to give whole collection analysis / understanding via the node JSON files.  

We expect to enhance and augment this section in future versions. 

### Collections

This textbox is a list of all the collections/depositors/sources we have recorded for this file format.
