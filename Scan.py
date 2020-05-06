
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
        self.sceneScanLengths = {}

    def makeID(self, stringLength=8):
        lettersAndDigits = string.ascii_letters + string.digits
        return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))

    def scanSession(self, msg, source):
        #/scenes                            Returns a series of all the scene names in the form /scene/name (int scene, string name)
        log("scanSession called")
        log(msg)
        songID = msg[2]
        self.addControlTrack()
        self.scanSongTracks(songID)
        self.scanScenes(songID)
        self.addControlClips(songID)
        return

    def scanSongs(self):
        songIDs = self.loadedSongs()
        self.oscEndpoint.sendMessage(OSC.OSCMessage("/session/songs/", songIDs))

    def addControlTrack(self):
        #check for LiveControl listener track
        firstTrack = LiveUtils.getTrack(0)
        if firstTrack.name != CONTROL_TRACK_IDENTIFIER:
            LiveUtils.getSong().create_midi_track(0)
            controlTrack = LiveUtils.getTrack(0)
            controlTrack.name = CONTROL_TRACK_IDENTIFIER
            controlTrack.mute = 1
   
    def addControlClips(self, songID):
        controlTrack = LiveUtils.getTrack(0)
        slotNumber = 0
        for slot in controlTrack.clip_slots:
            if not slot.has_clip:
                signature_denominator = LiveUtils.getSong().signature_denominator
                signature_numerator = LiveUtils.getSong().signature_numerator
                if slotNumber in self.sceneScanLengths.keys():
                    info = self.sceneScanLengths[slotNumber]
                    length = info['length']
                    signature_numerator = int(info['signature_numerator'])
                    signature_denominator = int(info['signature_denominator'])
                else:
                    length = 4.0
                slot.create_clip(length)
                slot.clip.signature_numerator = signature_numerator
                slot.clip.signature_denominator = signature_denominator
                slot.length = length
                slot.clip.name = CONTROL_CLIP_IDENTIFIER + " " + songID
            slotNumber = slotNumber + 1

    def loadedSongs(self):
        controlHashes = []
        controlTrack = LiveUtils.getTrack(0)
        for slot in controlTrack.clip_slots:
            log("hello")
            if slot.has_clip:
                slotName = slot.clip.name
                nameParts = slotName.split(CONTROL_CLIP_IDENTIFIER)
                for part in nameParts:                
                    songID = nameParts[1].strip()
                if not songID in controlHashes:
                    controlHashes.append(str(songID))
        return controlHashes


    """
    def scanTracks(self, msg, source):
        
        #cycle through the tracks for IDs
        trackBundle = OSC.OSCBundle()
        trackNumber = 0
        trackBundle.append(OSC.OSCMessage("/tracks/start"))
        for track in LiveUtils.getTracks():

            if (track.name.find(TRACK_IDENTIFIER) == -1):
                if trackNumber != 0:
                    scanID = TRACK_IDENTIFIER + self.makeID()
                    track.name = track.name + scanID

            trackType = 'MIDI' if track.has_midi_input else 'Audio'
            trackBundle.append(OSC.OSCMessage("/tracks", (trackNumber, str(track.name), str(trackType))))
            trackNumber = trackNumber + 1
        trackBundle.append(OSC.OSCMessage("/tracks/end"))
        self.oscEndpoint.sendMessage(trackBundle)
        return  
	"""
    def scanTracks(self, msg, source):
        #/tracks                  Returns a a series of all the track names in the form /track/name (int track, string name)
        trackNumber = 0
        bundle = OSC.OSCBundle()
        layoutID = self.makeID()
        bundle.append(OSC.OSCMessage("/layout/" + layoutID + "/start"))
        for track in LiveUtils.getTracks():
      	    trackType = 'MIDI' if track.has_midi_input else 'Audio'
            bundle.append(OSC.OSCMessage("/track/" + layoutID, (trackNumber, str(track.name), str(trackType))))
            trackNumber = trackNumber + 1

        bundle.append(OSC.OSCMessage("/layout/" + layoutID + "/end"))
        self.oscEndpoint.sendMessage(bundle)
        return

    def scanSongTracks(self, songID):
        
        trackNumber = 0
        bundle = OSC.OSCBundle()
        bundle.append(OSC.OSCMessage("/song/" + songID + "/layout/start"))
        for track in LiveUtils.getTracks():
            trackType = 'MIDI' if track.has_midi_input else 'Audio'
            bundle.append(OSC.OSCMessage("/song/" + songID + "/track/", (trackNumber, str(track.name), str(trackType))))
            trackNumber = trackNumber + 1

        bundle.append(OSC.OSCMessage("/song/" + songID + "/layout/end"))
        self.oscEndpoint.sendMessage(bundle)
        return

    def findLongestClip(self, sceneIndex):
        longestLength = 0.0
        signature_denominator = LiveUtils.getSong().signature_denominator
        signature_numerator = LiveUtils.getSong().signature_numerator
        scene = LiveUtils.getScene(int(sceneIndex))
        for slot in scene.clip_slots:
            if slot.clip != None:
                longestLength = slot.clip.length if slot.clip.length > longestLength else longestLength
                if slot.clip.length > longestLength:
                    longestLength = slot.clip.length
                    signature_numerator = slot.clip.signature_numerator
                    signature_denominator = slot.clip.signature_denominator
        if longestLength == 0.0:
            longestLength = 4.0
        
        return (longestLength, signature_numerator, signature_denominator)

    def scanScenes(self, songID):
        #cycle through the scenes for IDs
        
        sceneNumber = 0
        self.sceneScanLengths = {}
        sceneIDs = []
        #songID = makeID()
        self.oscEndpoint.sendMessage(OSC.OSCMessage("/song/" + songID + "/start/"))
        tempo = LiveUtils.getTempo()
        self.oscEndpoint.sendMessage(OSC.OSCMessage("/song/" + songID + "/tempo/", float(tempo)))
        numerator = LiveUtils.getNumerator()
        self.oscEndpoint.sendMessage(OSC.OSCMessage("/song/" + songID + "/numerator/", int(numerator)))
        denominator = LiveUtils.getDenominator()
        self.oscEndpoint.sendMessage(OSC.OSCMessage("/song/" + songID + "/denominator/", int(denominator)))
        #sceneBundle.append(OSC.OSCMessage("/scenes/start"))
        for scene in LiveUtils.getScenes():
            sceneArgs = {}
            sceneBundle = OSC.OSCBundle()
            sceneID = re.findall("(\#cS.{8})", scene.name)
            if (not sceneID):
                sceneID = SCENE_IDENTIFIER + self.makeID()
                sceneName = scene.name
                scene.name = scene.name + sceneID
            else:
                #sceneID = scene.name[idIndex:]
                try:
                    usedAlready = sceneIDs.index(sceneID)
                except ValueError: 
                    usedAlready = -1
                if usedAlready != -1:
                    sceneID = SCENE_IDENTIFIER + self.makeID()
                    sceneName = scene.name[:usedAlready]
                    scene.name = sceneName + newID
                    
            self.oscEndpoint.sendMessage(OSC.OSCMessage("/song/" + songID + "/scene/" + sceneID + "/start/"))
            sceneIDs.append(sceneID)
            length, signature_numerator, signature_denominator = self.findLongestClip(sceneNumber)
            sceneSignature = re.findall("\d+\/\d+", scene.name)
            if (sceneSignature):
                separator = sceneSignature[0].find('/')
                signature_numerator = int(sceneSignature[0][:separator])
                separator += 1
                signature_denominator = int(sceneSignature[0][separator:])
                #log(signature_denominator)
            self.sceneScanLengths[sceneNumber] = {'length':length, 'signature_numerator': signature_numerator, 'signature_denominator': signature_denominator}
            sceneBundle.append(OSC.OSCMessage("/song/" + songID + "/scene/" + sceneID + "/abletonIndex/", int(sceneNumber)))
            sceneBundle.append(OSC.OSCMessage("/song/" + songID + "/scene/" + sceneID + "/name/", str(scene.name)))
            sceneBundle.append(OSC.OSCMessage("/song/" + songID + "/scene/" + sceneID + "/tempo/", float(scene.tempo)))
            sceneBundle.append(OSC.OSCMessage("/song/" + songID + "/scene/" + sceneID + "/length/", float(length)))
            sceneBundle.append(OSC.OSCMessage("/song/" + songID + "/scene/" + sceneID + "/numerator/", int(signature_numerator)))
            sceneBundle.append(OSC.OSCMessage("/song/" + songID + "/scene/" + sceneID + "/denominator/", int(signature_denominator)))

            self.oscEndpoint.sendMessage(sceneBundle)
            self.oscEndpoint.sendMessage(OSC.OSCMessage("/song/" + songID + "/scene/" + sceneID + "/end/"))
            
            sceneNumber += 1
        self.oscEndpoint.sendMessage(OSC.OSCMessage("/song/" + songID + "/end/"))
        return

    def scanSceneClips(self, msg, source):
        
        scene = LiveUtils.getScene(int(msg[2]))
        oscEndpoint.sendMessage(OSC.OSCMessage("/clips/start"))
        slotNumber = 0
        for slot in scene.clip_slots:
            clipBundle = OSC.OSCBundle()
            clip = slot.clip
            scanID = CLIP_IDENTIFIER + self.makeID()
            if clip is None:
                # if there's no control clip in this slot let's add one
                if slotNumber == 0:
                    slot.create_clip(32.0)
                    slot.clip.name = "<!LC>" + scanID
            clip = slot.clip
            if clip is not None:
                clipBundle.append(OSC.OSCMessage("/clip/start"))
                if (clip.name.find(CLIP_IDENTIFIER) == -1):
                    clip.name = clip.name + scanID
                
                warping = True if clip.is_midi_clip else clip.warping
                arguments = (slotNumber, str(clip.name), int(clip.length), str(warping), str(clip.looping), int(clip.loop_start), int(clip.loop_end), int(clip.signature_numerator), int(clip.signature_denominator))
                clipBundle.append(OSC.OSCMessage("/clip", arguments))
                clipBundle.append(OSC.OSCMessage("/clip/end"))
                oscEndpoint.sendMessage(clipBundle)
                foundClip = True

            slotNumber = slotNumber + 1
        oscEndpoint.sendMessage(OSC.OSCMessage("/clips/end"))
        #self.oscEndpoint.send(clipBundle)
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


