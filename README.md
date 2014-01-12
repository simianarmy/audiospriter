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

