import urllib
import subprocess
import urlparse
from gi.repository import Nautilus, GObject
from gi.repository import Gtk


class NuxeoDriveFileInfoUpdater(GObject.GObject, Nautilus.InfoProvider,
                                Nautilus.PropertyPageProvider):

    def __init__(self):
        self.driveRoots = []
        self.callCounter = 0
        self.runAsync = False
        self.currentFolderUri = None
        self.syncStatuses = None

    # Call back for file info
    def update_file_info_full(self, provider, handle, closure, file_):
        if (self.isDriveRoot(file_)):
            print "Detected Nuxeo Drive folder: " + file_.get_uri()
            file_.add_emblem("drive_sync")
        else:
            if (self.isDriveManagedFile(file_)):
                uri = file_.get_uri()[7:]
                if (self.runAsync):
                    GObject.timeout_add_seconds(1, self.do_update_cb, provider,
                                                handle, closure, file_, uri)
                    return Nautilus.OperationResult.IN_PROGRESS
                else:
                    uri = file_.get_uri()[7:]
                    self.getDriveManagedFileStatus(file_, uri)

        self.callCounter = self.callCounter + 1
        # print "Counter => " + str(self.callCounter)
        return Nautilus.OperationResult.COMPLETE

    def get_property_pages(self, files):
        if not len(files):
            return
        if (len(files) > 1):
            return
        for file_ in files:
            if (not self.isDriveManagedFile(file_)):
                return

        self.property_label = Gtk.Label('Nuxeo Drive')
        self.property_label.show()
        self.hbox = Gtk.HBox(0, False)
        self.hbox.show()

        label = Gtk.Label('Last sync :')
        label.show()
        self.hbox.pack_start(label, expand=True, fill=True, padding=0)
        self.value_label = Gtk.Label()
        self.hbox.pack_start(self.value_label, expand=True, fill=True,
                             padding=0)
        self.value_label.set_text("???")
        self.value_label.show()

        return Nautilus.PropertyPage(name="NautilusPython::nuxeodrive",
                                     label=self.property_label,
                                     page=self.hbox),

    def decode(self, uri):
        try:
            return urllib.unquote(uri)
        except TypeError:
            print "Error while processing " + uri
            return uri.replace("%20", " ")

    def driveExec(self, cmds):
        # add the ndrive command !
        cmds.insert(0, "ndrive")
        print "Executing ndrive command: " + str(cmds)
        p = subprocess.Popen(cmds, stdout=subprocess.PIPE)
        result, _ = p.communicate()
        print "Result = " + result
        return eval(result)

    def getNuxeoDriveRoots(self):
        if (len(self.driveRoots) == 0):
            print "Getting Nuxeo Drive local folders"
            self.driveRoots = [urllib.quote(x) for x in
                                self.driveExec(['local_folders', ])]
        return self.driveRoots

    def isDriveRoot(self, file_):
        path = urlparse.urlparse(file_.get_uri()).path
        if (path in self.getNuxeoDriveRoots()):
            return True
        else:
            return False

    def isDriveManagedFile(self, file_):
        path = urlparse.urlparse(file_.get_uri()).path
        for root in self.getNuxeoDriveRoots():
            if (path.startswith(root)):
                return True
        return False

    def getDriveManagedFileStatus(self, file_, uri):
        # XXX
        folder_uri = file_.get_parent_uri()
        folder_uri = urlparse.urlparse(urllib.unquote(folder_uri)).path
        t = self.currentFolderUri if self.currentFolderUri is not None else ""
        if (not self.currentFolderUri == folder_uri):
            print "Getting Nuxeo Drive status for " + folder_uri
            self.syncStatuses = self.driveExec(['status',
                                                '--folder', folder_uri])
            self.currentFolderUri = folder_uri
        icon_set = False
        for t in self.syncStatuses:
            if (t[0] == urllib.unquote(file_.get_name())):
                print "Status of " + t[0] + " = " + t[1]
                status = t[1]
                status_icon = self.get_status_icon(status)
                file_.add_emblem(status_icon)
                icon_set = True
        if not icon_set:
            file_.add_emblem('drive_not_sync')

    def get_status_icon(self, status):
        if status == 'synchronized':
            return 'drive_sync'
        else:
            return 'drive_pending'

    def do_update_cb(self, provider, handle, closure, file_, uri):
        print "running async callback on " + str(file.get_uri())
        self.getDriveManagedFileStatus(file, uri)
        # Notify that we are done !
        Nautilus.info_provider_update_complete_invoke(closure, provider,
                                            handle,
                                            Nautilus.OperationResult.COMPLETE)
        print "update done"
        # return False to kill the timeout !
        return False
