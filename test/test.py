from functools import partial
import os
import unittest
import json
from tempfile import NamedTemporaryFile
from pydub import AudioSegment
from audiosprite import AudioSprite
from audiosprite.exceptions import (
        InvalidSource
)


data_dir = os.path.join(os.path.dirname(__file__), 'data')

class AudioSpriteTests(unittest.TestCase):

    def setUp(self):
        self.sprite = AudioSprite('test1')
        self.testout = 'sprite'

    def test_create(self):
        self.assertIsInstance(self.sprite, AudioSprite)

    def test_is_indexable(self):
        self.sprite.addAudio(os.path.join(data_dir, 'test1.mp3'))
        self.sprite.addAudio(os.path.join(data_dir, 'test2.mp3'))
        self.assertTrue(self.sprite[0]['seg'] == self.sprite._files[0]['seg'])
        self.assertTrue(self.sprite[1]['seg'] == self.sprite._files[1]['seg'])

    def test_find_index_by_path(self):
        self.sprite.addAudio(os.path.join(data_dir, 'test1.mp3'))
        self.sprite.addAudio(os.path.join(data_dir, 'test2.mp3'))
        self.assertEqual(self.sprite.findIndexOf(os.path.join(data_dir, 'test1.mp3')), 0)
        self.assertEqual(self.sprite.findIndexOf(os.path.join(data_dir, 'test2.mp3')), 1)

    def test_empty_file_list(self):
        self.assertTrue(len(self.sprite) == 0)

    def test_add_good_audio_saves_filepath(self):
        f = os.path.join(data_dir, 'test1.mp3')
        self.sprite.addAudio(f)
        self.assertTrue(self.sprite[0]['path'] == f)

    def test_add_good_audio_creates_audio_segment(self):
        f = os.path.join(data_dir, 'test1.mp3')
        self.sprite.addAudio(f)
        self.assertTrue(len(self.sprite[0]['seg']) > 0)

    def test_add_missing_audio_raises_exception(self):
        badPath = os.path.join(data_dir, 'idontexist.mp3')
        func = partial(self.sprite.addAudio, badPath)
        self.assertRaises(InvalidSource, func)

    def test_length_is_total_milliseconds(self):
        self.sprite.addAudio(os.path.join(data_dir, 'test1.mp3'))
        self.sprite.addAudio(os.path.join(data_dir, 'test2.mp3'))
        self.assertEqual(len(self.sprite), len(self.sprite[0]['seg']) + len(self.sprite[1]['seg']))

    def test_is_iterable(self):
        self.sprite.addAudio(os.path.join(data_dir, 'test1.mp3'))
        self.sprite.addAudio(os.path.join(data_dir, 'test2.mp3'))
        i = 0

        for f in self.sprite:
            i += 1
        self.assertEqual(i, 2)

    def test_save_supports_multiple_formats(self):
        self.sprite.addAudio(os.path.join(data_dir, 'bach.ogg'))
        self.sprite.addAudio(os.path.join(data_dir, 'test3.mp3'))
        outfile = os.path.join(data_dir, self.testout)

        self.assertTrue(self.sprite.save(data_dir, self.testout, formats=['mp4', 'ogg']))
        exported = AudioSegment.from_file(outfile + '.mp4', 'mp4')
        self.assertTrue(len(exported) > len(self.sprite[0]['seg']))
        exported = AudioSegment.from_file(outfile + '.ogg', 'ogg')
        self.assertTrue(len(exported) > len(self.sprite[0]['seg']))

    def test_save_generates_datafile(self):
        self.sprite.addAudio(os.path.join(data_dir, 'bach.ogg'))
        self.sprite.addAudio(os.path.join(data_dir, 'test3.mp3'))
        outfile = os.path.join(data_dir, self.testout)

        with NamedTemporaryFile('w+b') as tmp_file:
            self.assertTrue(self.sprite.save(data_dir, self.testout, formats=['ogg']))
            with open(outfile + '.json', 'r') as jsonfile:
                data = json.loads(jsonfile.read())
                self.assertEqual(data['sprite_id'], self.sprite._id)
                self.assertEqual(len(data['sounds']), 2)

    def test_assign_volume_to_single_file(self):
        fpath = os.path.join(data_dir, 'bach.ogg')
        self.sprite.addAudio(fpath)
        gain = self.sprite[0]['seg'].rms
        self.sprite.changeFileVolume(fpath, -2)
        self.assertTrue(self.sprite[0]['seg'].rms < gain)


if __name__ == "__main__":
    import sys

    if sys.version_info >= (3, 1):
        unittest.main(warnings="ignore")
    else:
        unittest.main()

