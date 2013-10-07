from gi.repository import Nautilus, GObject
import urllib

class NuxeoDriveFileInfoUpdater(GObject.GObject, Nautilus.InfoProvider):

    def __init__(self):
        self.driveRoots = []
        self.callCounter=0
        self.runAsync = False
    
    def update_file_info_full(self, provider, handle, closure, file):
        if (self.isDriveRoot(file)) :
            file.add_emblem("nxdrive")
        else : 
            if (self.isDriveManagedFile(file)) :
                uri = file.get_uri()[7:]
                if (self.runAsync) :
                    GObject.timeout_add_seconds(1, self.do_update_cb, provider, handle, closure, file, uri)
                    return Nautilus.OperationResult.IN_PROGRESS
                else : 
                    uri = file.get_uri()[7:]
                    self.getDriveManagedFileStatus(file, uri)

        self.callCounter = self.callCounter + 1
        # print "Counter => " + str(self.callCounter)
        return Nautilus.OperationResult.COMPLETE

    def decode(self,uri) :
        try:
          return urllib.unquote(uri)
        except TypeError:
          print "Error while processing " + uri 
          return uri.replace("%20", " ") 

    def getNuxeoDriveRoots(self):
        if (len(self.driveRoots)==0) :
            self.driveRoots = ["/home/tiry/Nuxeo Drive",]
        return self.driveRoots
    
    def isDriveRoot(self, file):
        uri = file.get_uri()[7:]
        fileName = self.decode(uri)
        if (fileName in self.getNuxeoDriveRoots()):
            return True
        else:
            return False
    
    def isDriveManagedFile(self, file):
        uri = file.get_uri()[7:]
        fileName = self.decode(uri)
        for root in self.getNuxeoDriveRoots() :
            if (fileName.startswith(root)) : 
                return True
        return False

    def getDriveManagedFileStatus(self, file, uri):
        # XXX
        file.add_emblem("OK")

        
    def do_update_cb(self, provider, handle, closure, file, uri):
        print "running async callback on " + str(file.get_uri())
        self.getDriveManagedFileStatus(file, uri)
        # Notify that we are done !
        Nautilus.info_provider_update_complete_invoke(closure, provider, handle, Nautilus.OperationResult.COMPLETE)
        print "update done"
        # return False to kill the timeout !
        return False



