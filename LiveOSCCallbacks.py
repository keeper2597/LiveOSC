"""
# Copyright (C) 2007 Rob King (rob@re-mu.org)
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# For questions regarding this module contact
# Rob King <rob@e-mu.org> or visit http://www.e-mu.org

This file contains all the current Live OSC callbacks. 

"""
import Live
import RemixNet
import OSC
import LiveUtils
import ClipMonitor
import sys
import re
import time
import string
import random

from Logger import log


debug = LiveUtils.debug


"""
    This class sets the address to call for much of the LiveAPI interactions.
    The callbackManager.add() puts them in a dictionary in the CallbackManager class in the OSC.py document
    The CallbackManager class adds a prefix for each address so one should not be added here
"""

class LiveOSCCallbacks:
    def __init__(self, c_instance, oscEndpoint):
        self.oscEndpoint = oscEndpoint
        self.callbackManager = oscEndpoint.callbackManager

        self.c_instance = c_instance

        self.sceneIdentifier = " #cS"
        self.trackIdentifier = " #cT"
        self.clipIdentifier = " #cC"
        self.clipSlotIdentifier = " #cL"

        ###################################################################################################################
        #######################################      GLOBAL                  ##############################################
        ###################################################################################################################

        self.callbackManager.add("/global/tempo", self.tempoCB)
        self.callbackManager.add("/global/time", self.timeCB)
        self.callbackManager.add("/global/quantization", self.quantizationCB)
        self.callbackManager.add("/global/selection", self.selectionCB)
        self.callbackManager.add("/global/undo", self.undoCB)
        self.callbackManager.add("/global/redo", self.redoCB)
        self.callbackManager.add("/global/play", self.playCB)
        self.callbackManager.add("/global/continue", self.playContinueCB)
        self.callbackManager.add("/global/playselection", self.playSelectionCB)  
        self.callbackManager.add("/global/stop", self.stopCB)
        self.callbackManager.add("/global/stopclips", self.stopAllClipsCB)


        self.callbackManager.add("/scan/tracks", self.trackScanCB)
        self.callbackManager.add("/scan/scenes", self.sceneScanCB)
        self.callbackManager.add("/scan", self.scanCB)

        ###################################################################################################################
        #######################################      SCENES                  ##############################################
        ###################################################################################################################

        self.callbackManager.add("/scene/play", self.playSceneCB)
        self.callbackManager.add("/scene/play/id", self.playSceneIDCB)
        self.callbackManager.add("/scene/count", self.scenecountCB)
        self.callbackManager.add("/scene/name", self.nameSceneCB)  #only for individual scenes now
        self.callbackManager.add("/scene/scan", self.sceneScanCB)
        self.callbackManager.add("/scene", self.sceneCB)
        self.callbackManager.add("/sceneblock/name", self.nameSceneBlockCB)

        ###################################################################################################################
        #######################################      TRACKS                  ##############################################
        ###################################################################################################################

        self.callbackManager.add("/track/stop", self.stopTrackCB)
        self.callbackManager.add("/track/name", self.nameTrackCB)
        self.callbackManager.add("/track/count", self.trackcountCB)
        self.callbackManager.add("/trackblock/name", self.nameTrackBlockCB)
        self.callbackManager.add("/track/arm", self.armTrackCB)
        self.callbackManager.add("/track/mute", self.muteTrackCB)
        self.callbackManager.add("/track/solo", self.soloTrackCB)
        self.callbackManager.add("/track/volume", self.volumeCB)
        self.callbackManager.add("/track/pan", self.panCB)
        self.callbackManager.add("/track/send", self.sendCB)
        self.callbackManager.add("/track/jump", self.trackJump)
        self.callbackManager.add("/track/info", self.trackInfoCB)


        ###################################################################################################################
        #######################################      CLIPS                   ##############################################
        ###################################################################################################################

        self.callbackManager.add("/clip/play", self.playClipCB)
        self.callbackManager.add("/clip/stop", self.stopClipCB)
        self.callbackManager.add("/clip/name", self.nameClipCB)
        self.callbackManager.add("/clip/info", self.clipInfoCB)
        self.callbackManager.add("/clipblock/name", self.nameClipBlockCB)    
        self.callbackManager.add("/clip/pitch", self.pitchCB)
        self.callbackManager.add("/clip/loopstate", self.loopStateCB)
        self.callbackManager.add("/clip/loopstart", self.loopStartCB)
        self.callbackManager.add("/clip/loopend", self.loopEndCB)
        self.callbackManager.add("/clip/loopstate_id", self.loopStateCB)
        self.callbackManager.add("/clip/loopstart_id", self.loopStartCB)
        self.callbackManager.add("/clip/loopend_id", self.loopEndCB)
        
        self.callbackManager.add("/clip/warping", self.warpingCB)
        self.callbackManager.add("/clip/signature", self.sigCB)

        self.callbackManager.add("/clip/add_note", self.addNoteCB)
        self.callbackManager.add("/clip/notes", self.getNotesCB)
        self.callbackManager.add("/clip/create", self.createClipCB)
        self.callbackManager.add("/clip/delete", self.deleteClipCB)

        self.callbackManager.add("/clip/mute", self.muteClipCB)
        self.callbackManager.add("/clipslot/play", self.playClipSlotCB)

        
        
        # self.callbackManager.add("/scene/view", self.viewSceneCB)
        # self.callbackManager.add("/track/view", self.viewTrackCB)
        # self.callbackManager.add("/return/view", self.viewTrackCB)
        # self.callbackManager.add("/master/view", self.mviewTrackCB)
        # self.callbackManager.add("/track/device/view", self.viewDeviceCB)
        # self.callbackManager.add("/return/device/view", self.viewDeviceCB)
        # self.callbackManager.add("/master/device/view", self.mviewDeviceCB)        
        # self.callbackManager.add("/clip/view", self.viewClipCB)
        # self.callbackManager.add("/detail/view", self.detailViewCB)
        

        # self.callbackManager.add("/overdub", self.overdubCB)
        # self.callbackManager.add("/state", self.stateCB)
        
        
        self.callbackManager.add("/return/mute", self.muteTrackCB)
        self.callbackManager.add("/return/solo", self.soloTrackCB)
        self.callbackManager.add("/return/volume", self.volumeCB)
        self.callbackManager.add("/return/pan", self.panCB)
        self.callbackManager.add("/return/send", self.sendCB)        

        self.callbackManager.add("/master/volume", self.volumeCB)
        self.callbackManager.add("/master/pan", self.panCB)
        
        # self.callbackManager.add("/devicelist", self.devicelistCB)
        # self.callbackManager.add("/return/devicelist", self.devicelistCB)
        # self.callbackManager.add("/master/devicelist", self.mdevicelistCB)

        # self.callbackManager.add("/device/range", self.devicerangeCB)
        # self.callbackManager.add("/return/device/range", self.devicerangeCB)
        # self.callbackManager.add("/master/device/range", self.mdevicerangeCB)
        
        # self.callbackManager.add("/device", self.deviceCB)
        # self.callbackManager.add("/return/device", self.deviceCB)
        # self.callbackManager.add("/master/device", self.mdeviceCB)
        
        

        # self.callbackManager.add("/master/crossfader", self.crossfaderCB)
        # self.callbackManager.add("/track/crossfader", self.trackxfaderCB)
        # self.callbackManager.add("/return/crossfader", self.trackxfaderCB)

        

        # self.callbackManager.add("/deactivate", self.deactivateCB)
        # self.callbackManager.add("/clear_inactive", self.clearInactiveCB)
        # self.callbackManager.add("/filter_clips", self.filterClipsCB)
        # self.callbackManager.add("/distribute_groups", self.distributeGroupsCB)
        # self.callbackManager.add("/play/group_scene", self.playGroupSceneCB)

        self.callbackManager.add("/playMode", self.setPlayModeCB)

        self.clip_notes_cache = {}

    def makeID(self, stringLength=4):
        lettersAndDigits = string.ascii_letters + string.digits
        return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))

    def tempoCB(self, msg, source):
        """Called when a /tempo message is received.

        Messages:
        /tempo                 Request current tempo, replies with /tempo (float tempo)
        /tempo (float tempo)   Set the tempo, replies with /tempo (float tempo)
        """
        if len(msg) == 2 or (len(msg) == 3 and msg[2] == "query"):
            self.oscEndpoint.send("/global/tempo", LiveUtils.getTempo())
        
        elif len(msg) == 3:
            tempo = msg[2]
            LiveUtils.setTempo(tempo)
    
    def timeCB(self, msg, source):
        """Called when a /time message is received.

        Messages:
        /time                 Request current song time, replies with /time (float time)
        /time (float time)    Set the time , replies with /time (float time)
        """
        if len(msg) == 2 or (len(msg) == 3 and msg[2] == "query"):
            self.oscEndpoint.send("/global/time", float(LiveUtils.currentTime()))

        elif len(msg) == 3:
            time = msg[2]
            LiveUtils.currentTime(time)


    # self.callbackManager.add("/next/cue", self.nextCueCB)
    # self.callbackManager.add("/prev/cue", self.prevCueCB)

    ###################################################################################################################
    #######################################      PLAY / STOP             ##############################################
    ###################################################################################################################


    def playCB(self, msg, source):
        LiveUtils.play()
    
    def playContinueCB(self, msg, source):
        LiveUtils.continuePlaying()
        
    def playSelectionCB(self, msg, source):
        LiveUtils.playSelection()
        
    def playClipCB(self, msg, source):
        if len(msg) == 4:
            track = int(msg[2])
            clip = int(msg[3])
            LiveUtils.launchClip(track, clip)
            
    def playSceneCB(self, msg, source):
        if len(msg) == 3:
            scene = msg[2]
            LiveUtils.launchScene(scene)

    def playSceneIDCB(self, msg, source):
        if len(msg) == 3:
            sceneID = msg[2]
            for scene in LiveUtils.getScenes():
                if scene.name.find(sceneID) != -1:
                #if self.hasString(sceneID, scene.name):
                    scene.fire()
        else:
            log("playSceneIDCB couldn't find a matching ID for:")
            log(sceneID)
    
    def stopCB(self, msg, source):
        LiveUtils.stop()

    def stopAllClipsCB(self, msg, source):
        """Called when a /stop/clips message is received.

        Messages:
        /stop              Stops playing the song
        """
        LiveUtils.stopClips()
        
    def stopClipCB(self, msg, source):
        """Called when a /stop/clip message is received.

        Messages:
        /stop/clip     (int track, int clip)   Stops clip number clip in track number track
        """
        if len(msg) == 4:
            track = msg[2]
            clip = msg[3]
            LiveUtils.stopClip(track, clip)

    def stopTrackCB(self, msg, source):
        """Called when a /track/stop message is received.

        Messages:
        /track/stop     (int track, int clip)   Stops track number track
        """
        if len(msg) == 3:
            track = msg[2]
            LiveUtils.stopTrack(track)


    ###################################################################################################################
    #######################################      SCENE MANAGEMENT        ##############################################
    ###################################################################################################################



    def sceneCB(self, msg, source):
        """Called when a /scene message is received.
        
        Messages:
        /scene         no argument or 'query'  Returns the currently selected scene index
        """
        if len(msg) == 2 or (len(msg) == 3 and msg[2] == "query"):
            selected_scene = LiveUtils.getSong().view.selected_scene
            scenes = LiveUtils.getScenes()
            index = 0
            selected_index = 0
            for scene in scenes:
                index = index + 1        
                if scene == selected_scene:
                    selected_index = index
                    
            self.oscEndpoint.send("/scene", (selected_index))
            
        elif len(msg) == 3:
            scene = msg[2]
            LiveUtils.getSong().view.selected_scene = LiveUtils.getSong().scenes[scene]

    def trackcountCB(self, msg, source):
        """Called when a /trackcount message is received.

        Messages:
        /trackcount       no argument or 'query'  Returns the total number of scenes

        """
        if len(msg) == 2 or (len(msg) == 3 and msg[2] == "query"):
            trackTotal = len(LiveUtils.getTracks())
            self.oscEndpoint.send("/tracks", (trackTotal))
            return

    def scenecountCB(self, msg, source):
        """Called when a /scenecount message is received.

        Messages:
        /scenecount        no argument or 'query'  Returns the total number of scenes

        """
        #if len(msg) == 2 or (len(msg) == 3 and msg[2] == "query"):
        sceneTotal = len(LiveUtils.getScenes())
        self.oscEndpoint.send("/scenes", (sceneTotal))
        return

    def sceneScanCB(self, msg, source):
        #/scan/scenes                            Returns a a series of all the scene names in the form /scene/name (int scene, string name)
        bundle = OSC.OSCBundle()
        sceneNumber = 0
        for scene in LiveUtils.getScenes():
            bundle.append("/scan/scenes", (sceneNumber, str(scene.name)))
            sceneNumber = sceneNumber + 1
        self.oscEndpoint.sendMessage(bundle)
        return



    def nameSceneCB(self, msg, source):
        """Called when a /scene/name message is received.
        /scene/name    (int scene)             Returns a single scene's name in the form /scene/name (int scene, string name)
        /scene/name    (int scene, string name)Sets scene number scene's name to name
        """        
            
        #Requesting a single scene name
        if len(msg) == 3:
            sceneNumber = int(msg[2])
            self.oscEndpoint.send("/scene/name", (sceneNumber, str(LiveUtils.getScene(sceneNumber).name)))
            return
        #renaming a scene
        if len(msg) == 4:
            sceneNumber = int(msg[2])
            name = msg[3]
            LiveUtils.getScene(sceneNumber).name = name
            self.oscEndpoint.send("/scene/name", (sceneNumber, str(LiveUtils.getScene(sceneNumber).name)))

    def nameSceneBlockCB(self, msg, source):
        """Called when a /name/sceneblock message is received.

        /name/clipblock    (int offset, int blocksize) Returns a list of blocksize scene names starting at offset
        """
        if len(msg) == 4:
            block = []
            sceneOffset = int(msg[2])
            blocksize = int(msg[3])
            for scene in range(0, blocksize):
                block.extend([str(LiveUtils.getScene(sceneOffset+scene).name)])                            
            self.oscEndpoint.send("/sceneblock/name", block)

    def scanCB(self, msg, source):
        #/scan/scenes                            Returns a a series of all the scene names in the form /scene/name (int scene, string name)
        log("scanCB called")
        fullBundle = OSC.OSCBundle()
        sceneBundle = OSC.OSCBundle()
        trackBundle = OSC.OSCBundle()
        sceneNumber = 0
        trackNumber = 0
        for scene in LiveUtils.getScenes():
            
            #check to see if we already scanned this
            alreadyScanned = scene.name.find(self.sceneIdentifier)
            log(alreadyScanned)
            #if self.hasString(self.sceneIdentifier, scene.name):
            if (scene.name.find(self.sceneIdentifier) == -1):
                scanID = self.sceneIdentifier + self.makeID()
                scene.name = scene.name + scanID

            sceneBundle.append("/scan/scenes", (sceneNumber, str(scene.name), scene.tempo))

            # check for clips
            clipBundle = OSC.OSCBundle()
            foundClip = False
            slotNumber = 0
            for slot in scene.clip_slots:
                clip = slot.clip
                if clip is not None:
                    if (clip.name.find(self.clipIdentifier) == -1):
                        scanID = self.clipIdentifier + self.makeID()
                        clip.name = clip.name + scanID
                    if clip.is_audio_clip:
                        warping = clip.warping
                    else:
                        warping = False
                    clipBundle.append("/scan/clips", (slotNumber, clip.name, clip.length, warping, clip.looping, clip.loop_start, clip.loop_end, clip.signature_numerator, clip.signature_denominator))
                    foundClip = True
                slotNumber = slotNumber + 1
            if foundClip:
                sceneBundle.append(clipBundle)


            sceneNumber = sceneNumber + 1
        for track in LiveUtils.getTracks():

            #if self.hasString(self.trackIdentifier, track.name):
            if (track.name.find(self.trackIdentifier) == -1):
                scanID = self.trackIdentifier + self.makeID()
                track.name = track.name + scanID

            trackType = 'MIDI' if track.has_midi_input else 'Audio'
            trackBundle.append("/scan/tracks", (trackNumber, str(track.name), str(trackType)))
            trackNumber = trackNumber + 1
        fullBundle.append(sceneBundle)
        fullBundle.append(trackBundle)
        self.oscEndpoint.sendMessage(fullBundle)
        return
    

    def setPlayModeCB(self, msg, source):
        ClipMonitor.playMode = str(msg[2])
        self.oscEndpoint.send("/playMode", msg[2])
        if debug:
            log("setPlayModeCB called by OSC with message: " + str(msg[2]))


    def sigCB(self, msg, source):
        """ Called when a /clip/signature message is recieved
        """
        track = msg[2]
        clip = msg[3]
        c = LiveUtils.getSong().tracks[track].clip_slots[clip].clip
        
        if len(msg) == 4:
            self.oscEndpoint.send("/clip/signature", (track, clip, c.signature_numerator, c.signature_denominator))
            
        if len(msg) == 6:
            self.oscEndpoint.send("/clip/signature", 1)
            c.signature_denominator = msg[5]
            c.signature_numerator = msg[4]

    def warpingCB(self, msg, source):
        """ Called when a /clip/warping message is recieved
        """
        track = msg[2]
        clip = msg[3]
        
        
        if len(msg) == 4:
            state = LiveUtils.getSong().tracks[track].clip_slots[clip].clip.warping
            self.oscEndpoint.send("/clip/warping", (track, clip, int(state)))
        
        elif len(msg) == 5:
            LiveUtils.getSong().tracks[track].clip_slots[clip].clip.warping = msg[4]

    def selectionCB(self, msg, source):
        """ Called when a /selection message is received
        """
        if len(msg) == 6:
            self.c_instance.set_session_highlight(msg[2], msg[3], msg[4], msg[5], 0)

    def trackxfaderCB(self, msg, source):
        """ Called when a /track/crossfader or /return/crossfader message is received
        """
        ty = msg[0] == '/return/crossfader' and 1 or 0
    
        if len(msg) == 3:
            track = msg[2]
        
            if ty == 1:
                assign = LiveUtils.getSong().return_tracks[track].mixer_device.crossfade_assign
                name   = LiveUtils.getSong().return_tracks[track].mixer_device.crossfade_assignments.values[assign]
            
                self.oscEndpoint.send("/return/crossfader", (track, str(assign), str(name)))
            else:
                assign = LiveUtils.getSong().tracks[track].mixer_device.crossfade_assign
                name   = LiveUtils.getSong().tracks[track].mixer_device.crossfade_assignments.values[assign]
            
                self.oscEndpoint.send("/track/crossfader", (track, str(assign), str(name)))

            
        elif len(msg) == 4:
            track = msg[2]
            assign = msg[3]
            
            if ty == 1:
                LiveUtils.getSong().return_tracks[track].mixer_device.crossfade_assign = assign
            else:
                LiveUtils.getSong().tracks[track].mixer_device.crossfade_assign = assign

    

    # def nextCueCB(self, msg, source):
    #     """Called when a /next/cue message is received.

    #     Messages:
    #     /next/cue              Jumps to the next cue point
    #     """
    #     LiveUtils.jumpToNextCue()
        
    # def prevCueCB(self, msg, source):
    #     """Called when a /prev/cue message is received.

    #     Messages:
    #     /prev/cue              Jumps to the previous cue point
    #     """
    #     LiveUtils.jumpToPrevCue()
        
    
    def trackScanCB(self, msg, source):
        #/scan/tracks                  Returns a a series of all the track names in the form /track/name (int track, string name)
        #Requesting all track names
        trackNumber = 0
        bundle = OSC.OSCBundle()
        for track in LiveUtils.getTracks():
            bundle.append("/scan/tracks", (trackNumber, str(track.name)))
            trackNumber = trackNumber + 1
        self.oscEndpoint.sendMessage(bundle)
        return
    
            
            
    def nameTrackCB(self, msg, source):
        """Called when a /name/track message is received.
        Messages:
        /track/name   (int track)             Returns a single track's name in the form /track/name (int track, string name)
        /track/name    (int track, string name)Sets track number track's name to name
        """ 
        #Requesting a single track name
        if len(msg) == 3:
            trackNumber = msg[2]
            self.oscEndpoint.send("/track/name", (trackNumber, str(LiveUtils.getTrack(trackNumber).name)))
            return
        #renaming a track
        if len(msg) == 4:
            trackNumber = msg[2]
            name = msg[3]
            LiveUtils.getTrack(trackNumber).name = name

    def nameTrackBlockCB(self, msg, source):
        """Called when a /trackblock/name message is received.

        /trackblock/name    (int offset, int blocksize) Returns a list of blocksize track names starting at offset
        """
        if len(msg) == 4:
            block = []
            trackOffset = int(msg[2])
            blocksize = int(msg[3])
            for track in range(0, blocksize):
                block.extend([str(LiveUtils.getTrack(trackOffset+track).name)])                            
            self.oscEndpoint.send("/trackblock/name", block)

    def nameClipBlockCB(self, msg, source):
        """Called when a /name/clipblock message is received.

        /clipblock/name    (int track, int clip, blocksize x/tracks, blocksize y/clipslots) Returns a list of clip names for a block of clips (int blockX, int blockY, clipname)

        """
        #Requesting a block of clip names X1 Y1 X2 Y2 where X1,Y1 is the first clip (track, clip) of the block, X2 the number of tracks to cover and Y2 the number of scenes
        
        if len(msg) == 6:
            block = []
            trackOffset = int(msg[2])
            clipOffset = int(msg[3])
            blocksizeX = int(msg[4])
            blocksizeY = int(msg[5])
            for clip in range(0, blocksizeY):
                for track in range(0, blocksizeX):
                        trackNumber = trackOffset+track
                        clipNumber = clipOffset+clip
                        if LiveUtils.getClip(trackNumber, clipNumber) != None:
                            block.extend([str(LiveUtils.getClip(trackNumber, clipNumber).name)])
                        else:
                            block.extend([""])
                            
            self.oscEndpoint.send("/clipbock/name", block)



    def nameClipCB(self, msg, source):
        """Called when a /clip/name message is received.

        Messages:
        /clip/name                                      Returns a a series of all the clip names in the form /clip/name (int track, int clip, string name)
        /clip/name    (int track, int clip)             Returns a single clip's name in the form /clip/name (int clip, string name)
        /clip/name    (int track, int clip, string name)Sets clip number clip in track number track's name to name

        """

        #Requesting all clip names
        if len(msg) == 2 or (len(msg) == 3 and msg[2] == "query"):
            trackNumber = 0
            clipNumber = 0
            for track in LiveUtils.getTracks():
                bundle = OSC.OSCBundle()
                for clipSlot in track.clip_slots:
                    if clipSlot.clip != None:
                        bundle.append("/clip/name", (trackNumber, clipNumber, str(clipSlot.clip.name), clipSlot.clip.color))
                    clipNumber = clipNumber + 1
                self.oscEndpoint.sendMessage(bundle)
                clipNumber = 0
                trackNumber = trackNumber + 1
            return
        #Requesting a single clip name
        if len(msg) == 4:
            trackNumber = msg[2]
            clipNumber = msg[3]
            self.oscEndpoint.send("/clip/name", (trackNumber, clipNumber, str(LiveUtils.getClip(trackNumber, clipNumber).name), LiveUtils.getClip(trackNumber, clipNumber).color))
            return
        #renaming a clip
        if len(msg) >= 5:
            trackNumber = msg[2]
            clipNumber = msg[3]
            name = msg[4]
            LiveUtils.getClip(trackNumber, clipNumber).name = name

        if len(msg) >= 6:
            trackNumber = msg[2]
            clipNumber = msg[3]
            color = msg[5]
            LiveUtils.getClip(trackNumber, clipNumber).color = color

    def addNoteCB(self, msg, source):
        """Called when a /clip/add_note message is received

        Messages:
        /clip/add_note (int pitch) (double time) (double duration) (int velocity) (bool muted)    Add the given note to the clip
        """
        trackNumber = msg[2]
        clipNumber = msg[3]
        pitch = int(msg[4])
        time = msg[5]
        duration = msg[6]
        velocity = int(msg[7])
        muted = msg[8]
        LiveUtils.getClip(trackNumber, clipNumber).deselect_all_notes()

        notes = ((pitch, time, duration, velocity, muted),)
        LiveUtils.getClip(trackNumber, clipNumber).replace_selected_notes(notes)
        self.oscEndpoint.send('/clip/note', (trackNumber, clipNumber, pitch, time, duration, velocity, muted))

    def getNotesCB(self, msg, source):
        """Called when a /clip/notes message is received

        Messages:
        /clip/notes    Return all notes in the clip in /clip/note messages.  Each note is sent in the format
                            (int trackNumber) (int clipNumber) (int pitch) (double time) (double duration) (int velocity) (int muted)
        """
        trackNumber = msg[2]
        clipNumber = msg[3]
        LiveUtils.getClip(trackNumber, clipNumber).select_all_notes()
        bundle = OSC.OSCBundle()
        for note in LiveUtils.getClip(trackNumber, clipNumber).get_selected_notes():
            pitch = note[0]
            time = note[1]
            duration = note[2]
            velocity = note[3]
            muted = 0
            if note[4]:
                muted = 1
            bundle.append('/clip/note', (trackNumber, clipNumber, pitch, time, duration, velocity, muted))
        self.oscEndpoint.sendMessage(bundle)

    def createClipCB(self, msg, source):
        """
        Messages:
        /clip/create (int track, int slot, float length)
        Create a clip in [track, slot], length [length] beats
        """
        clipSlots = LiveUtils.getClipSlots()
        track_index = msg[2]
        clipslot_index = msg[3]
        length = msg[4]

        track = LiveUtils.getTrack(track_index)
        clipslot = track.clip_slots[clipslot_index]
        clipslot.create_clip(length)
    
    def deleteClipCB(self, msg, source):
        """
        Messages:
        /clip/delete (int track, int slot)
        Delete clip at [track, slot]
        """
        clipSlots = LiveUtils.getClipSlots()
        track_index = msg[2]
        clipslot_index = msg[3]

        track = LiveUtils.getTrack(track_index)
        clipslot = track.clip_slots[clipslot_index]
        clipslot.delete_clip()
    
    def armTrackCB(self, msg, source):
        """Called when a track/arm message is received.

        Messages:
        /arm     (int track)   (int armed/disarmed)     Arms track number track
        """
        track = msg[2]
        
        if len(msg) == 4:
            if msg[3] == 1:
                LiveUtils.armTrack(track)
            else:
                LiveUtils.disarmTrack(track)
        # Return arm status        
        elif len(msg) == 3:
            status = LiveUtils.getTrack(track).arm
            self.oscEndpoint.send("track/arm", (track, int(status)))     
            
    def muteTrackCB(self, msg, source):
        """Called when a track/mute or return/mute message is received.

        Messages:
        /mute     (int track)   Mutes track number track
        """
        ty = msg[0] == '/return/mute' and 1 or 0
        track = msg[2]
            
        if len(msg) == 4:
            if msg[3] == 1:
                LiveUtils.muteTrack(track, ty)
            else:
                LiveUtils.unmuteTrack(track, ty)
                
        elif len(msg) == 3:
            if ty == 1:
                status = LiveUtils.getSong().return_tracks[track].mute
                self.oscEndpoint.send("/return/mute", (track, int(status)))
                
            else:
                status = LiveUtils.getTrack(track).mute
                self.oscEndpoint.send("track/mute", (track, int(status)))

    def deactivateCB(self, msg, source):
        for track in LiveUtils.getTracks():
            for slot in track.clip_slots:
                if slot.clip != None:
                    slot.clip.muted = True

    def clearInactiveCB(self, msg, source):
        log("clearing inactive")
        for track in LiveUtils.getTracks():
            for slot in track.clip_slots:
                if slot.clip != None and slot.clip.muted:
                    slot.delete_clip()

    def nameToMIDI(self, name):
        """ Maps a MIDI note name (D3, C#6) to a value.
        Assumes that middle C is C4. """
        note_names = [
            [ "C" ],
            [ "C#", "Db" ],
            [ "D" ],
            [ "D#", "Eb" ],
            [ "E" ],
            [ "F" ],
            [ "F#", "Gb" ],
            [ "G" ],
            [ "G#", "Ab" ],
            [ "A" ],
            [ "A#", "Bb" ],
            [ "B" ]
        ]

        if name[-1].isdigit():
            octave = int(name[-1])
            name = name[:-1]
        else:
            octave = 0

        try:
            index = note_names.index([nameset for nameset in note_names if name in nameset][0])
            return octave * 12 + index
        except:
            return None
                    
    def filterClipsCB(self, msg, source):
        def bipolar_diverge(maximum):
            """ returns [0, 1, -1, ...., maximum, -maximum ] """
            sequence = list(sum(list(zip(list(range(maximum + 1)), list(range(0, -maximum - 1, -1)))), ()))
            sequence.pop(0)
            return sequence

        def filter_tone_row(source, target, bend_limit = 7):
            """ filters the notes in <source> by the permitted notes in <target>.
            returns a tuple (<bool> acceptable, <int> pitch_bend) """
            bends = bipolar_diverge(bend_limit)
            for bend in bends:
                if all(((note + bend) % 12) in target for note in source):
                    return (True, bend)
            return (False, 0)

        if not self.clip_notes_cache:
            log("no cache found, creating")
            self._filterClipsMakeCache()

        try:
            t0 = time.time()
            note_names = msg[2:]
            log("filtering clips according to %s" % note_names)
            target = tuple(self.nameToMIDI(note) for note in note_names)

            clip_states = {}
            if target in self.clip_tone_row_cache:
                log(" - found cached")
                clip_states = self.clip_tone_row_cache[target]
            else:
                log(" - not found in cache, calculating")
                for track_index, track in enumerate(LiveUtils.getTracks()):
                    for clip_index, slot in enumerate(track.clip_slots):
                        if slot.clip != None:
                            notes = self.clip_notes_cache[track_index][clip_index]
                            # log(" - found notes: %s" % notes)

                            if notes:
                                # don't transpose for now
                                acceptable, bend = filter_tone_row(notes, target, 0)
                                clip_states[slot.clip] = acceptable
                self.clip_tone_row_cache[target] = clip_states

            for clip, acceptable in clip_states.items():
                clip.muted = not acceptable
        except Exception, e:
            log("filtering failed (%s); rebuilding cache" % e)
            self._filterClipsMakeCache()

        log("filtered clips (took %.3fs)" % (time.time() - t0))

    def _filterClipsMakeCache(self, msg = None, source = None):
        self.clip_notes_cache = {}
        self.clip_tone_row_cache = {}
        log("making clip filter cache")
        t0 = time.time()
        try:
            for track_index, track in enumerate(LiveUtils.getTracks()):
                self.clip_notes_cache[track_index] = {}
                for clip_index, slot in enumerate(track.clip_slots):
                    if slot.clip is not None:

                        # match = re.search("(^|[_-])([A-G][A-G#b1-9-]*)$", slot.clip.name)
                        match = re.search("([_-])([A-G][A-G#b1-9-]*)$", slot.clip.name)
                        if match:
                            notes_found_str = match.group(2)
                            notes_found_str = re.sub("[1-9]", "", notes_found_str)
                            notes_found = notes_found_str.split("-")
                            notes = [ self.nameToMIDI(note) for note in notes_found ]

                            # in case we have spurious/nonsense notes, filter them out
                            notes = filter(lambda n: n is not None, notes)
                            # log(" - %s: found notes: %s" % (slot.clip.name, notes))

                            self.clip_notes_cache[track_index][clip_index] = notes
                        else:
                            self.clip_notes_cache[track_index][clip_index] = None
                            slot.clip.muted = False
            log("filtered clips (took %.3fs)" % (time.time() - t0))
        except Exception, e:
            log("Exception: %s" % e)

    def soloTrackCB(self, msg, source):
        """Called when a /solo message is received.

        Messages:
        /solo     (int track)   Solos track number track
        """
        ty = msg[0] == '/return/solo' and 1 or 0
        track = msg[2]
        
        if len(msg) == 4:
            if msg[3] == 1:
                LiveUtils.soloTrack(track, ty)
            else:
                LiveUtils.unsoloTrack(track, ty)
            
        elif len(msg) == 3:
            if ty == 1:
                status = LiveUtils.getSong().return_tracks[track].solo
                self.oscEndpoint.send("/return/solo", (track, int(status)))
                
            else:
                status = LiveUtils.getTrack(track).solo
                self.oscEndpoint.send("/solo", (track, int(status)))
            
    def volumeCB(self, msg, source):
        """Called when a /volume message is received.

        Messages:
        /volume     (int track)                            Returns the current volume of track number track as: /volume (int track, float volume(0.0 to 1.0))
        /volume     (int track, float volume(0.0 to 1.0))  Sets track number track's volume to volume
        """
        if msg[0] == '/return/volume':
            ty = 1
        elif msg[0] == '/master/volume':
            ty = 2
        else:
            ty = 0
        
        if len(msg) == 2 and ty == 2:
            self.oscEndpoint.send("/master/volume", LiveUtils.getSong().master_track.mixer_device.volume.value)
        
        elif len(msg) == 3 and ty == 2:
            volume = float(msg[2])
            LiveUtils.getSong().master_track.mixer_device.volume.value = volume
        
        elif len(msg) == 4:
            track = int(msg[2])
            volume = float(msg[3])
            
            if ty == 0:
                LiveUtils.trackVolume(track, volume)
            elif ty == 1:
                LiveUtils.getSong().return_tracks[track].mixer_device.volume.value = volume

        elif len(msg) == 3:
            track = int(msg[2])

            if ty == 1:
                self.oscEndpoint.send("/return/volume", (track, LiveUtils.getSong().return_tracks[track].mixer_device.volume.value))
            
            else:
                self.oscEndpoint.send("/volume", (track, LiveUtils.trackVolume(track)))
            
    def panCB(self, msg, source):
        """Called when a /pan message is received.

        Messages:
        /pan     (int track)                            Returns the pan of track number track as: /pan (int track, float pan(-1.0 to 1.0))
        /pan     (int track, float pan(-1.0 to 1.0))    Sets track number track's pan to pan

        """
        if msg[0] == '/return/pan':
            ty = 1
        elif msg[0] == '/master/pan':
            ty = 2
        else:
            ty = 0
        
        if len(msg) == 2 and ty == 2:
            self.oscEndpoint.send("/master/pan", LiveUtils.getSong().master_track.mixer_device.panning.value)
        
        elif len(msg) == 3 and ty == 2:
            pan = msg[2]
            LiveUtils.getSong().master_track.mixer_device.panning.value = pan
            
        elif len(msg) == 4:
            track = msg[2]
            pan = msg[3]
            
            if ty == 0:
                LiveUtils.trackPan(track, pan)
            elif ty == 1:
                LiveUtils.getSong().return_tracks[track].mixer_device.panning.value = pan
            
        elif len(msg) == 3:
            track = msg[2]
            
            if ty == 1:
                self.oscEndpoint.send("/pan", (track, LiveUtils.getSong().return_tracks[track].mixer_device.panning.value))
            
            else:
                self.oscEndpoint.send("/pan", (track, LiveUtils.trackPan(track)))

            
    def sendCB(self, msg, source):
        """Called when a /send message is received.

        Messages:
        /send     (int track, int send)                              Returns the send level of send (send) on track number track as: /send (int track, int send, float level(0.0 to 1.0))
        /send     (int track, int send, float level(0.0 to 1.0))     Sets the send (send) of track number (track)'s level to (level)

        """
        ty = msg[0] == '/return/send' and 1 or 0
        track = msg[2]
        
        if len(msg) == 5:
            send = msg[3]
            level = msg[4]
            if ty == 1:
                LiveUtils.getSong().return_tracks[track].mixer_device.sends[send].value = level
            
            else:
                LiveUtils.trackSend(track, send, level)
        
        elif len(msg) == 4:
            send = msg[3]
            if ty == 1:
                self.oscEndpoint.send("/return/send", (track, send, float(LiveUtils.getSong().return_tracks[track].mixer_device.sends[send].value)))

            else:
                self.oscEndpoint.send("/send", (track, send, float(LiveUtils.trackSend(track, send))))
            
        elif len(msg) == 3:
            if ty == 1:
                sends = LiveUtils.getSong().return_tracks[track].mixer_device.sends
            else:
                sends = LiveUtils.getSong().tracks[track].mixer_device.sends
                
            so = [track]
            for i in range(len(sends)):
                so.append(i)
                so.append(float(sends[i].value))
                
            if ty == 1:
                self.oscEndpoint.send("/return/send", tuple(so))
            else:
                self.oscEndpoint.send("/send", tuple(so))
                
        
            
    def pitchCB(self, msg, source):
        """Called when a /clip/pitch message is received.

        Messages:
        /pitch     (int track, int clip)                                               Returns the pitch of clip as: /clip/pitch (int track, int clip, int coarse(-48 to 48), int fine (-50 to 50))
        /pitch     (int track, int clip, int coarse(-48 to 48), int fine (-50 to 50))  Sets clip number clip in track number track's pitch to coarse / fine

        TODO: Unlike other callbacks, this does not include the track/pitch indices.

        """
        if len(msg) == 6:
            track = int(msg[2])
            clip = int(msg[3])
            coarse = msg[4]
            fine = msg[5]
            LiveUtils.clipPitch(track, clip, coarse, fine)
        if len(msg) ==4:
            track = int(msg[2])
            clip = int(msg[3])
            self.oscEndpoint.send("/pitch", LiveUtils.clipPitch(track, clip))

    def trackJump(self, msg, source):
        """Called when a /track/jump message is received.

        Messages:
        /track/jump     (int track, float beats)   Jumps in track's currently running session clip by beats
        """
        if len(msg) == 4:
            track = int(msg[2])
            beats = int(msg[3])
            track = LiveUtils.getTrack(track)
            track.jump_in_running_session_clip(beats)

    def trackInfoCB(self, msg, source):
        """Called when a /track/info message is received.

        Messages:
        /track/info     (int track)   Returns clip slot status' for all clips in a track in the form /track/info (tracknumber, armed  (clipnumber, state, length))
                                           [state: 1 = Has Clip, 2 = Playing, 3 = Triggered]
        """
        clipslots = LiveUtils.getClipSlots()
        
        new = []
        if len(msg) == 3:
            new.append(clipslots[msg[2]])
            tracknum = int(msg[2]) - 1
        else:
            new = clipslots
            tracknum = -1
        
        for track in new:
            tracknum = tracknum + 1
            clipnum = -1
            tmptrack = LiveUtils.getTrack(tracknum)
            foldable = tmptrack.is_foldable and 1 or 0
            armed = (not foldable and tmptrack.arm) and 1 or 0
            li = [tracknum, foldable, armed]
            for clipSlot in track:
                clipnum = clipnum + 1
                li.append(clipnum);
                if clipSlot.clip != None:
                    clip = clipSlot.clip
                    if clip.is_playing == 1:
                        li.append(2)
                        li.append(clip.length)
                        
                    elif clip.is_triggered == 1:
                        li.append(3)
                        li.append(clip.length)
                        
                    else:
                        li.append(1)
                        li.append(clip.length)
                else:
                    li.append(0)
                    li.append(0.0)
                    
            tu = tuple(li)
            
            self.oscEndpoint.send("/track/info", tu)


    def undoCB(self, msg, source):
        """Called when a /undo message is received.
        
        Messages:
        /undo      Requests the song to undo the last action
        """
        LiveUtils.getSong().undo()
        
    def redoCB(self, msg, source):
        """Called when a /redo message is received.
        
        Messages:
        /redo      Requests the song to redo the last action
        """
        LiveUtils.getSong().redo()
        
    def playClipSlotCB(self, msg, source):
        """Called when a /clipslot/play message is received.
        
        Messages:
        /clipslot/play     (int track, int clip)   Launches clip number clip in track number track
        """
        if len(msg) == 4:
            track_num = int(msg[2])
            clip_num = int(msg[3])
            track = LiveUtils.getTrack(track_num)
            clipslot = track.clip_slots[clip_num]
            clipslot.fire()

    def viewSceneCB(self, msg, source):
        """Called when a /scene/view message is received.
        
        Messages:
        /scene/view     (int track)      Selects a scene to view
        """
        
        if len(msg) == 3:
            scene = int(msg[2])
            LiveUtils.getSong().view.selected_scene = LiveUtils.getSong().scenes[scene]
            
    def viewTrackCB(self, msg, source):
        """Called when a /track/view message is received.
        
        Messages:
        /track/view     (int track)      Selects a track to view
        """
        ty = msg[0] == '/return/view' and 1 or 0
        track_num = msg[2]
        
        if len(msg) == 3:
            if ty == 1:
                track = LiveUtils.getSong().return_tracks[track_num]
            else:
                track = LiveUtils.getSong().tracks[track_num]
                
            LiveUtils.getSong().view.selected_track = track
            Live.Application.get_application().view.show_view("Detail/DeviceChain")
                
            #track.view.select_instrument()
            
    def mviewTrackCB(self, msg, source):
        """Called when a /master/view message is received.
        
        Messages:
        /track/view     (int track)      Selects a track to view
        """
        track = LiveUtils.getSong().master_track

        LiveUtils.getSong().view.selected_track = track
        Live.Application.get_application().view.show_view("Detail/DeviceChain")        
        
        #track.view.select_instrument()
        
    def viewClipCB(self, msg, source):
        """Called when a /clip/view message is received.
        
        Messages:
        /clip/view     (int track, int clip)      Selects a track to view
        """
        track = LiveUtils.getSong().tracks[msg[2]]
        
        if len(msg) == 4:
            clip  = msg[3]
        else:
            clip  = 0

        Live.Application.get_application().view.focus_view("Session")

        Live.Application.get_application().view.hide_view("Browser")
        Live.Application.get_application().view.hide_view("Detail")

        LiveUtils.getSong().view.selected_track = track
        LiveUtils.getSong().view.highlighted_clip_slot = track.clip_slots[clip]
        
        #LiveUtils.getSong().view.detail_clip = track.clip_slots[clip].clip
        # Live.Application.get_application().view.show_view("Detail/Clip")

        self.oscEndpoint.send("/clip/highlighted", (msg[2], msg[3]))
        

    def detailViewCB(self, msg, source):
        """Called when a /detail/view message is received. Used to switch between clip/track detail

        Messages:
        /detail/view (int) Selects view where 0=clip detail, 1=track detail
        """
        if len(msg) == 3:
            if msg[2] == 0:
                Live.Application.get_application().view.show_view("Detail/Clip")
            elif msg[2] == 1:
                Live.Application.get_application().view.show_view("Detail/DeviceChain")

    def viewDeviceCB(self, msg, source):
        """Called when a /track/device/view message is received.
        
        Messages:
        /track/device/view     (int track)      Selects a track to view
        """
        ty = msg[0] == '/return/device/view' and 1 or 0
        track_num = int(msg[2])
        
        if len(msg) == 4:
            if ty == 1:
                track = LiveUtils.getSong().return_tracks[track_num]
            else:
                track = LiveUtils.getSong().tracks[track_num]

            LiveUtils.getSong().view.selected_track = track
            LiveUtils.getSong().view.select_device(track.devices[msg[3]])
            Live.Application.get_application().view.show_view("Detail/DeviceChain")
            
    def mviewDeviceCB(self, msg, source):
        track = LiveUtils.getSong().master_track
        
        if len(msg) == 3:
            LiveUtils.getSong().view.selected_track = track
            LiveUtils.getSong().view.select_device(track.devices[msg[2]])
            Live.Application.get_application().view.show_view("Detail/DeviceChain")
        
    def overdubCB(self, msg, source):
        """Called when a /overdub message is received.
        
        Messages:
        /overdub     (int on/off)      Enables/disables overdub
        """        
        if len(msg) == 3:
            overdub = msg[2]
            LiveUtils.getSong().overdub = overdub

    def stateCB(self, msg, source):
        """Called when a /state is received.
        
        Messages:
        /state                    Returns the current tempo and overdub status
        """
        if len(msg) == 2 or (len(msg) == 3 and msg[2] == "query"):
            tempo = LiveUtils.getTempo()
            overdub = LiveUtils.getSong().overdub
            self.oscEndpoint.send("/state", (tempo, int(overdub)))
        
    def clipInfoCB(self,msg):
        """Called when a /clip/info message is received.
        
        Messages:
        /clip/info     (int track, int clip)      Gets the status of a single clip in the form  /clip/info (tracknumber, clipnumber, state)
                                                       [state: 1 = Has Clip, 2 = Playing, 3 = Triggered]
        """
        
        if len(msg) == 4:
            trackNumber = msg[2]
            clipNumber = msg[3]    
            
            clip = LiveUtils.getClip(trackNumber, clipNumber)
            
            playing = 0
            
            if clip != None:
                playing = 1
                
                if clip.is_playing == 1:
                    playing = 2
                elif clip.is_triggered == 1:
                    playing = 3

            self.oscEndpoint.send("/clip/info", (trackNumber, clipNumber, playing))
        
        return

    def muteClipCB(self, msg, source):
        """Called when a /clip/mute message is received.
        
        Messages:
        /clip/mute     (int track, int clip)      Selects a clip to mute.
        """
        # use LogServer.py to read logs
        # log("muting")
        trackNumber = msg[2]
        clipNumber = msg[3]
        
        clip = LiveUtils.getClip(trackNumber, clipNumber)
        log("clip is %s (vars %s)" % (clip, vars(clip)))
        if len(msg) == 5:
            muted = msg[4]
            clip.muted = bool(muted)
        else:
            self.oscEndpoint.send("/clip/mute", (trackNumber, clipNumber, int(clip.muted)))
        
    def deviceCB(self, msg, source):
        ty = msg[0] == '/return/device' and 1 or 0
        track = msg[2]
    
        if len(msg) == 4:
            device = msg[3]
            po = [track, device]
            
            if ty == 1:
                params = LiveUtils.getSong().return_tracks[track].devices[device].parameters
            else:
                params = LiveUtils.getSong().tracks[track].devices[device].parameters
    
            for i in range(len(params)):
                po.append(i)
                po.append(float(params[i].value))
                po.append(str(params[i].name))
            
            self.oscEndpoint.send(ty == 1 and "/return/device/allparam" or "/device/allparam", tuple(po))
    
        elif len(msg) == 5:
            device = msg[3]
            param  = msg[4]
            
            if ty == 1:
                p = LiveUtils.getSong().return_tracks[track].devices[device].parameters[param]
            else: 
                p = LiveUtils.getSong().tracks[track].devices[device].parameters[param]
        
            self.oscEndpoint.send(ty == 1 and "/return/device/param" or "/device/param", (track, device, param, p.value, str(p.name)))
    
    
        elif len(msg) == 6:
            device = msg[3]
            param  = msg[4]
            value  = msg[5]
        
            if ty == 1:
                LiveUtils.getSong().return_tracks[track].devices[device].parameters[param].value = value
            else:
                LiveUtils.getSong().tracks[track].devices[device].parameters[param].value = value

    def devicerangeCB(self, msg, source):
        ty = msg[0] == '/return/device/range' and 1 or 0
        track = msg[2]
    
        if len(msg) == 4:
            device = msg[3]
            po = [track, device]
            
            if ty == 1:
                params = LiveUtils.getSong().return_tracks[track].devices[device].parameters
            else:
                params = LiveUtils.getSong().tracks[track].devices[device].parameters
    
            for i in range(len(params)):
                po.append(i)
                po.append(params[i].min)
                po.append(params[i].max)
            
            self.oscEndpoint.send(ty == 1 and "/return/device/range" or "/device/range", tuple(po))
    
        elif len(msg) == 5:
            device = msg[3]
            param  = msg[4]
            
            if ty == 1:
                p = LiveUtils.getSong().return_tracks[track].devices[device].parameters[param]
            else: 
                p = LiveUtils.getSong().tracks[track].devices[device].parameters[param]
        
            self.oscEndpoint.send(ty == 1 and "/return/device/range" or "/device/range", (track, device, param, p.min, p.max))
                
    def devicelistCB(self, msg, source):
        ty = msg[0] == '/return/devicelist' and 1 or 0

        track = msg[2]
    
        if len(msg) == 3:
            do = [track]
            
            if ty == 1:
                devices = LiveUtils.getSong().return_tracks[track].devices
            else:
                devices = LiveUtils.getSong().tracks[track].devices
        
            for i in range(len(devices)):
                do.append(i)
                do.append(str(devices[i].name))
            
            self.oscEndpoint.send(ty == 1 and "/return/devicelist" or "/devicelist", tuple(do))

    def mdeviceCB(self, msg, source):
        if len(msg) == 3:
            device = msg[2]
            po = [device]
            
            params = LiveUtils.getSong().master_track.devices[device].parameters
    
            for i in range(len(params)):
                po.append(i)
                po.append(float(params[i].value))
                po.append(str(params[i].name))
            
            self.oscEndpoint.send("/master/device", tuple(po))
    
        elif len(msg) == 4:
            device = msg[2]
            param  = msg[3]
            
            p = LiveUtils.getSong().master_track.devices[device].parameters[param]
        
            self.oscEndpoint.send("/master/device", (device, param, p.value, str(p.name)))
    
        elif len(msg) == 5:
            device = msg[2]
            param  = msg[3]
            value  = msg[4]
        
            LiveUtils.getSong().master_track.devices[device].parameters[param].value = value

    def mdevicerangeCB(self, msg, source):
        if len(msg) == 3:
            device = msg[2]
            po = [device]
            
            params = LiveUtils.getSong().master_track.devices[device].parameters
    
            for i in range(len(params)):
                po.append(i)
                po.append(params[i].max)
                po.append(params[i].min)
            
            self.oscEndpoint.send("/master/device/range", tuple(po))
    
        elif len(msg) == 4:
            device = msg[2]
            param  = msg[3]
            
            p = LiveUtils.getSong().master_track.devices[device].parameters[param]
        
            self.oscEndpoint.send("/master/device/range", (device, param, p.min, p.max))
            
    def mdevicelistCB(self, msg, source):
        if len(msg) == 2 or (len(msg) == 3 and msg[2] == "query"):
            do = []
            devices = LiveUtils.getSong().master_track.devices
        
            for i in range(len(devices)):
                do.append(i)
                do.append(str(devices[i].name))
            
            self.oscEndpoint.send("/master/devicelist", tuple(do))            
            
            
    def crossfaderCB(self, msg, source):
        if len(msg) == 2 or (len(msg) == 3 and msg[2] == "query"):
            self.oscEndpoint.send("/master/crossfader", float(LiveUtils.getSong().master_track.mixer_device.crossfader.value))
        
        elif len(msg) == 3:
            val = msg[2]
            LiveUtils.getSong().master_track.mixer_device.crossfader.value = val


    def loopStateCB(self, msg, source):
        type = msg[0] == '/clip/loopstate_id' and 1 or 0
    
        trackNumber = msg[2]
        clipNumber = msg[3]
    
        if len(msg) == 4:
            if type == 1:
                self.oscEndpoint.send("/clip/loopstate", (trackNumber, clipNumber, int(LiveUtils.getClip(trackNumber, clipNumber).looping)))
            else:
                self.oscEndpoint.send("/clip/loopstate", (int(LiveUtils.getClip(trackNumber, clipNumber).looping)))    
        
        elif len(msg) == 5:
            loopState = msg[4]
            LiveUtils.getClip(trackNumber, clipNumber).looping =  loopState

    def loopStartCB(self, msg, source):
        type = msg[0] == '/clip/loopstart_id' and 1 or 0
        
        trackNumber = msg[2]
        clipNumber = msg[3]
    
        if len(msg) == 4:
            if type == 1:
                self.oscEndpoint.send("/clip/loopstart", (trackNumber, clipNumber, float(LiveUtils.getClip(trackNumber, clipNumber).loop_start)))    
            else:
                self.oscEndpoint.send("/clip/loopstart", (float(LiveUtils.getClip(trackNumber, clipNumber).loop_start)))    
    
        elif len(msg) == 5:
            loopStart = msg[4]
            LiveUtils.getClip(trackNumber, clipNumber).loop_start = loopStart
            
    def loopEndCB(self, msg, source):
        type = msg[0] == '/clip/loopend_id' and 1 or 0
    
        trackNumber = msg[2]
        clipNumber = msg[3]    
        if len(msg) == 4:
            if type == 1:
                self.oscEndpoint.send("/clip/loopend", (trackNumber, clipNumber, float(LiveUtils.getClip(trackNumber, clipNumber).loop_end)))
            else:
                self.oscEndpoint.send("/clip/loopend", (float(LiveUtils.getClip(trackNumber, clipNumber).loop_end)))    
        
        elif len(msg) == 5:
            loopEnd = msg[4]
            LiveUtils.getClip(trackNumber, clipNumber).loop_end =  loopEnd

    def quantizationCB(self, msg, source):
        if len(msg) == 2 or (len(msg) == 3 and msg[2] == "query"):
            self.oscEndpoint.send("/quantization", int(LiveUtils.getSong().clip_trigger_quantization))
        
        elif len(msg) == 3:
            LiveUtils.getSong().clip_trigger_quantization = msg[2]

    def distributeGroupsCB(self, msg, source):
        if len(msg) == 3:
            outputs = range(1, msg[2] + 1)
        else:
            outputs = range(1, 64)
        index = 0
        for track in LiveUtils.getTracks():
            if track.is_foldable:
                output = outputs[index]
                index = (index + 1) % len(outputs)
                log(" - rerouting group track %s (%d), current subrouting = %s" % (track, index, track.current_output_sub_routing))
                track.current_output_routing = "Ext. Out"
                track.current_output_sub_routing = str(output)
                track.mixer_device.sends[0].value = 1.0

    def playGroupSceneCB(self, msg, source):
        if len(msg) == 4:
            track_index = msg[2]
            clip_index = msg[3]
            tracks = LiveUtils.getTracks()
            group = tracks[track_index]
            if group.is_foldable:
                target_tracks = []
                for track in tracks[track_index+1:]:
                    if track.is_foldable:
                        break
                    else:
                        target_tracks.append(track)
                for index, track in enumerate(target_tracks):
                    for cindex, clipslot in enumerate(track.clip_slots[clip_index:]):
                        if clipslot.clip is None:
                            track.stop_all_clips()
                            break
                        elif not clipslot.clip.muted:
                            clipslot.fire()
                            break
            else:
                log("playGroupScene: Target is not a group (ID %d)" % track_index)
        else:
            log("playGroupScene: Too few args")
