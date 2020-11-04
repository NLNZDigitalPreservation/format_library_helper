import os
import pickle
from bs4 import BeautifulSoup as bs
import PySimpleGUI as ui
import pyperclip
import csv
import json
import subprocess
import webbrowser


pronom_lookup_pickle = "pickles\pronom_lookup.pickle"
loc_lookup_pickle = "pickles\loc_lookup_pickle.pickle"
format_library_nodes = "format_library_nodes"
test_set_location = r"E:\testSet"

########### get resources #########

def get_pronom_lookup():
    folder = r"sources\pronom"
    puids = {}
    my_exts = {}
    for f in os.listdir(folder):
        puid = f.replace("fmt", "fmt_").replace(".xml", "")
        my_f = os.path.join(folder, f)
        with open(my_f, encoding="utf8") as data:
            format_family = ""
            format_type = ""
            mime = ""
            exts = []
            my_xml = bs(data.read(), 'lxml')
            parts = my_xml.findAll("fileformatidentifier")
            for part in parts:
                if part.find("identifiertype") and part.find("identifiertype").string == "MIME":
                    mime = part.find('identifier').string.strip()

            format_family = my_xml.find("formatfamilies").string.strip()
            format_type = my_xml.find("formattypes").string.strip()
            format_name = my_xml.find("formatname").string.strip()
            format_version = my_xml.find("formatversion").string.strip() 

            parts = my_xml.findAll("externalsignature")
            for p in parts:
                if p.find("signaturetype") and p.find("signaturetype").string == "File extension":
                    exts.append(p.find("signature").string.strip())

            for ext in exts:
                if ext not in my_exts:
                    my_exts[ext] = []

                if puid not in my_exts[ext]:
                    my_exts[ext].append(puid)

        puids[puid] = {"mime":mime, "type":format_type, "format_families":format_family, "exts":exts, "format_name":format_name, "format_version":format_version}

    pickle.dump( (puids, my_exts), open( pronom_lookup_pickle, "wb" )) 
    return puids, my_exts

def get_rosetta_clasifications():
    puids = {}
    with open (r"sources\rosetta_type_classifications.csv") as data:
        rows = csv.reader(data)
        for r in rows:
            classification = r[0]
            puid = r[1]

            if puid == "ExL-Fmt-21":
                puid = "fmt/397"
            if puid == "ExL-Fmt-22":
                puid = "fmt/869"
            if puid == "ExL-Fmt-23":
                puid = "fmt/398"
            if puid == "ExL-Fmt-41":
                puid = "fmt/483"
            if puid == "ExL-Fmt-61":
                puid = "fmt/199"
            if puid == "ExL-Fmt-62":
                puid = "fmt/189"
            if puid == "ExL-Fmt-161":
                puid = "fmt/573"
            if puid == "ExL-Fmt-241":
                puid = "fmt/851"
            if puid == "ExL-Fmt-261":
                puid = "fmt/937"
            if puid == "ExL-Fmt-321":
                puid = "fmt/866"
            if puid == "ExL-Fmt-24417":
                puid = "fmt/279"

            puid = puid.replace("/", "_")
            if puid not in puids:
                puids[puid]=classification
            else:
                print(puid)
    return puids

def get_rosetta_collections_count():
    ### todo get from local data file
    lookup={}
    f = os.path.join("sources", "rosetta_collections_per_format.csv")
    with open(f, encoding='utf-8') as data:
        rows = csv.reader(data)
        for puid, count in rows:
            lookup[puid]=int(count)
    return lookup

def get_nara_id_lookup():
    nara_ids = {}
    with open(r"sources\NARA_preservation_matrix_sept_2020.csv",  encoding='utf-8') as data:
        rows = csv.reader(data)
        for r in rows:
            nara_id = r[3]
            puid = r[6].replace("https://www.nationalarchives.gov.uk/PRONOM/", "").replace("https://www.nationalarchives.gov.uk/pronom/", "").replace("http://www.nationalarchives.gov.uk/PRONOM/", "")
            puid = puid.replace("/", "_")
            nara_ids[puid] = nara_id
    return nara_ids

def get_loc_lookup():
    folder = r"sources\fddXML"
    puids_lookup = {}
    wiki_id_lookup = {}
    for f in [os.path.join(folder, x) for x in os.listdir(folder) if x.endswith(".xml")]:
        wiki_ids = []
        puids = []
        with open(f, encoding='utf8') as data:
            loc = bs(data.read(), "lxml")
            loc_id = f.replace(folder, "").replace(".xml", "")[1:]
            blocks = loc.findAll("fdd:other")
            for block in blocks:
                if block.find("fdd:tag").string == "Pronom PUID":
                    puids = [x.string for x in block.findAll("fdd:sigvalue")]
                    puids = [x for x in puids if x != "See notes" or x != "See note"]
                    puids = [x.replace("(Lotus Notes Database Version 2)", "") for x in puids]
                    puids = [x.replace("(Lotus Notes Database Version 3)", "") for x in puids]
                    puids = [x.replace("(Lotus Notes Database Version 4)", "") for x in puids]
                    puids = [x.replace("/", "_") for x in puids]
                    puids = [x.strip() for x in puids]

                    for puid in puids:
                        if puid not in puids_lookup:
                            puids_lookup[puid] = []
                        if loc_id not in puids_lookup[puid]:
                            puids_lookup[puid].append(loc_id)

                if block.find("fdd:tag").string == "Wikidata Title ID":
                    wiki_ids = [x.string for x in block.findAll("fdd:sigvalue")]
                    wiki_ids = [x.replace("(Lotus Notes Database file format, version 2)", "") for x in wiki_ids]
                    wiki_ids = [x.replace("(Lotus Notes Database file format, version 3)", "") for x in wiki_ids]
                    wiki_ids = [x.replace("(Lotus Notes Database file format, version 4)", "") for x in wiki_ids]
                    wiki_ids = [x.strip() for x in wiki_ids]
                    for wiki_id in wiki_ids:
                        if loc_id not in wiki_id_lookup:
                            wiki_id_lookup[loc_id] = []
                        if wiki_id not in wiki_id_lookup[loc_id]:
                            wiki_id_lookup[loc_id].append(wiki_id)
    pickle.dump( puids_lookup, open( loc_lookup_pickle, "wb" )) 
    return puids_lookup

def get_wiki_data_ids():
    with open ("sources/wiki_data_dump_Sept_2020.csv", encoding = "utf8") as data:
        puids = {}
        reader = csv.reader(data)
        for r in reader:
            wiki_id, name, puid = r
            puid = puid.replace("/", "_")
            if puid != "":
                if puid not in puids:
                    puids[puid] = []
                puids[puid].append(wiki_id)
    return puids

def get_rosetta_counts():
    puids = {}
    with open("sources/formats_breakdown.csv") as data:
        rows = [x for x in data.read().split("\n") if x != ""]
        for r in rows[1:]:
            puid, count = r.split(",")
            if puid == "ExL-Fmt-21":
                puid = "fmt/397"
            if puid == "ExL-Fmt-22":
                puid = "fmt/869"
            if puid == "ExL-Fmt-23":
                puid = "fmt/398"
            if puid == "ExL-Fmt-41":
                puid = "fmt/483"
            if puid == "ExL-Fmt-61":
                puid = "fmt/199"
            if puid == "ExL-Fmt-62":
                puid = "fmt/189"
            if puid == "ExL-Fmt-161":
                puid = "fmt/573"
            if puid == "ExL-Fmt-241":
                puid = "fmt/851"
            if puid == "ExL-Fmt-261":
                puid = "fmt/937"
            if puid == "ExL-Fmt-321":
                puid = "fmt/866"
            if puid == "ExL-Fmt-24417":
                puid = "fmt/279"
            puid = puid.replace("/","_")
            if puid not in puids:
                puids[puid] = 0
            puids[puid] += int(count)
    return puids


###################################

if os.path.exists(pronom_lookup_pickle):
    pronom_lookup, pronom_exts = pickle.load( open( pronom_lookup_pickle, "rb" )) 
else:
    pronom_lookup, pronom_exts = get_pronom_lookup()


if os.path.exists(loc_lookup_pickle):
    loc_lookup =  pickle.load( open( loc_lookup_pickle, "rb" ))
else:
    loc_lookup = get_loc_lookup()

rosetta_class_lookup = get_rosetta_clasifications()
rosetta_counts_lookup = get_rosetta_counts()
rosetta_collection_counts_lookup =  get_rosetta_collections_count()
nara_lookup = get_nara_id_lookup()
wiki_lookup = get_wiki_data_ids()

######### Data management tools ################

def flush_all():
    for node in os.listdir(format_library_nodes):
        local_file = os.path.join(format_library_nodes, node, "local_data", f"{node}.json")
        try:
            os.remove(local_file)
            print ("Flushing:", local_file)
        except FileNotFoundError:
            pass 
# flush_all()
# quit()


def put_data_into_local_if_field_empty(node):

    puid = node.replace("_", "/")
    local_file = os.path.join(format_library_nodes, node, "local_data", f"{node}.json")
    if os.path.exists(local_file):
        with open(local_file) as json_file:
            local_data = json.load(json_file)

            ### PRONOM #######

            if not local_data["pronom_data"][0]["pronom_name"]:
                try:
                    local_data["pronom_data"][0]["pronom_name"] = pronom_lookup[node]['format_name']
                except KeyError:
                  local_data["pronom_data"][0]["pronom_name"] = "N/A"  

            if not local_data["pronom_data"][0]["pronom_version"]:
                try:
                    local_data["pronom_data"][0]["pronom_version"] = pronom_lookup[node]['format_version']
                except KeyError:
                    local_data["pronom_data"][0]["pronom_version"] = "N/A"

            if not local_data["pronom_data"][0]["pronom_exts"]:
                local_data["pronom_data"][0]["pronom_exts"] = ", ".join(pronom_lookup[node]['exts'])

            if not local_data["pronom_data"][0]["pronom_puid"]:
                local_data["pronom_data"][0]["pronom_puid"] = puid

            if not local_data["pronom_data"][0]["pronom_types"]:
                try:
                    local_data["pronom_data"][0]["pronom_types"] = pronom_lookup[node]['type']
                except KeyError:
                    local_data["pronom_data"][0]["pronom_types"] = "N/A"

            if not local_data["pronom_data"][0]["pronom_mime"]:
                try:
                    local_data["pronom_data"][0]["pronom_mime"] = pronom_lookup[node]['mime']
                except KeyError:
                    local_data["pronom_data"][0]["pronom_mime"] = "N/A"

            if not local_data["pronom_data"][0]["pronom_families"]:
                try:
                    local_data["pronom_data"][0]["pronom_families"] = pronom_lookup[node]['format_families']
                except KeyError:
                    local_data["pronom_data"][0]["pronom_families"] = "N/A"

            ######## Rosetta Data ############
            try:
                local_data["rosetta_data"][0]["rosetta_format_family"] = rosetta_class_lookup[node]
            except KeyError:
                local_data["rosetta_data"][0]["rosetta_format_family"] = None

            try:
                local_data["rosetta_data"][0]["collection_count"] = rosetta_collection_counts_lookup[puid]
            except KeyError:
                local_data["rosetta_data"][0]["collection_count"] = None
            try:

                local_data["rosetta_data"][0]["files_count"] = rosetta_counts_lookup[node]
            except KeyError:
                local_data["rosetta_data"][0]["files_count"] = None


            ####### other identifiers ##########
            try:
                local_data["other_registry_identifers"][0]["loc_ids"] = loc_lookup[node]
            except KeyError:
                 local_data["other_registry_identifers"][0]["loc_ids"] = None

            try:
                local_data["other_registry_identifers"][0]["nara_ids"] = nara_lookup[node]
            except KeyError:
                local_data["other_registry_identifers"][0]["nara_ids"] = None

            try:
                local_data["other_registry_identifers"][0]["wikidata_IDs"] = wiki_lookup[node]
            except KeyError:
                 local_data["other_registry_identifers"][0]["wikidata_IDs"] = None

            ### to do
            # local_data["other_registry_identifers"][0]["freedesktop_mime"] = 

            # for k, v in local_data.items():
            #     print (k, v)

        # with open(local_file, 'w') as outfile:
        #     json.dump(local_data, outfile)
    return 

#################################################

#########  UI ########################

def update_for_pronom(puid, form):
    form["__puid__"].update(puid.replace("_", "/"))
    form["__pronom_name__"].update(pronom_lookup[puid]['format_name'])

    form["__pronom_version__"].update(pronom_lookup[puid]['format_version'])
    
    p_mime  = pronom_lookup[puid]['mime']
    if p_mime:
        form["__pronom_mime__"].update(pronom_lookup[puid]['mime'])
    else:
        form["__pronom_mime__"].update("None")
    
    p_family = pronom_lookup[puid]['format_families']
    if p_family:
        form["__pronom_family__"].update(p_family)
    else:
        form["__pronom_family__"].update("None")

    p_type = pronom_lookup[puid]['type']
    if p_type:
        form["__pronom_type__"].update(p_type)
    else:
        form["__pronom_type__"].update("None")

    p_exts = pronom_lookup[puid]['exts']
    if p_exts:
        form["__pronom_exts__"].update(", ".join(p_exts))
    else:
        form["__pronom_exts__"].update("None")

def update_for_rosetta(puid, form):
    puid = puid.replace("/", "_")
    if puid in rosetta_class_lookup:
        form["__rosetta_family__"].update(f"{rosetta_class_lookup[puid]}")
    else:
        form["__rosetta_family__"].update("None")

def update_for_nara(puid, form):
    puid = puid.replace("/", "_")
    if puid in nara_lookup:
        form["__nara_id__"].update(nara_lookup[puid])
    else:
        form["__nara_id__"].update("None")

def update_for_loc(puid, form):
    if puid in loc_lookup:
        form["__loc_id__"].update(", ".join(loc_lookup[puid]))
    else:
        form["__loc_id__"].update("None")

def update_for_wiki_data(puid, form):
    puid = puid.replace("/", "_")
    if puid in wiki_lookup:
        form["__wiki_id__"].update(", ".join(wiki_lookup[puid]))
    else:
        form["__wiki_id__"].update("None")

def update_for_collection_count(puid, form):
    puid = puid.replace("_", "/")
    if puid in rosetta_collection_counts_lookup:
        form["__collection_count__"].update(rosetta_collection_counts_lookup[puid])
    else:
        form["__collection_count__"].update("None")

def update_for_files_count(puid, form):
    if puid in rosetta_counts_lookup:
        form["__qty__"].update(f"{rosetta_counts_lookup[puid]:,}")

def update_for_local_data(puid, form, flush=False):
    local_file = os.path.join(format_library_nodes, puid, "local_data", f"{puid}.json")

    if flush:
        try:
            os.remove(local_file)
            print ("Flushing:", local_file)
        except FileNotFoundError:
            pass 

    if not os.path.exists(os.path.join(format_library_nodes, puid)):
        os.makedirs(os.path.join(format_library_nodes, puid, "specifications"))
        os.makedirs(os.path.join(format_library_nodes, puid, "local_data"))
        os.makedirs(os.path.join(format_library_nodes, puid, "web-pages"))
        os.makedirs(os.path.join(format_library_nodes, puid, "other_resources"))
        os.makedirs(os.path.join(format_library_nodes, puid, "cluster_networks"))
    
    if not os.path.exists(local_file):
        make_local_file(local_file)

    with open(local_file) as json_file:
        local_data = json.load(json_file)

    form["have_spec"].update(local_data["documentation"][0]["has_formal_spec"])
    form["used_spec"].update(local_data["documentation"][0]["used_formal_spec"])
    form["know_spec"].update(local_data["documentation"][0]["know_name_of_formal_spec"])
    form["used_spec"].update(local_data["documentation"][0]["used_formal_spec"])
    form["__spec_notes__"].update(local_data["documentation"][0]["format_spec_notes"])
    form["have_informal"].update(local_data["documentation"][0]["has_informal_notes"])
    form["used_informal"].update(local_data["documentation"][0]["used_informal_notes"])
    form["__informal_notes__"].update(local_data["documentation"][0]["informal_spec_notes"])
    form["have_orgs"].update(local_data["documentation"][0]["has_other_org_notes"])
    form["used_orgs"].update(local_data["documentation"][0]["used_other_org_notes"])
    form["__orgs_notes__"].update(local_data["documentation"][0]["other_org_notes_notes"])

    form["render_rosetta"].update(local_data["render_assessments"][0]["has_rosetta_viewer"])
    form["rosetta_viewer"].update(local_data["render_assessments"][0]["rosetta_viewer"])
    form["access_via_dc"].update(local_data["render_assessments"][0]["access_in_rosetta_via_designation_copy"])
    form["dc_puid"].update(local_data["render_assessments"][0]["designation_copy_format_puid"])
    form["dc_viewer"].update(local_data["render_assessments"][0]["designation_copy_renderer"])
    form["render_normal"].update(local_data["render_assessments"][0]["rendered_on_basic_machine"])
    form["normal_application"].update(local_data["render_assessments"][0]["basic_machine_renderer"])
    form["render_special"].update(local_data["render_assessments"][0]["rendered_on_specicalist_machine"])
    form["special_application"].update(local_data["render_assessments"][0]["specialist_machine_renderer"])
    form["__render_notes__"].update(local_data["render_assessments"][0]["render_notes"])

    form["__list_of_collections__"].update("\n".join(local_data["rosetta_data"][0]["collections"]))

    try:
        form["init_risk_judgement"].update(local_data["risk_assessments"][0]["initial_judgement"])
    except KeyError:
        form["init_risk_judgement"].update("Low")

def make_local_file(f):
    local_data = {"rosetta_data": [{"rosetta_format_family":None,
                                    "collection_count":None,
                                    "collections":None,
                                    "files_count":None}],

                "pronom_data":[{"pronom_exts":None,  
                                "pronom_puid":None,
                                "pronom_name":None,
                                "pronom_version":None,
                                "pronom_types":None,  
                                "pronom_mime":None,
                                "pronom_families":None}],

                "other_registry_identifers":[{  "loc_ids":None,
                                                "nara_ids":None,
                                                "wikidata_IDs":None,
                                                "freedesktop_mime":None
                                            }],

                "policy_docs":  [{  "has_preservation_plan":False,
                                    "preservation_plan":None,
                                    "has_initial_assessement":False,
                                    "initial_assessement":None,
                                    "has_risk_assessement":False,
                                    "risk_assessement":None
                                }],
                
                "documentation":[{  "has_formal_spec":False,
                                    "used_formal_spec":False,
                                    "know_name_of_formal_spec":False,
                                    "format_spec_notes":"",
                                    "has_informal_notes":False,
                                    "used_informal_notes":False,
                                    "informal_spec_notes":"",
                                    "has_other_org_notes":False,
                                    "used_other_org_notes":False,
                                    "other_org_notes_notes":""
                                }],

                "render_assessments":   [{  "has_rosetta_viewer":False,
                                            "rosetta_viewer":"",
                                            "access_in_rosetta_via_designation_copy":False,
                                            "designation_copy_format_puid":"",
                                            "designation_copy_renderer":"",
                                            "rendered_on_basic_machine":False,
                                            "basic_machine_renderer":"",
                                            "rendered_on_specicalist_machine":False,
                                            "specialist_machine_renderer":"",
                                            "render_notes":""
                                        }],

                "risk_assessments": [{  "initial_judgement":""}]
                }

    with open(f, 'w') as outfile:
        json.dump(local_data, outfile) 

def update_local_data(puid):
    local_file = os.path.join(format_library_nodes, puid, "local_data", f"{puid}.json")
    if os.path.exists(local_file):
        with open(local_file) as json_file:
            local_data = json.load(json_file)

        if form["have_spec"].get() == 1:
            local_data["documentation"][0]["has_formal_spec"] = True
        elif form["have_spec"].get() == 0:
            local_data["documentation"][0]["has_formal_spec"] = False

        if form["used_spec"].get() == 1:
            local_data["documentation"][0]["used_formal_spec"] = True
        elif form["used_spec"].get() == 0:
            local_data["documentation"][0]["used_formal_spec"] = False

        if form["know_spec"].get() == 1:
            local_data["documentation"][0]["know_name_of_formal_spec"] = True
        elif form["know_spec"].get() == 0:
            local_data["documentation"][0]["know_name_of_formal_spec"] = False

        local_data["documentation"][0]["format_spec_notes"] = form["__spec_notes__"].get()

        if form["have_informal"].get() == 1:
            local_data["documentation"][0]["has_informal_notes"] = True
        elif form["have_informal"].get() == 0:
            local_data["documentation"][0]["has_informal_notes"] = False

        if form["used_informal"].get() == 1:
            local_data["documentation"][0]["used_informal_notes"] = True
        elif form["used_informal"].get() == 0:
            local_data["documentation"][0]["used_informal_notes"] = False

        local_data["documentation"][0]["informal_spec_notes"] = form["__informal_notes__"].get()

        if form["have_orgs"].get() == 1:
            local_data["documentation"][0]["has_other_org_notes"] = True
        elif form["have_orgs"].get() == 0:
            local_data["documentation"][0]["has_other_org_notes"] = False

        if form["used_orgs"].get() == 1:
            local_data["documentation"][0]["used_other_org_notes"] = True
        elif form["used_orgs"].get() == 0:
            local_data["documentation"][0]["used_other_org_notes"] = False

        local_data["documentation"][0]["other_org_notes_notes"] = form["__orgs_notes__"].get()

        if form["render_rosetta"].get() == 1:
            local_data["render_assessments"][0]["has_rosetta_viewer"] = True
        elif form["render_rosetta"].get() == 0:
            local_data["render_assessments"][0]["has_rosetta_viewer"] = False

        local_data["render_assessments"][0]["rosetta_viewer"] = form["rosetta_viewer"].get()

        if form["access_via_dc"].get() == 1:
            local_data["render_assessments"][0]["access_in_rosetta_via_designation_copy"] = True
        elif form["access_via_dc"].get() == 0:
            local_data["render_assessments"][0]["access_in_rosetta_via_designation_copy"] = False

        local_data["render_assessments"][0]["designation_copy_format_puid"] = form["dc_puid"].get()

        local_data["render_assessments"][0]["designation_copy_renderer"] = form["dc_viewer"].get()

        if form["render_normal"].get() == 1:
            local_data["render_assessments"][0]["rendered_on_basic_machine"] = True
        elif form["render_normal"].get() == 0:
            local_data["render_assessments"][0]["rendered_on_basic_machine"] = False
                                        
        local_data["render_assessments"][0]["basic_machine_renderer"] = form["normal_application"].get()

        if form["render_special"].get() == 1:
            local_data["render_assessments"][0]["rendered_on_specicalist_machine"] = True
        elif form["render_special"].get() == 0:
            local_data["render_assessments"][0]["rendered_on_specicalist_machine"] = False

        local_data["render_assessments"][0]["specialist_machine_renderer"] = form["special_application"].get()

        local_data["render_assessments"][0]["render_notes"] = form["___render_notes__"].get()

        try:
            local_data["risk_assessments"][0]["initial_judgement"] = form["init_risk_judgement"].get()
        except KeyError:
           local_data["risk_assessments"] = [{"initial_judgement":""}]
           local_data["risk_assessments"][0]["initial_judgement"] = form["init_risk_judgement"].get()



        with open(local_file, 'w') as outfile:
            json.dump(local_data, outfile) 

def clear(form, puid):
    form["__puid__"].update("")
    form["__pronom_name__"].update("")
    form["__pronom_version__"].update("")
    form["__pronom_mime__"].update("")
    form["__pronom_family__"].update("")
    form["__pronom_type__"].update("")
    form["__pronom_exts__"].update("")
    form["__wiki_id__"].update("")
    form["__loc_id__"].update("")
    form["__nara_id__"].update("")
    form["__rosetta_family__"].update("")
    form["__qty__"].update("N/A")
    form["__collection_count__"].update("")

def clear_local(form, puid):
   
    form["__qty__"].update("N/A")
    form["have_spec"].update(False)
    form["used_spec"].update(False)
    form["know_spec"].update(False)
    form["__spec_notes__"].update("")
    form["have_informal"].update(False)
    form["used_informal"].update(False)
    form["__informal_notes__"].update("")
    form["have_orgs"].update(False)
    form["used_orgs"].update(False)
    form["__orgs_notes__"].update("")
    form["render_rosetta"].update(False)
    form["rosetta_viewer"].update("")
    form["access_via_dc"].update(False)
    form["dc_puid"].update("")
    form["dc_viewer"].update("")
    form["render_normal"].update(False)
    form["normal_application"].update("")
    form["render_special"].update(False)
    form["special_application"].update("")
    form["_render_notes__"].update("")
    form["init_risk_judgement"].update("")
    form["__list_of_collections__"].update("")

def do_clipboard(event):
    event = "__"+event.replace("copy ", "").replace(" ", "_")+"__"
    text = form[event].get()
    pyperclip.copy(text)

def do_resolve(event):
    ### to do, only handles first identifier if list 
    event = "__"+event.replace("resolve ", "").replace(" ", "_")+"__"
    key = form[event].get()

    if "," in key:
        keys = key.split(",")
        key = keys[0]

    if "wiki" in event:
        url = f"https://www.wikidata.org/wiki/{key}"
    elif "nara" in event: 
        url = f"https://github.com/usnationalarchives/digital-preservation"
    elif "loc" in event:
        url = f"https://www.loc.gov/preservation/digital/formats/fdd/{key}.shtml"
    elif "puid" in event:
        url = f"https://www.nationalarchives.gov.uk/pronom/{key}"

    webbrowser.open_new(url)

def do_spawn_explorer_node(puid):
    node_path = f'"{os.path.join(os.getcwd(), format_library_nodes, puid)}"'
    subprocess.Popen(f'explorer {node_path}')  

def do_spawn_explorer_test_set(puid):
    test_set_path = f'"{os.path.join(test_set_location, puid)}"'
    if os.path.exists(test_set_path.replace('"', "")):
        subprocess.Popen(f'explorer {test_set_path}') 
    else:
        subprocess.Popen(f'explorer {test_set_location}') 


def make_basic_frame():
    identifier_puid = [ui.Text("PUID: ", text_color="grey70", right_click_menu=(['&Right',["!&edit puid", "copy puid", "resolve puid"]])), ui.Text("", size=(20, 0), k="__puid__", right_click_menu=(['&Right',["!&edit puid", "copy PUID", "resolve puid"]]))]
    identifier_pronom_name = [ui.Text("", size=(25, 2), font='Ariel 14', k="__pronom_name__", right_click_menu=(['&Right',["!&edit pronom name", "copy pronom name"]]))]
    identifier_pronom_version = [ui.Text("Version:", text_color="grey70"), ui.Text("", size=(20, 1), font='Ariel 12', k="__pronom_version__")]
    identifier_pronom_exts = [ui.Text("PRONOM Exts: ", text_color="grey70", right_click_menu=(['&Right',["!&edit pronom exts", "copy pronom exts"]])),  ui.Text("", size=(20, 0), k="__pronom_exts__", right_click_menu=(['&Right',["!&edit pronom exts", "copy pronom exts"]]))]
    identifier_pronom_mime = [ui.Text("PRONOM MIME: ", text_color="grey70", right_click_menu=(['&Right',["!&edit pronom MIME", "copy pronom MIME"]])),  ui.Text("", size=(20, 0), k="__pronom_mime__", right_click_menu=(['&Right',["!&edit pronom mime", "copy pronom mime"]]))]
    identifier_pronom_type = [ui.Text("PRONOM Type: ", text_color="grey70", right_click_menu=(['&Right',["!&edit pronom type", "copy pronom type"]])),  ui.Text("", size=(20, 0), k="__pronom_type__", right_click_menu=(['&Right',["!&edit pronom type", "copy pronom type"]]))]
    identifier_pronom_family = [ui.Text("PRONOM Family: ", text_color="grey70", right_click_menu=(['&Right',["!&edit pronom family", "copy pronom family"]])),  ui.Text("", size=(20, 0), k="__pronom_family__", right_click_menu=(['&Right',["!&edit pronom family", "copy pronom family"]]))]
    
    identifier_rosetta_family =  [ui.Text("Rosetta Family: ", text_color="grey70", right_click_menu=(['&Right',["!&edit Rosetta family", "copy Rosetta family"]])), ui.Text("", size=(20, 0), k="__rosetta_family__", right_click_menu=(['&Right',["!&edit rosetta family", "copy rosetta family"]]))]
    
    identifier_wiki = [ui.Text("WIKIDATA: ", text_color="grey70", right_click_menu=(['&Right',["!&edit wiki", "copy wiki",]])), ui.Text("", size=(20, 0), k="__wiki_id__", right_click_menu=(['&Right',["!&edit wiki id", "copy wiki id", "resolve wiki id"]]))]
    
    identifier_loc = [ui.Text("LOC: ", text_color="grey70", right_click_menu=(['&Right',["!&edit loc", "copy loc",]])), ui.Text("", size=(20, 0), k="__loc_id__", right_click_menu=(['&Right',["!&edit loc id", "copy loc id", "resolve loc id"]]))]

    identifier_nara = [ui.Text("NARA: ", text_color="grey70", right_click_menu=(['&Right',["!&edit loc", "copy loc",]])), ui.Text("", size=(20, 0), k="__nara_id__", right_click_menu=(['&Right',["!&edit nara id", "copy nara id", "resolve nara id"]]))]
    
    identifier_shared_mime = [ui.Text("Shared MIME: ", text_color="grey70", right_click_menu=(['&Right',["!&edit shared mime", "copy shared mime",]]))]

    row_pronom_lookup = [
                            [ui.Text("PRONOM Helper \n\nSearchPuid")],
                            [ui.In(size=(25, 1), enable_events=True, key="--puid--")],
                            [ui.Text("Search extension")],
                            [ui.In(size=(25, 1), enable_events=True, key="--ext--")],
                            [ui.Multiline("", size=(25, 10), key="-TOUT-")],
                            [ui.B('Clipboard',  button_color=('yellow', 'purple'))],
                        ]

    row_a = [
                identifier_pronom_name,
                identifier_pronom_version,
                [ui.Text("Search PUID:", size=(22, 1)), ui.Text("Qty", text_color="grey70")],
                [ui.In(size=(20, 1), key="--puidsearch--", enable_events=True, focus=True), ui.B("Go", k="--go--", bind_return_key=True), ui.Text("N/A", k="__qty__", size=(9,1))],
                [ui.Text("Collection Count:", text_color="grey70", justification="right"), ui.Text("", k="__collection_count__", size=(5,1))],
                [ui.HorizontalSeparator(pad=(0,5))],
                identifier_puid,
                identifier_pronom_mime,
                identifier_pronom_exts,
                identifier_pronom_family,
                identifier_pronom_type, 
                identifier_rosetta_family,
                identifier_wiki,
                identifier_loc,
                identifier_nara,
                identifier_shared_mime,
                [ui.HorizontalSeparator(pad=(0,5))],
                [ui.B("Go To Node for Access Docs", k="--spawn_explorer_node--")],
                [ui.B("Go To TestSet", k="--spawn_explorer_testSet--")],
            ]
            
    row_b = [   
                [ui.Text("Documentation", font=13)],
                [ui.Checkbox("Have formal specification", default=False, k="have_spec")],
                [ui.Checkbox("Have used formal specification", default=False,  k="used_spec", enable_events=True)],
                [ui.Checkbox("Know formal specification", default=False,  k="know_spec", enable_events=True)],
                [ui.Text("Notes")],
                [ui.Multiline(size=(50, 4), k="__spec_notes__", right_click_menu=(['&Right',["copy spec notes"]]))],
                [ui.Checkbox("Have informal technical notes", default=False, k="have_informal", enable_events=True)],
                [ui.Checkbox("Have used informal technical notes", default=False,  k="used_informal", enable_events=True)],
                [ui.Text("Notes")],
                [ui.Multiline(size=(50, 4), k="__informal_notes__", right_click_menu=(['&Right',["copy informal notes"]]))],
                [ui.Checkbox("Have other org notes", default=False, k="have_orgs", enable_events=True)],
                [ui.Checkbox("Have used other org  notes", default=False,  k="used_orgs", enable_events=True)],
                [ui.Text("Notes")],
                [ui.Multiline(size=(50, 4), k="__orgs_notes__", right_click_menu=(['&Right',["copy orgs notes"]]))],
                [ui.B("Update Local Data", k="--update--")]
            ]

    row_c = [   
                [ui.Text("Render", font=13)],
                [ui.Checkbox("Render in Rosetta? ", default=False, k="render_rosetta")], 
                [ui.In("", k="rosetta_viewer", size=(35, 1))],
                [ui.Checkbox("Access in Rosetta via DC?", default=False, k="access_via_dc")],
                [ui.Text("DC PUID"), ui.In("", k="dc_puid", size=(25, 1))],
                [ui.Text("Renderer"), ui.In("", k="dc_viewer", size=(25, 1))],
                [ui.Checkbox("Render on standard machine?", default=False,  k="render_normal")], 
                [ui.In("", k="normal_application", size=(35, 1))],
                [ui.Checkbox("Render on specialist machine?", default=False,  k="render_special")], 
                [ui.In("", k="special_application", size=(35, 1))],
                [ui.Text("Notes", font=5)],
                [ui.Multiline(size=(35, 3), k="__render_notes__", right_click_menu=(['&Right', ["copy render notes"]]))],
                [ui.Text("Initial Risk Assessment")],
                [ui.In("", k="init_risk_judgement", size=(5, 1))],
                [ui.HorizontalSeparator(pad=(5,5))],
                [ui.Text("Collections", font=5)],
                [ui.Multiline(size=(35, 5), k="__list_of_collections__", right_click_menu=(['&Right', ["copy list of collections"]]))],
            ]

    layout = [
                [
                    ui.Column(row_pronom_lookup),
                    ui.VSeperator(),
                    ui.Column(row_a),
                    ui.VSeperator(),
                    ui.Column(row_b),
                    ui.VSeperator(),
                    ui.Column(row_c),
                ]
    ]


    form = ui.FlexForm(layout, no_titlebar=True, keep_on_top=True, grab_anywhere=True, return_keyboard_events=True)
    form.Layout(layout) 
    ui.ChangeLookAndFeel('dark')
    ui.SetOptions(element_padding=(0, 0))  
    return form

form = make_basic_frame() 

#####################################

while True:
    event, values = form.read()
    values["--puidsearch--"] = values["--puidsearch--"].replace("/", "_")
    if event == "Exit" or event == ui.WIN_CLOSED or event == "Escape:27":
        break
    if event == "--go--":
        if  values["--puidsearch--"] and values["--puidsearch--"] in pronom_lookup:
            update_for_pronom(values["--puidsearch--"], form)
            update_for_rosetta(values["--puidsearch--"], form)
            update_for_loc(values["--puidsearch--"], form)
            update_for_nara(values["--puidsearch--"], form)
            update_for_wiki_data(values["--puidsearch--"], form)
            update_for_files_count(values["--puidsearch--"], form)
            update_for_collection_count(values["--puidsearch--"], form)
            put_data_into_local_if_field_empty(values["--puidsearch--"])

        if values["--puidsearch--"] and values["--puidsearch--"] in rosetta_counts_lookup:
            update_for_local_data(values["--puidsearch--"], form)

        if values["--puidsearch--"] and not values["--puidsearch--"] in pronom_lookup:
            clear(form, values["--puidsearch--"])

        if values["--puidsearch--"] not in rosetta_counts_lookup:
            clear_local(form, values["--puidsearch--"])

    if "copy" in event:
        do_clipboard(event)

    if "resolve" in event:
        do_resolve(event)

    if "go to node" in event:
        do_go_to_node(values["--puidsearch--"])

    if event == "--update--":
        update_local_data(values["--puidsearch--"])

    if event == "--spawn_explorer_node--":
        do_spawn_explorer_node(values["--puidsearch--"])

    if event == "--spawn_explorer_testSet--":
        do_spawn_explorer_test_set(values["--puidsearch--"])
        



    if event == "--puid--":
        form["--ext--"].update("")
        my_puid = values["--puid--"]
        my_puid = my_puid.replace("/", "_")
        if my_puid in pronom_lookup:
            found_mime = pronom_lookup[my_puid]["mime"]
            if found_mime == "":
                found_mime = " None recorded"
            mime = found_mime 
            found_exts = pronom_lookup[my_puid]["exts"]
            if found_exts == []:
                found_exts = " None recorded \nMight be container based?\nTodo [containers]"
            else:
                found_exts = ", ".join(found_exts)
            txt = "MIME:"+mime+"\nExts: "+ found_exts
            form["-TOUT-"].update(txt)
        else:
            if my_puid:
                form["-TOUT-"].update(f"No puid found : {my_puid.replace('_', '/')}")
            else:
                form["-TOUT-"].update("")


    if event == "--ext--":
        form["--puid--"].update("")
        my_ext = values["--ext--"].lower()
        if my_ext in pronom_exts:
            txt = "\n".join([ x.replace("_", "/") for x in pronom_exts[my_ext]]) 
            form["-TOUT-"].update(txt)
        else:
            form["-TOUT-"].update("")

    if event == "Clipboard":
        pyperclip.copy(form["-TOUT-"].get())
