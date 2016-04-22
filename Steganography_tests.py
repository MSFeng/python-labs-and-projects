from os.path import join
import unittest
from numpy import ndarray as nmat
from scipy.misc import *
from Steganography import *


class ImageAssertion:
    """
    Provides a convenience method for comparing two images.
    """
    @staticmethod
    def assertImageEqual(img1, img2):

        if not isinstance(img1, nmat) or not isinstance(img2, nmat):
            raise AssertionError("One or more of the input parameters are not valid images.")

        if img1.shape != img2.shape:
            raise AssertionError("Image Shapes does not match.")

        if not np.all(img1 == img2):
            raise AssertionError("Images do not match.")


class SteganographyTestSuite(unittest.TestCase, ImageAssertion):

    folder = "test_images"

    @staticmethod
    def getXML(path):

        with open(path, "r") as xFile:
            content = xFile.read()

        return content

    def test_PayloadBadInitializer(self):

        with self.subTest(key="Bad Image"):
            img = [[1, 1], [0, 0]]
            self.assertRaises(TypeError, Payload, img)

        with self.subTest(key="Bad XML"):
            self.assertRaises(TypeError, Payload, xml=3.2)

        with self.subTest(key="Missing Parameters"):
            self.assertRaises(ValueError, Payload)

        with self.subTest(key="Bad Compression"):
            img = imread(join(self.folder, "dummy.png"))
            self.assertRaises(ValueError, Payload, img=img, compressionLevel=10)

    def test_PayloadWithImage(self):

        with self.subTest(key="Color Image 1"):
            img = imread(join(self.folder, "payload1.png"))
            expectedValue = self.getXML(join(self.folder, "payload1_0.xml"))
            actualValue = Payload(img, 0).xml

            self.assertMultiLineEqual(expectedValue, actualValue)

        with self.subTest(key="Color Image 2"):
            img = imread(join(self.folder, "payload1.png"))
            expectedValue = self.getXML(join(self.folder, "payload1_9.xml"))
            actualValue = Payload(img, 9).xml

            self.assertMultiLineEqual(expectedValue, actualValue)

        with self.subTest(key="Gray Image 1"):
            img = imread(join(self.folder, "payload2.png"))
            expectedValue = self.getXML(join(self.folder, "payload2_-1.xml"))
            actualValue = Payload(img).xml

            self.assertMultiLineEqual(expectedValue, actualValue)

        with self.subTest(key="Gray Image 2"):
            img = imread(join(self.folder, "payload2.png"))
            expectedValue = self.getXML(join(self.folder, "payload2_9.xml"))
            actualValue = Payload(img, 9).xml

            self.assertMultiLineEqual(expectedValue, actualValue)

    def test_PayloadWithXML(self):

        with self.subTest(key="Color Image 1"):
            xml = self.getXML(join(self.folder, "payload1_-1.xml"))
            expectedValue = imread(join(self.folder, "payload1.png"))
            actualValue = Payload(xml=xml).img

            self.assertImageEqual(expectedValue, actualValue)

        with self.subTest(key="Color Image 2"):
            xml = self.getXML(join(self.folder, "payload1_9.xml"))
            expectedValue = imread(join(self.folder, "payload1.png"))
            actualValue = Payload(xml = xml).img

            self.assertImageEqual(expectedValue, actualValue)

        with self.subTest(key="Gray Image 1"):
            xml = self.getXML(join(self.folder, "payload2_-1.xml"))
            expectedValue = imread(join(self.folder, "payload2.png"))
            actualValue = Payload(xml = xml).img

            self.assertImageEqual(expectedValue, actualValue)

        with self.subTest(key="Gray Image 2"):
            xml = self.getXML(join(self.folder, "payload2_9.xml"))
            expectedValue = imread(join(self.folder, "payload2.png"))
            actualValue = Payload(xml = xml).img

            self.assertImageEqual(expectedValue, actualValue)

    def test_CarrierInitializerAndValidation(self):

        with self.subTest(key="Initializer Check"):
            img = [[1, 1], [0, 0]]
            self.assertRaises(TypeError, Carrier, img)

        with self.subTest(key="Invalid Extraction"):
            c = Carrier(imread(join(self.folder, "carrier1.png")))

            self.assertRaises(Exception, c.extractPayload)

    def test_CarrierImmutability(self):

        with self.subTest(key="After Cleaning"):
            img = imread(join(self.folder, "carrier1.png"))
            ref = img.copy()
            c = Carrier(img)
            c.clean()

            self.assertImageEqual(ref, c.img)

        with self.subTest(key="After Embedding"):
            img = imread(join(self.folder, "carrier1.png"))
            ref = img.copy()
            c = Carrier(img)
            p = Payload(imread(join(self.folder, "payload1.png")))
            c.embedPayload(p)

            self.assertImageEqual(ref, c.img)

        with self.subTest(key="After Extraction"):
            img = imread(join(self.folder, "result1.png"))
            ref = img.copy()
            c = Carrier(img)
            c.extractPayload()

            self.assertImageEqual(ref, c.img)

    def test_CarrierCheckingForPayload(self):

        with self.subTest(key="No Payload in Color"):
            img = imread(join(self.folder, "result7.png"))
            c = Carrier(img)
            actualValue = c.payloadExists()

            self.assertFalse(actualValue)

        with self.subTest(key="No Payload in Gray"):
            img = imread(join(self.folder, "result8.png"))
            c = Carrier(img)
            actualValue = c.payloadExists()

            self.assertFalse(actualValue)

        with self.subTest(key="Payload in Color"):
            img = imread(join(self.folder, "result1.png"))
            c = Carrier(img)
            actualValue = c.payloadExists()

            self.assertTrue(actualValue)

        with self.subTest(key="Payload in Gray"):
            img = imread(join(self.folder, "result3.png"))
            c = Carrier(img)
            actualValue = c.payloadExists()

            self.assertTrue(actualValue)

    def test_CarrierCleaning(self):

        with self.subTest(key="Cleaning Color 1"):
            img = imread(join(self.folder, "carrier1.png"))
            expectedValue = imread(join(self.folder, "result5.png"))
            actualValue = Carrier(img).clean()

            self.assertImageEqual(expectedValue, actualValue)

        with self.subTest(key="Cleaning Color 2"):
            img = imread(join(self.folder, "result2.png"))
            expectedValue = imread(join(self.folder, "result7.png"))
            actualValue = Carrier(img).clean()

            self.assertImageEqual(expectedValue, actualValue)

        with self.subTest(key="Cleaning Gray 1"):
            img = imread(join(self.folder, "carrier2.png"))
            expectedValue = imread(join(self.folder, "result6.png"))
            actualValue = Carrier(img).clean()

            self.assertImageEqual(expectedValue, actualValue)

        with self.subTest(key="Cleaning Gray 2"):
            img = imread(join(self.folder, "result3.png"))
            expectedValue = imread(join(self.folder, "result8.png"))
            actualValue = Carrier(img).clean()

            self.assertImageEqual(expectedValue, actualValue)

    def test_CarrierEmbeddingValidation(self):

        with self.subTest(key="Incorrect Parameter"):
            img = imread(join(self.folder, "dummy.png"))
            c = Carrier(imread(join(self.folder, "carrier1.png")))

            self.assertRaises(TypeError, c.embedPayload, payload=img)

        with self.subTest(key="Payload Exists"):
            p = Payload(imread(join(self.folder, "payload1.png")), 9)
            c = Carrier(imread(join(self.folder, "result1.png")))

            self.assertRaises(Exception, c.embedPayload, payload=p)

        with self.subTest(key="Very Large Payload"):
            p = Payload(imread(join(self.folder, "payload1.png")), 9)
            c = Carrier(imread(join(self.folder, "carrier2.png")))

            self.assertRaises(ValueError, c.embedPayload, payload=p)

    def test_CarrierEmbedding(self):

        with self.subTest(key="Color in Color"):
            p = Payload(imread(join(self.folder, "payload1.png")), 9)
            c = Carrier(imread(join(self.folder, "carrier1.png")))

            expectedValue = imread(join(self.folder, "result1.png"))
            actualValue = c.embedPayload(p)

            self.assertImageEqual(expectedValue, actualValue)

        with self.subTest(key="Gray in Color"):
            p = Payload(imread(join(self.folder, "payload2.png")), 9)
            c = Carrier(imread(join(self.folder, "result1.png")))

            expectedValue = imread(join(self.folder, "result2.png"))
            actualValue = c.embedPayload(p, True)

            self.assertImageEqual(expectedValue, actualValue)

        with self.subTest(key="Color in Gray"):
            p = Payload(imread(join(self.folder, "payload3.png")), 9)
            c = Carrier(imread(join(self.folder, "result4.png")))

            expectedValue = imread(join(self.folder, "result3.png"))
            actualValue = c.embedPayload(p, True)

            self.assertImageEqual(expectedValue, actualValue)

        with self.subTest(key="Gray in Gray"):
            p = Payload(imread(join(self.folder, "payload4.png")), 9)
            c = Carrier(imread(join(self.folder, "carrier2.png")))

            expectedValue = imread(join(self.folder, "result4.png"))
            actualValue = c.embedPayload(p)

            self.assertImageEqual(expectedValue, actualValue)

    def test_CarrierExtraction(self):

        with self.subTest(key="Color in Color"):
            c = Carrier(imread(join(self.folder, "result1.png")))

            expectedValue = imread(join(self.folder, "payload1.png"))
            actualValue = c.extractPayload().img

            self.assertImageEqual(expectedValue, actualValue)

        with self.subTest(key="Gray in Color"):
            c = Carrier(imread(join(self.folder, "result2.png")))

            expectedValue = imread(join(self.folder, "payload2.png"))
            actualValue = c.extractPayload().img

            self.assertImageEqual(expectedValue, actualValue)

        with self.subTest(key="Color in Gray"):
            c = Carrier(imread(join(self.folder, "result3.png")))

            expectedValue = imread(join(self.folder, "payload3.png"))
            actualValue = c.extractPayload().img

            self.assertImageEqual(expectedValue, actualValue)

        with self.subTest(key="Gray in Gray"):
            c = Carrier(imread(join(self.folder, "result4.png")))

            expectedValue = imread(join(self.folder, "payload4.png"))
            actualValue = c.extractPayload().img

            self.assertImageEqual(expectedValue, actualValue)


if __name__ == '__main__':
    unittest.main(warnings='ignore')
