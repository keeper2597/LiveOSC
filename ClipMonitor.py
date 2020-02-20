"""
    Here is dir(ClipMonitorObject):
    ['__doc__', '__init__', '__module__', 'clip_position', 'playMode', 'slot', 'slot_changed', 'track', 'trackID', 'triggers']
"""

import LiveUtils
from Logger import log


class ClipMonitor:
    

    triggers = {'self.fire_scene()':4.0}  # a dictionary of events we want to fire at certain distances from the end of the clip
    clip_listener = {}
    end_time = 0.0

    def __init__(self, trackID):
        
        self.trackID = trackID
        self.track = LiveUtils.getTrack(self.trackID)
        callback = lambda : self.slot_changed()
        self.track.add_playing_slot_index_listener(callback)
        self.playMode = 'next'
        log("Clip Monitor initialized on Track " + str(trackID))


    def slot_changed(self):
        slot_index = self.track.playing_slot_index
        self.playing_scene_index = slot_index
        #if slot_index == -2:  #no slot playing
        #log("Playing Slot Index: " + str(slot_index))

        #  CLEAN UP ANY OLD LISTENERS
        if len(self.clip_listener) > 0:
            for old_clip in self.clip_listener:
                if old_clip.playing_position_has_listener(self.clip_listener[old_clip]) == 1:
                    old_clip.remove_playing_position_listener(self.clip_listener[old_clip])
            self.clip_listener = {}
        
        #MAKE SURE WE HAVE A CLIP AND ASSIGN A PLAYING POSITION LISTENER TO IT
        slot = self.track.clip_slots[slot_index]
        if slot.has_clip:
    	    clip = slot.clip
            callback = lambda: self.playing_position()
            dir(clip)
            if self.clip_listener.has_key(clip) != 1:
                self.clip_listener[clip] = callback
                clip.add_playing_position_listener(callback)
                log(str(clip.name))
                self.active_triggers = self.triggers.copy()
        else:
            log("No Clip Playing in Track " + str(self.trackID))
            self.clip_listener = {}


    def playing_position(self):
        for clip in self.clip_listener:
            if len(self.triggers) > 0:
                for trigger in list(self.active_triggers):
                    if clip.loop_end <= (clip.playing_position + self.active_triggers[trigger]):
                        del self.active_triggers[trigger]
                        log(str(trigger))
                        eval(str(trigger))

    def fire_scene(self):
        if self.playMode == 'next':
            next_index = int(self.playing_scene_index) + 1
            LiveUtils.getScene(next_index).fire()



