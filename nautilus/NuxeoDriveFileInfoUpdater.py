from gi.repository import Nautilus, GObject
import urllib

class NuxeoDriveFileInfoUpdater(GObject.GObject, Nautilus.InfoProvider):

    def __init__(self):
        self.driveRoots = []
        self.callCounter=0
    
    def update_file_info_full(self, provider, handle, closure, file):
        if (self.isDriveRoot(file)) :
            file.add_emblem("nxdrive")
        else : 
            if (self.isDriveManagedFile(file)) :
                self.getDriveManagedFileStatus(file)

        self.callCounter = self.callCounter + 1
        print "Counter => " + str(self.callCounter)
        # self.isDriveManagedFile(file)
        # GObject.timeout_add_seconds(5, self.do_update_cb, provider, handle, closure, file)
        # return Nautilus.OperationResult.IN_PROGRESS
        return Nautilus.OperationResult.COMPLETE

    def getNuxeoDriveRoots(self):
        if (len(self.driveRoots)==0) :
            self.driveRoots = ["/home/tiry/Nuxeo Drive",]
        return self.driveRoots
    
    def isDriveRoot(self, file):
        fileName = urllib.unquote(file.get_uri()[7:])
        if (fileName in self.getNuxeoDriveRoots()):
            return True
        else:
            return False
    
    def isDriveManagedFile(self, file):
        fileName = urllib.unquote(file.get_uri()[7:])
        for root in self.getNuxeoDriveRoots() :
            if (fileName.startswith(root)) : 
                return True
        return False

    def getDriveManagedFileStatus(self, file):
        # XXX
        file.add_emblem("OK")

        
    def do_update_cb(self, provider, handle, closure, file):
        print "update_cb " + str(file)
        #file.add_emblem("OK")
        Nautilus.info_provider_update_complete_invoke(closure, provider, handle, Nautilus.OperationResult.COMPLETE)
