# coding: utf-8

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

repolink = "https://github.com/%(user)s/%(repo)s/archive/master.zip"
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
        if err.getcode() == 406:
            console.alert("Error", "Repo not found", "Ok", hide_cancel_button=True)
        else:
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
        vers = [i["tag_name"] for i in data]
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

def gitdownload(button):
    isrelease = view.subviews[0].selected_index
    username  = view.subviews[2].text
    reponame  = view.subviews[4].text
    unzip     = view.subviews[7].value
    
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

view = ui.load_view('gitrepo')
cb = clipboard.get().strip()
parse = urlparse.urlparse(cb)
if parse.scheme:
    path = [i for i in parse.path.split("/") if i]
    if len(path) >= 2:
        view.subviews[2].text = path[0] # Username
        view.subviews[4].text = path[1] # Reponame
view.present('popover')
