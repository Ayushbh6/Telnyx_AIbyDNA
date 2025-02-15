class SoundfileMixer:
    def __init__(self, sound_files, default_sound, volume=1.0):
        self.sound_files = sound_files
        self.default_sound = default_sound
        self.volume = volume
        # ... additional initialization if any

    def set_parent(self, parent):
        # This method is required for pipeline linkage.
        self.parent = parent 