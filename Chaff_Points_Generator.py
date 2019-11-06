"""
    Chaff Points Generator to create randomized Minutia
"""

import random
from Minutia import MinutiaNBIS
import Constants


class ChaffPointsGenerator:
    @staticmethod
    def generate_chaff_points_randomly(amount, genuine_minutiae, smallest_minutia_rep, minutia_converter):
        """ create the amount of chaff points (Minutia) desired
        Chaff points need to have at least a specified distance from all other genuine minutiae and chaff points

        :returns a list of Minutia randomly generated """
        chaff_points_list = []
        all_vault_points = genuine_minutiae.copy()
        for _ in range(amount):
            plausible_minutia = False
            while not plausible_minutia:
                x_random = random.randrange(MinutiaNBIS.X_MIN, MinutiaNBIS.X_MAX)
                y_random = random.randrange(MinutiaNBIS.Y_MIN, MinutiaNBIS.Y_MAX)
                theta_random = random.randrange(MinutiaNBIS.THETA_MIN, MinutiaNBIS.THETA_MAX)
                quality_random = random.randrange(MinutiaNBIS.QUALITY_MIN, MinutiaNBIS.QUALITY_MAX)
                chaff_point = MinutiaNBIS(x_random, y_random, theta_random, quality_random)

                if minutia_converter.get_uint_from_minutia(chaff_point) >= (smallest_minutia_rep // 2):
                    too_close = False
                    for minutia in all_vault_points:
                        if chaff_point.distance_to(minutia) <= Constants.POINTS_DISTANCE:
                            too_close = True
                            break
                    if not too_close:
                        chaff_points_list.append(chaff_point)
                        all_vault_points.append(chaff_point)
                        plausible_minutia = True
        return chaff_points_list
