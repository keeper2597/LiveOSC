
import Live
import RemixNet
import OSC
import LiveUtils
import sys
import re
import time
import string
import random

from Logger import log


debug = LiveUtils.debug

LIVE_CONTROL_TRACK = 0
SCENE_IDENTIFIER = " #cS"
TRACK_IDENTIFIER = " #cT"
CLIP_IDENTIFIER = " #cC"
CONTROL_TRACK_IDENTIFIER = "<!LCONTROL>"
CONTROL_CLIP_IDENTIFIER = "<!LC>"


class Scan:
    def __init__(self, oscEndpoint):
        self.oscEndpoint = oscEndpoint

    def makeID(self, stringLength=4):
        lettersAndDigits = string.ascii_letters + string.digits
        return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))

    def scanSession(self, msg, source):
        #/scan/scenes                            Returns a a series of all the scene names in the form /scene/name (int scene, string name)
        log("scanSession called")
        self.addControlTrack(msg, source)
        self.scanScenes(msg, source)
        return

    def addControlTrack(self, msg, source):
    	#check for LiveControl listener track
        firstTrack = LiveUtils.getTrack(0)
        if firstTrack.name != CONTROL_TRACK_IDENTIFIER:
            LiveUtils.getSong().create_midi_track(0)
            controlTrack = LiveUtils.getTrack(0)
            controlTrack.name = CONTROL_TRACK_IDENTIFIER
            controlTrack.mute = 1
            for slot in controlTrack.clip_slots:
                if not slot.has_clip:
                    slot.create_clip(32.0)
                    slot.clip.name = CONTROL_CLIP_IDENTIFIER

    """
    def scanTracks(self, msg, source):
        
        #cycle through the tracks for IDs
        trackBundle = OSC.OSCBundle()
        trackNumber = 0
        trackBundle.append(OSC.OSCMessage("/scan/tracks/start"))
        for track in LiveUtils.getTracks():

            if (track.name.find(TRACK_IDENTIFIER) == -1):
                if trackNumber != 0:
                    scanID = TRACK_IDENTIFIER + self.makeID()
                    track.name = track.name + scanID

            trackType = 'MIDI' if track.has_midi_input else 'Audio'
            trackBundle.append(OSC.OSCMessage("/scan/tracks", (trackNumber, str(track.name), str(trackType))))
            trackNumber = trackNumber + 1
        trackBundle.append(OSC.OSCMessage("/scan/tracks/end"))
        self.oscEndpoint.sendMessage(trackBundle)
        return  
	"""

    def scanTracks(self, msg, source):
        #/scan/tracks                  Returns a a series of all the track names in the form /track/name (int track, string name)
        trackNumber = 0
        bundle = OSC.OSCBundle()
        bundle.append(OSC.OSCMessage("scan/tracks/start"))
        for track in LiveUtils.getTracks():
        	trackType = 'MIDI' if track.has_midi_input else 'Audio'
            bundle.append("/scan/layout", (trackNumber, str(track.name), str(trackType)))
            trackNumber = trackNumber + 1
        bundle.append(OSC.OSCMessage("scan/tracks/end"))
        self.oscEndpoint.sendMessage(bundle)
        return  


    def scanScenes(self, msg, source):
        #cycle through the scenes for IDs
        sceneBundle = OSC.OSCBundle()
        sceneNumber = 0
        sceneIDs = []
        sceneBundle.append(OSC.OSCMessage("/scan/scenes/start"))
        for scene in LiveUtils.getScenes():

            idIndex = scene.name.find(SCENE_IDENTIFIER)
            if idIndex == -1:
                sceneID = SCENE_IDENTIFIER + self.makeID()
                sceneName = scene.name
                scene.name = scene.name + sceneID
            else:
                sceneID = scene.name[idIndex:]
                try:
                    usedAlready = sceneIDs.index(sceneID)
                except ValueError: 
                    usedAlready = -1
                if usedAlready != -1:
                    newID = SCENE_IDENTIFIER + self.makeID()
                    sceneName = scene.name[:idIndex]
                    scene.name = sceneName + newID
                else:
                    sceneIDs.append(sceneID)



            sceneBundle.append(OSC.OSCMessage("/scan/scenes", (sceneNumber, str(scene.name), scene.tempo)))
            #self.oscEndpoint.send("/scan/scenes", (sceneNumber, str(sceneName), sceneID, scene.tempo))

            
            if sceneNumber > 30:
                sceneNumber = 0
                self.oscEndpoint.sendMessage(sceneBundle)
                sceneBundle = OSC.OSCBundle()
            else:
                sceneNumber = sceneNumber + 1

        #fullBundle.append(sceneBundle)
        sceneBundle.append(OSC.OSCMessage("/scan/scenes/end"))
        self.oscEndpoint.sendMessage(sceneBundle)
        return


    def scanSceneClips(self, msg, source):
    	
    	scene = LiveUtils.getScene(int(msg[2]))

        clipBundle = OSC.OSCBundle()
        clipBundle.append(OSC.OSCMessage("/scan/clips/start"))
        slotNumber = 0
        for slot in scene.clip_slots:
            clip = slot.clip
            scanID = CLIP_IDENTIFIER + self.makeID()
            if clip is None:
            	# if there's no control clip in this slot let's add one
                if slotNumber == 0:
                    slot.create_clip(32.0)
                    slot.clip.name = "<!LC>" + scanID
            clip = slot.clip
            if clip is not None:
                if (clip.name.find(CLIP_IDENTIFIER) == -1):
                    clip.name = clip.name + scanID
                
                warping = True if clip.is_midi_clip else clip.warping
                arguments = (slotNumber, str(clip.name), int(clip.length), str(warping), str(clip.looping), int(clip.loop_start), int(clip.loop_end), int(clip.signature_numerator), int(clip.signature_denominator))
                clipBundle.append(OSC.OSCMessage("/scan/clips", arguments))
                foundClip = True

            slotNumber = slotNumber + 1
        clipBundle.append(OSC.OSCMessage("/scan/clips/end"))
        self.oscEndpoint.send(clipBundle)
        return


 # proof of concept to duplicate scenes and move them into separate scenes
        """i = 0
        while i < 10:
            sceneToGet = i + 4
            scene = LiveUtils.getSong().duplicate_scene(sceneToGet)
            newScene = LiveUtils.getScene(sceneToGet + 1)
            for slot in newScene.clip_slots:
                #log(slot.has_clip)
                if slot.has_clip:
                    newStart = slot.clip.start_marker + 2.0
                    if newStart >= slot.clip.end_marker:
                        newStart = slot.clip.end_marker - 2.0
                    slot.clip.start_marker = newStart
            i += 1
        """

