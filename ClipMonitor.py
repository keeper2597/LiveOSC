"""
    Here is dir(ClipMonitorObject):
    ['__doc__', '__init__', '__module__', 'clip_position', 'playMode', 'slot', 'slot_changed', 'track', 'trackID', 'triggers']
"""

import LiveUtils
from Logger import log


class ClipMonitor:
    

    triggers = {'bang':12.0}  # a dictionary of events we want to fire at certain distances from the end of the clip
    clip_listener = {}
    end_time = 0.0

    def __init__(self, trackID):
        
        self.trackID = trackID
        self.track = LiveUtils.getTrack(self.trackID)
        callback = lambda : self.slot_changed()
        self.track.add_playing_slot_index_listener(callback)
        self.playMode = 'next'
        log("Clip Monitor initialized on track " + str(trackID))

    def clip_position(self, clip, tid, cid):
        if clip.is_playing:
        	print("clip is playing")
            #self.oscEndpoint.send('/live/clip/position', (tid, cid, clip.playing_position, clip.length, clip.loop_start, clip.loop_end))

    def slot_changed(self):
        slot_index = self.track.playing_slot_index
        #if slot_index == -2:  #no slot playing
        log("Playing Slot Index: " + str(slot_index))
        if len(self.clip_listener) > 0:
            for old_clip in self.clip_listener:
                if old_clip.playing_position_has_listener(self.clip_listener[old_clip]) == 1:
                    old_clip.remove_playing_position_listener(self.clip_listener[old_clip])
            self.clip_listener = {}
        
        slot = self.track.clip_slots[slot_index]
        if slot.has_clip:
    	    clip = slot.clip
            callback = lambda: self.playing_position()
            dir(clip)
            if self.clip_listener.has_key(clip) != 1:
                self.clip_listener[clip] = callback
                clip.add_playing_position_listener(callback)
                log(str(clip.name))
        else:
            log("no clip playing")
            self.clip_listener = {}

    def playing_position(self):
        for clip in self.clip_listener:
            if len(self.triggers) > 0:
                for trigger in list(self.triggers):
                    if clip.loop_end <= (clip.playing_position + self.triggers[trigger]):
                        del self.triggers[trigger]
                        log(str(trigger))