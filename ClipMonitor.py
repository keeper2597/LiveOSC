

import LiveUtils
from Logger import log

# playMode gives us a chace to change the behavior when triggers are fired
# referenced in ClipMonitor.fire_scene()
playMode = "next"

# a dictionary of events we want to fire at certain distances from the end of the clip
triggers = {'self.fire_scene()':4.0, 'self.cue_count()':5.0}  

debug = LiveUtils.debug

class ClipMonitor:
    
    clip_listener = {}
    trackID = 0

    
    def __init__(self, trackID):
        self.trackID = trackID

        self.track = LiveUtils.getTrack(self.trackID)

        callback = lambda : self.slot_changed()

        # make sure we get notified whenever a new clip starts playing by putting a listener on the Track
        self.track.add_playing_slot_index_listener(callback)

        log("Clip Monitor initialized on Track " + str(self.trackID))


        # slot_changed() is called whenever the playing_slot_index changes (see __init__)
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
                #copy the triggers onto the clip we're watching
                self.active_triggers = triggers.copy()
        else:
            log("No Clip Playing in Track " + str(self.trackID))
            self.clip_listener = {}



    def playing_position(self):
        for clip in self.clip_listener:
            #check to see if we have triggers
            if len(triggers) > 0:
                for trigger in list(self.active_triggers):
                    #check to see if we're close enough to the end to fire it
                    if clip.loop_end <= (clip.playing_position + self.active_triggers[trigger]):
                        #if we fired the trigger, get rid of it so it doesn't go again
                        del self.active_triggers[trigger]
                        log(str(trigger))
                        #call the function named in the trigger
                        eval(str(trigger))


    def fire_scene(self):
        if debug:
            log("PlayMode: " + str(playMode))
        if playMode == 'next':
            next_index = int(self.playing_scene_index) + 1
            LiveUtils.getScene(next_index).fire()
        elif playMode == 'repeat':
            LiveUtils.getScene(self.playing_scene_index).fire()

    def cue_count(self):
        if debug:
            log("Cue Count Triggered ")


