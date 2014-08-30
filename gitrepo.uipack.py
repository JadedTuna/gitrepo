# -*- coding: utf-8 -*-
###############################################################################
# This is a self-extracting UI application package for gitrepo.
# Run this script once to extract the packaged application.
# The files will be extracted to gitrepo.py and gitrepo.pyui.
# Make sure that these files do not exist yet.
# To update from an older version, move or delete the old files first.
# After extracting, the application can be found at gitrepo.py.
# This bundle can be deleted after extraction.
###############################################################################
# Packaged using PackUI by dgelessus
# https://github.com/dgelessus/pythonista-scripts/blob/master/UI/PackUI.py
###############################################################################

import console, os.path

NAME     = "gitrepo"
PYFILE   = """# coding: utf-8

import ui
import json
import urllib2
import console
import zipfile
import urlparse
import clipboard
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO  import StringIO

class Delegate (object):
    def __init__(self):
        self.selrow = None
    
    def tableview_did_select(self, tableview, section, row):
        # Called when a row was selected.
        self.selrow = row
        tableview.superview.close()

    def tableview_did_deselect(self, tableview, section, row):
        # Called when a row was de-selected (in multiple selection mode).
        pass

    def tableview_title_for_delete_button(self, tableview, section, row):
        # Return the title for the 'swipe-to-***' button.
        return 'Delete'

repolink    = "https://github.com/%(user)s/%(repo)s/archive/master.zip"
browselink  = "https://api.github.com/users/%(user)s/repos"
releaselink = "https://api.github.com/repos/%(user)s/%(repo)s/releases"

@ui.in_background
def save_zip(data, name, unzip):
    if unzip:
        io = StringIO(data)
        with zipfile.ZipFile(io) as zp:
            zp.extractall()
    else:
        with open(name + ".zip", "wb") as zp:
            zp.write(data)

@ui.in_background
def download_repo(username, repo, unzip):
    formatdict = {
        "user": username,
        "repo": repo
    }
    
    try:
        page = urllib2.urlopen(repolink % formatdict)
    except urllib2.HTTPError as err:
        console.alert("Error", "Repo not found", "Ok", hide_cancel_button=True)
        return
    except:
        console.alert("Error", "Error downloading repo", "Ok", hide_cancel_button=True)
        return
        
    data = page.read()
    page.close()
    save_zip(data, repo, unzip)
    console.hud_alert("Done!")

@ui.in_background
def download_release(username, repo, unzip):
    formatdict = {
        "user": username,
        "repo": repo
    }
    
    page = urllib2.urlopen(releaselink % formatdict)
    data = json.load(StringIO(page.read()))
    page.close()
    
    if not data:
        console.alert("Error", "This repo has no releases", "Ok", hide_cancel_button=True)
        return
    
    elif "message" in data and data["message"] == "Not Found":
        console.alert("Error", "Repo not found", "Ok", hide_cancel_button=True)
        return
    
    else:
        vers = sorted([i["tag_name"] for i in data])
        rview = release_view(vers)
        rview.present("sheet")
        rview.wait_modal()
        
        row = rview["rtable"].delegate.selrow
        if row is None: return
        
        lastrls = data[row]
        zipurl  = lastrls["zipball_url"]
        page = urllib2.urlopen(zipurl)
        data = page.read()
        page.close()
        save_zip(data, lastrls["name"], unzip)
        console.hud_alert("Done!")

@ui.in_background
def gitdownload(button):
    isrelease = view["sgcontrol"].selected_index
    username  = view["username"].text
    reponame  = view["reponame"].text
    unzip     = view["dounzip"].value
    
    if not username.strip():
        console.alert("Error", "Please enter username", "Ok", hide_cancel_button=True)
        return
    
    if not reponame.strip():
        console.alert("Error", "Please enter repo name", "Ok", hide_cancel_button=True)
        return
    
    console.show_activity()
    if isrelease:
        download_release(username, reponame, unzip)
    else:
        download_repo(username, reponame, unzip)
    console.hide_activity()

@ui.in_background
def gitbrowse(sender):
    username  = view["username"].text
    if not username.strip():
        console.alert("Error", "Please enter username", "Ok", hide_cancel_button=True)
        return
    
    formatdict = {
        "user": username
    }
    try:
        page = urllib2.urlopen(browselink % formatdict)
    except urllib2.HTTPError as err:
        console.alert("Error", "User not found", "Ok", hide_cancel_button=True)
        return
    except:
        console.alert("Error", "Error downloading metadata", "Ok", hide_cancel_button=True)
        return
    data = json.load(StringIO(page.read()))
    page.close()
    
    if "message" in data and data["message"] == "Not Found":
        console.alert("Error", "User not found", "Ok", hide_cancel_button=True)
        return
    
    else:
        repos = sorted([i["name"] for i in data])
        rview = repo_view(repos)
        rview.present("sheet")
        rview.wait_modal()
        
        row = rview["rtable"].delegate.selrow
        if row is None: return
        
        repo = data[row]
        view["reponame"].text = repo["name"]

def release_view(releases):
    rview = ui.View(name="Choose release")
    lst   = ui.ListDataSource(releases)
    delegate = Delegate()
    
    table = ui.TableView()
    table.name = "rtable"
    table.flex = "WH"
    table.data_source = lst
    table.delegate = delegate
    
    rview.add_subview(table)
    return rview

def repo_view(repos):
    rview = ui.View(name="Choose a repo")
    lst   = ui.ListDataSource(repos)
    delegate = Delegate()
    
    table = ui.TableView()
    table.name = "rtable"
    table.flex = "WH"
    table.data_source = lst
    table.delegate = delegate
    
    rview.add_subview(table)
    return rview

view = ui.load_view('gitrepo')
cb = clipboard.get().strip()
parse = urlparse.urlparse(cb)
if parse.scheme:
    path = [i for i in parse.path.split("/") if i]
    if len(path) >= 2:
        view["username"].text = path[0]
        view["reponame"].text = path[1]
view.present('popover')
"""
PYUIFILE = """[{"class":"View","attributes":{"name":"gitrepo","background_color":"RGBA(1.000000,1.000000,1.000000,1.000000)","tint_color":"RGBA(0.000000,0.478000,1.000000,1.000000)","enabled":true,"border_color":"RGBA(0.000000,0.000000,0.000000,1.000000)","flex":""},"frame":"{{0, 0}, {341, 250}}","nodes":[{"class":"SegmentedControl","attributes":{"name":"sgcontrol","border_color":"RGBA(0.000000,0.000000,0.000000,1.000000)","uuid":"308A3491-ABAA-43BC-8D2C-1319469FF3C9","enabled":true,"segments":"Repo | Release","flex":"LR"},"frame":"{{16, 6}, {120, 29}}","nodes":[]},{"class":"Label","attributes":{"font_size":20,"enabled":true,"text":"Username:","flex":"","name":"label1","border_color":"RGBA(0.000000,0.000000,0.000000,1.000000)","text_color":"RGBA(0.000000,0.000000,0.000000,1.000000)","alignment":"left","uuid":"7C45FE1B-8084-4257-A1D1-DE573BC8299A"},"frame":"{{16.5, 57.5}, {96, 35.5}}","nodes":[]},{"class":"TextField","attributes":{"uuid":"18AD549C-48DF-40CF-B008-5E2C283AD3EA","alignment":"left","autocorrection_type":"no","font_size":17,"font_name":"Avenir-Book","enabled":true,"flex":"","border_color":"RGBA(0.571429,0.571429,0.571429,1.000000)","text_color":"RGBA(0.000000,0.000000,0.000000,1.000000)","corner_radius":2,"border_width":1,"secure":false,"border_style":3,"name":"username","spellchecking_type":"no"},"frame":"{{120.5, 57.5}, {200, 36}}","nodes":[]},{"class":"Label","attributes":{"font_size":20,"enabled":true,"text":"Repo:","flex":"","name":"label2","border_color":"RGBA(0.000000,0.000000,0.000000,1.000000)","text_color":"RGBA(0.000000,0.000000,0.000000,1.000000)","alignment":"left","uuid":"97359D8F-3BD5-4D8F-8711-14B4565F9601"},"frame":"{{16.5, 102}, {96, 35}}","nodes":[]},{"class":"TextField","attributes":{"name":"reponame","alignment":"left","autocorrection_type":"no","font_size":17,"font_name":"Avenir-Book","enabled":true,"flex":"","border_color":"RGBA(0.571429,0.571429,0.571429,1.000000)","text_color":"RGBA(0.000000,0.000000,0.000000,1.000000)","corner_radius":2,"border_width":1,"uuid":"7BFD908D-CA67-4976-94DD-5CF0DB5EC360","border_style":3,"secure":false,"spellchecking_type":"no"},"frame":"{{120, 101.5}, {200, 36}}","nodes":[]},{"class":"Button","attributes":{"font_size":16,"enabled":true,"flex":"","font_bold":false,"name":"dbutton","corner_radius":9,"border_color":"RGBA(0.244898,0.520408,0.857143,1.000000)","border_width":1,"action":"gitdownload","uuid":"7C58793E-E2CA-4724-B2FC-3E779FD71890","title":"Download"},"frame":"{{16.5, 201}, {96, 31}}","nodes":[]},{"class":"Label","attributes":{"font_size":20,"enabled":true,"text":"Unzip archive:","flex":"","name":"label3","border_color":"RGBA(0.000000,0.000000,0.000000,1.000000)","text_color":"RGBA(0.000000,0.000000,0.000000,1.000000)","alignment":"left","uuid":"3A801AA2-D086-48E9-9262-E9880135E8EA"},"frame":"{{16.5, 145}, {137, 35}}","nodes":[]},{"class":"Switch","attributes":{"enabled":true,"flex":"","name":"dounzip","value":true,"alpha":1,"border_color":"RGBA(0.000000,0.000000,0.000000,1.000000)","uuid":"40756EA8-214B-4247-9A47-F7D519C0BE88"},"frame":"{{161.5, 147}, {51, 31}}","nodes":[]},{"class":"Button","attributes":{"font_size":16,"enabled":true,"flex":"","font_bold":false,"name":"bbutton","corner_radius":9,"border_color":"RGBA(0.244898,0.520408,0.857143,1.000000)","border_width":1,"action":"gitbrowse","uuid":"127F82F8-97A9-4835-AD60-DF5FCDC942E3","title":"Browse repos"},"frame":"{{139, 201}, {119.5, 31}}","nodes":[]}]}]"""

def fix_quotes_out(s):
    return s.replace("\\\"\\\"\\\"", "\"\"\"").replace("\\\\", "\\")

def main():
    if os.path.exists(NAME + ".py"):
        console.alert("Failed to Extract", NAME + ".py already exists.")
        return
    
    if os.path.exists(NAME + ".pyui"):
        console.alert("Failed to Extract", NAME + ".pyui already exists.")
        return
    
    with open(NAME + ".py", "w") as f:
        f.write(fix_quotes_out(PYFILE))
    
    with open(NAME + ".pyui", "w") as f:
        f.write(fix_quotes_out(PYUIFILE))
    
    msg = NAME + ".py and " + NAME + ".pyui were successfully extracted!"
    console.alert("Extraction Successful", msg, "OK", hide_cancel_button=True)
    
if __name__ == "__main__":
    main()
