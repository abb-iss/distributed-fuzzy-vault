"""
    Minutiae Extractor to get Minutia from files (fingerprint templates)
"""


from Minutia import MinutiaNBIS


class MinutiaeExtractor:
    NBIS_FORMAT = 1

    def __init__(self, extractor_format=NBIS_FORMAT):
        self.extractor_type = extractor_format

    def extract_minutiae_from_xyt(self, file_path):
        """ Extracts minutiae from a fingerprint .xyt file
        :returns a list of Minutia with descending order of quality """

        minutiae_list = []
        with open(file_path, 'r') as file:
            for line in file:
                x, y, theta, quality = line.split(' ')
                minutia = MinutiaNBIS(int(x), int(y), int(theta), int(quality))
                minutiae_list.append(minutia)
        # sort list according to quality of minutiae
        minutiae_list.sort(key=lambda m: int(m.quality), reverse=True)
        return minutiae_list
