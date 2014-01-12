audiospriter
============

Generates audio sprites in multiple formats with configurable sound levels

Example
===
Generate audiosprite 'testing1.mp4' and 'testing1.json' from 3 mp3 sources, 
lowering the volume on the 1st mp3 only

    import os
    from audiosprite import AudioSprite

    data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def run():
        sprite = AudioSprite('testclient')

        sprite.addAudio(os.path.join(data_dir, 'test1.mp3'))
        sprite.addAudio(os.path.join(data_dir, 'test3.mp3'))
        sprite.addAudio(os.path.join(data_dir, 'party.mp3'))
        sprite.changeFileVolume(os.path.join(data_dir, 'test1.mp3'), -3)
        sprite.save(data_dir, 'testing1', formats=['mp4'])
        print "Done."

    if __name__ == "__main__":
        import sys

        run()

Sample JSON file
===
After save() is called, the AudioSrite object will generate at least 2 files
- One audio sprite file for each specified audio format
- One data file containing JSON blob for programmatic control

    {
   "sounds":[
      {
         "rms":2060,
         "file":"data/bach.ogg",
         "max":10872,
         "max_amp":32768.0,
         "channels":1,
         "frame_rate":44100,
         "duration":3030,
         "frame_width":2,
         "start":0,
         "duration_sec":3.030204081632653,
         "dBFS":-12.015827145905645,
         "sample_width":2
      },
      {
         "rms":7383,
         "file":"data/test3.mp3",
         "max":32768,
         "max_amp":32768.0,
         "channels":1,
         "frame_rate":44100,
         "duration":8333,
         "frame_width":2,
         "start":3030,
         "duration_sec":8.333061224489796,
         "dBFS":-6.47217066537253,
         "sample_width":2
      },
      {
         "rms":951,
         "file":"data/party.mp3",
         "max":19008,
         "max_amp":32768.0,
         "channels":1,
         "frame_rate":44100,
         "duration":6583,
         "frame_width":2,
         "start":11363,
         "duration_sec":6.582857142857143,
         "dBFS":-15.37269418022304,
         "sample_width":2
      }
   ],
   "sprite_id":"testclient"
}
