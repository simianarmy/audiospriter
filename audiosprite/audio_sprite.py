import os
from pydub import AudioSegment

from .exceptions import (
        InvalidSource
)

class AudioSprite(object):
   
    """ Uses list of AudioSegment objects to maintain sprite
    """

    EXPORT_FORMATS = [
        'ogg', 'mp3', 'mp4'
    ]

    def __init__(self, data=None, *args, **kwargs):
        self._data = data
        self._files = []

        super(AudioSprite, self).__init__(*args, **kwargs)

    def __len__(self):
        return sum(len(f['seg']) for f in self._files)
    
    def __iter__(self):
        return (self._files[i] for i in xrange(len(self._files)))

    def addAudio(self, filePath):
        """ Main interface for adding audio to the sprite.
        Takes any audio format that ffmpeg supports
        """
        fileName, fileExtension = os.path.splitext(filePath)
        try:
            seg = AudioSegment.from_file(filePath, fileExtension[1:])
        except:
            raise InvalidSource("Invalid audio source: " + filePath)

        self._files.append({'seg': seg, 'path': filePath})


    def save(self, saveDir, outfile, formats=EXPORT_FORMATS, bitrate=None, parameters=None, tags=None, id3v2_version='4'):
        """ Generates audiosprite files and control data JSON file

        saveDir (string):
            Path to destination files

        outfile (string):
            destination filename (without extension)

        formats (list)
            Formats for destination audio file. ('mp3', 'mp4', 'ogg' or other ffmpeg/avconv supported files)

        bitrate (string)
            Bitrate used when encoding destination file. (128, 256, 312k...)

        parameters (string)
            Aditional ffmpeg/avconv parameters

        tags (dict)
            Set metadata information to destination files usually used as tags. ({title='Song Title', artist='Song Artist'})

        id3v2_version (string)
            Set ID3v2 version for tags. (default: '4')
        """
        out = self._files[0]['seg']

        # concat all teh sounds!
        for f in self._files[1:]:
            out = out + f['seg']

        if (len(out) == 0):
            return False

        for fmt in formats:
            fname = os.path.join(saveDir, outfile + '.' + fmt)
            print 'Saving to ' + fname
            out.export(fname, format=fmt, bitrate=bitrate, parameters=parameters, tags=tags, id3v2_version=id3v2_version) 

        return True
