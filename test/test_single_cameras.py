import unittest
import numpy as np
from camio import Camera


options = {
    'src': 0,
    'name': 'webcam',
    'fps': None,
    'backgroundIsEnabled': True,
}


class TestSingleCamera(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestSingleCamera, self).__init__(*args, **kwargs)
        self.camera = Camera(**options)

    def test_camera(self):
        self.assertIsNotNone(self.camera, 'Is not a valid device!')

    def test_has_device(self):
        self.assertIsBoolean(self.camera.hasDevice())

    def test_background(self):
        background = self.camera.getBackground()
        if options['backgroundIsEnabled']:
            self.assertIs(background, np.ndarray, 'It is not a numpy array')
        else:
            self.assertIs(background, None, 'It is not a NoneType')


if __name__ == '__main__':
    unittest.main()
