import os
import json
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

    def __init__(self, id, data=None, *args, **kwargs):
        self._data = data
        self._files = []
        self._id = id

        super(AudioSprite, self).__init__(*args, **kwargs)

    def __len__(self):
        return sum(len(f['seg']) for f in self._files)
    
    def __iter__(self):
        return (self._files[i] for i in xrange(len(self._files)))

    def __getitem__(self, idx):
        return self._files[idx]

    def findIndexOf(self, path):
        return map(lambda f: f['path'], self).index(path)

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

    def changeFileVolume(self, file_path, volume_change):
        """
        Changes a single file's volume by volume_change (+ or -)
        Specify file by path
        @return new gain value, -1 if not found
        """
        idx = self.findIndexOf(file_path)
        if idx >= 0:
            self._files[idx]['seg'] = self._files[idx]['seg'] + volume_change
            return self._files[idx]['seg'].rms

        return -1

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
        fileBase = os.path.join(saveDir, outfile)

        if self._generateAudioSprite(fileBase, formats, bitrate, parameters, tags, id3v2_version): 
            return self._generateDataFile(fileBase)

        return False

    def _generateAudioSprite(self, fileBase, formats, bitrate, parameters, tags, id3v2_version):
        out = self._files[0]['seg']

        # concat all teh sounds!
        for f in self._files[1:]:
            out = out + f['seg']

        if (len(out) == 0):
            return False

        for fmt in formats:
            fname = os.path.join(fileBase + '.' + fmt)
            out.export(fname, format=fmt, bitrate=bitrate, parameters=parameters, tags=tags, id3v2_version=id3v2_version) 

        return True

    def _generateDataFile(self, fileBase):
        # generate the JSON data and write to file
        with open(fileBase + '.json', 'w') as outfile:
            json.dump(self._genSpriteData(), outfile)

        return True

    def _genSpriteData(self):
        data = {'sprite_id': self._id, 'sounds': []}
        start = 0

        for f in self._files:
            sound_data = self._getSoundData(f)
            data['start'] = start
            data['sounds'].append(sound_data)
            start += len(f['seg'])

        return data

    def _getSoundData(self, item):
        seg = item['seg']

        return {'file': item['path'], 
                'duration': len(seg),
                'duration_sec': seg.duration_seconds,
                'channels': seg.channels,
                'frame_rate': seg.frame_rate,
                'frame_width': seg.frame_width,
                'sample_width': seg.sample_width,
                'rms': seg.rms,
                #'dBFS': seg.dBFS,
                'max': seg.max,
                'max_amp': seg.max_possible_amplitude
                }

