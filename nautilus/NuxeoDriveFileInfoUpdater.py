from gi.repository import Nautilus, GObject
import urllib
#from gtk import Label
#import gtk
#import os
from gi.repository import Gtk


class NuxeoDriveFileInfoUpdater(GObject.GObject, Nautilus.InfoProvider,
                                Nautilus.PropertyPageProvider):

    def __init__(self):
        self.driveRoots = []
        self.callCounter = 0
        self.runAsync = False

    # Call back for fule info
    def update_file_info_full(self, provider, handle, closure, file_):
        if (self.isDriveRoot(file_)):
            file_.add_emblem("nxdrive")
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

    def getNuxeoDriveRoots(self):
        if (len(self.driveRoots) == 0):
            self.driveRoots = ["/home/ataillefer/Nuxeo Drive"]
        return self.driveRoots

    def isDriveRoot(self, file_):
        uri = file_.get_uri()[7:]
        fileName = self.decode(uri)
        if (fileName in self.getNuxeoDriveRoots()):
            return True
        else:
            return False

    def isDriveManagedFile(self, file_):
        uri = file_.get_uri()[7:]
        fileName = self.decode(uri)
        for root in self.getNuxeoDriveRoots():
            if (fileName.startswith(root)):
                return True
        return False

    def getDriveManagedFileStatus(self, file_, uri):
        # XXX
        file_.add_emblem("OK")

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
