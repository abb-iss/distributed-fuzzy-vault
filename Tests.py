"""
    Module for tests
"""

from bitstring import BitArray
import binascii
from itertools import permutations
import datetime

from Polynomial_Extractor import PolynomialExtractor
from Polynomial_Generator import PolynomialGenerator
import Vault_Verifier
from Minutia import *
from Minutiae_Extractor import MinutiaeExtractor
from Geometric_Hashing_Transformer import GHTransformer
import Constants
from Minutia_Converter import MinutiaConverter

now = datetime.datetime.now()

GALLERY_IMAGE = '2_6'
PROBE_IMAGE = '4_2'
XYT_GALLERY_PATH = 'input_images/' + 'FVC2006_DB_2B/' + GALLERY_IMAGE + '.xyt'
XYT_PROBE_PATH = 'input_images/' + 'FVC2006_DB_2B/' + PROBE_IMAGE + '.xyt'
POLY_DEGREE = 12
SECRET = "SECRET..."
GF_2_M = 32
CRC_LENGTH = 32
SECRET_LENGTH = len(SECRET.encode()) * 8
MINUTIAE_OUT_FILE = 'out/minutiae_out_basis_{}_vs_{}_{}_{}.csv'.format(
    PROBE_IMAGE, GALLERY_IMAGE, now.strftime("%Y%m%d"), now.strftime("%H%M")
)


def test_ideal_secret_length(len_poly, len_crc):
    for x in range(1000):
        if (x + len_crc) % (len_poly + 1) == 0 and x % 8 == 0:
            print(x)


def test_secret_length():
    secret_original_bytes = SECRET.encode()
    secret_original_bit = BitArray(bytes=secret_original_bytes, length=len(secret_original_bytes) * 8)
    print(len(secret_original_bit))


def test_bitstring_extraction():
    secret_bytes = SECRET.encode()
    secret_bit = BitArray(bytes=secret_bytes, length=len(secret_bytes) * 8)
    print(secret_bit.bin)
    print("Length of bits original secret: %d" % len(secret_bit))

    checksum_bit = BitArray(uint=binascii.crc32(secret_bit.bytes), length=CRC_LENGTH)
    print(checksum_bit.bin)
    print(len(checksum_bit))

    # join secret bitstring with CRC
    total_bit = secret_bit.copy()
    total_bit.append(checksum_bit)
    print('Length total bit: {}'.format(len(total_bit)))

    coefficients = []
    assert len(total_bit) % 13 == 0
    step = int(len(total_bit) / 13)
    for i in range(0, len(total_bit), step):
        coefficients.append(total_bit[i:i + step].uint)
    print(coefficients)
    PolynomialExtractor.check_crc_in_poly(coefficients, POLY_DEGREE, CRC_LENGTH)

    poly = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 83, 69, 67, 82, 69, 84, 46, 46, 46, 201, 112, 67, 73]
    print(PolynomialExtractor.check_crc_in_poly(poly, POLY_DEGREE, CRC_LENGTH))


def test_combinations():
    l = list(range(10))
    combinations(l, 4)


def combinations(iterable, r):
    pool = tuple(iterable)
    n = len(pool)
    for indices in permutations(range(n), r):
        if sorted(indices) == list(indices):
            print(tuple(pool[i] for i in indices))


def generate_basis_transformed_tuples(xyt_path):
    """
    :param xyt_path: fingerprint probe image
    :returns: list of minutiae tuple (basis count [int], basis [Minutia], minutia [Minutia])
    """
    nbis_minutiae_extractor = MinutiaeExtractor()
    minutiae_list = nbis_minutiae_extractor.extract_minutiae_from_xyt(xyt_path)[0:Constants.MINUTIAE_POINTS_AMOUNT]
    minutiae_list_gh = []
    for m in minutiae_list:
        minutiae_list_gh.append(MinutiaNBIS_GH.convert_from_MinutiaNBIS(m))
    all_minutiae_list = []
    for cnt_basis, basis in enumerate(minutiae_list_gh, 1):
        for m in GHTransformer.transform_minutiae_to_basis(basis, minutiae_list_gh):
            all_minutiae_list.append((cnt_basis, basis, m))
    return all_minutiae_list


def write_probe_vs_gallery(probe_xyt_path, gallery_xyt_path, out_file):
    write_basis_minutiae_header(out_file)
    gallery_tuples = generate_basis_transformed_tuples(gallery_xyt_path)
    probe_tuples = generate_basis_transformed_tuples(probe_xyt_path)
    for i, probe_tuple in enumerate(probe_tuples, 1):
        print('Probe tuple: {}'.format(i))
        probe_minutia = probe_tuple[2]
        probe_string = generate_print_string_tuple(probe_tuple)
        if probe_minutia.is_zero():
            continue
        match = False
        print_string = probe_string
        for gallery_tuple in gallery_tuples:
            gallery_minutia = gallery_tuple[2]
            if gallery_minutia.is_zero():
                continue
            if Vault_Verifier.fuzzy_compare(gallery_minutia, probe_minutia):
                match = True
                gallery_string = generate_print_string_tuple(gallery_tuple)
                print_string = print_string + gallery_string
        if match:
            with open(out_file, 'a') as log:
                log.write(print_string + '\n')
        else:
            with open(out_file, 'a') as log:
                log.write(probe_string + '\n')


def write_geometric_hashing(xyt_path, out_file):
    tuples_list = generate_basis_transformed_tuples(xyt_path)
    for m_tuple in tuples_list:
        write_basis_minutiae_to_file(m_tuple[0], m_tuple[1], m_tuple[2], out_file)


def write_tuple_to_file(m_tuples, out_file):
    """
    :param m_tuples: list of tuples
    :param out_file: output file
    :return:
    """
    for m_tuple in m_tuples:
        write_basis_minutiae_to_file(m_tuple[0], m_tuple[1], m_tuple[2], out_file)


def generate_print_string_tuple(m_tuple):
    cnt_basis = m_tuple[0]
    basis = m_tuple[1]
    minutia = m_tuple[2]
    return '{};{};{};{};{};{};{};'.format(
                cnt_basis, basis.x, basis.y, basis.theta, minutia.x, minutia.y, minutia.theta
            )


def write_basis_minutiae_to_file(cnt_basis, basis, minutia, out_file, line_break=True):
    with open(out_file, 'a') as log:
        if line_break:
            log.write('{};{};{};{};{};{};{}\n'.format(
                cnt_basis, basis.x, basis.y, basis.theta, minutia.x, minutia.y, minutia.theta
            ))
        else:
            log.write('{};{};{};{};{};{};{};'.format(
                cnt_basis, basis.x, basis.y, basis.theta, minutia.x, minutia.y, minutia.theta
            ))


def write_basis_minutiae_header(out_file):
    # clear log file and add log header
    open(out_file, 'w+').close()
    with open(out_file, 'a') as log:
        log.write('basis#;basis_x probe;basis_y probe;basis_theta probe;x probe;y probe;theta probe;'
                  'basis#;basis_x gallery;basis_y gallery;basis_theta gallery;x gallery;y gallery;theta gallery\n')


def generate_all_geom_from_path(xyt_path):
    nbis_minutiae_extractor = MinutiaeExtractor()
    minutiae_list = nbis_minutiae_extractor.extract_minutiae_from_xyt(xyt_path)[0:]
    probe_minutiae_GH = GHTransformer.convert_list_to_MinutiaNBIS_GH(minutiae_list)
    for cnt_basis, basis in enumerate(probe_minutiae_GH):
        # take random basis and try matching
        element = GHTransformer.generate_verification_table_element(basis, probe_minutiae_GH.copy())
        print(element)


def convert_x_to_minutia(x):
    m_conv = MinutiaConverter()
    m = m_conv.get_minutia_from_uint(x)
    m_gh = MinutiaNBIS_GH.convert_from_MinutiaNBIS(m)
    return m_gh


def test_poly_in_gf(x):
    secret_bytes = b'\xa4uw\x89|\xaao\xce\x8b\xdf\xcdIsB\xd3k\x95G'
    poly_gen = PolynomialGenerator(secret_bytes, Constants.POLY_DEGREE, Constants.CRC_LENGTH, 32)
    print(poly_gen.evaluate_polynomial_gf_2(x, 32))


if __name__ == '__main__':
    # test_geometric_hashing()
    # generate_all_geom_from_path(XYT_GALLERY_PATH)
    #write_basis_minutiae_header(MINUTIAE_OUT_FILE)
    #write_probe_vs_gallery(XYT_PROBE_PATH, XYT_GALLERY_PATH, MINUTIAE_OUT_FILE)
    test_poly_in_gf(297850099)
