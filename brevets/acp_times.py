"""
Open and close time calculations
for ACP-sanctioned brevets
following rules described at https://rusa.org/octime_alg.html
and https://rusa.org/pages/rulesForRiders
Algorithm
https://rusa.org/pages/acp-brevet-control-times-calculator
"""
from datetime import timedelta

import arrow
import math
import bisect

# used to assign speeds given the kilometer distance in the open_time function
speed_lis = [
    (0, 200, 34),
    (200, 400, 32),
    (400, 600, 30),
    (600, 1000, 28),
    (1000, 1300, 26)
]
# used in the closed_time function to calculate the special cases
# and standard "Randonneuring" events time limits as stated on wikipedia
time_limits = {
    200: 13.5,
    300: 20,
    400: 27,
    600: 40,
    1000: 75
}


def open_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Calculates the open time for a given control distance in a brevet.

    Args:
        control_dist_km: number, control distance in kilometers
        brevet_dist_km: number, nominal distance of the brevet
            in kilometers, which must be one of 200, 300, 400, 600,
            or 1000 (the only official ACP brevet distances)
        brevet_start_time: An arrow object representing the start time of the brevet.

    Returns:
        An arrow object indicating the control open time.
        This will be in the same time zone as the brevet start time.
    """
    # Copy the control distance for later use.
    brev_control_dist = control_dist_km
    # Limit control distance to the brevet distance.
    control_dist_km = min(control_dist_km, brevet_dist_km)
    done = False
    elapse = 0
    i = 0
    while not done:
        # the speed range for the current interval.
        speed_range = speed_lis[i]
        # the length of the interval.
        interval_t = speed_lis[i][1] - speed_lis[i][0]
        # the maximum speed for the current interval.
        maximum = speed_range[2]
        if interval_t <= brev_control_dist:
            # elapsed time and remaining distance for the current interval.
            elapse, brev_control_dist = elapse + interval_t / maximum, brev_control_dist - interval_t
        else:
            # elapsed time for the remaining distance and mark the calculation as done.
            elapse, brev_control_dist, done = elapse + brev_control_dist / maximum, 0, True
        # check if we have reached the last speed range or covered the entire control distance.
        if i == len(speed_lis) - 1 or brev_control_dist == 0:
            done = True
        else:
            i += 1
    # Convert elapsed time to hours and minutes and return as an Arrow object shifted from the brevet start time.
    hour = int(elapse)
    minute = round((elapse - hour) * 60)
    return brevet_start_time.shift(hours=hour, minutes=minute)


def close_time(control_dist_km, brevet_dist_km, brevet_start_time):
    """
    Args:
        control_dist_km:  number, control distance in kilometers
        brevet_dist_km: number, nominal distance of the brevet
            in kilometers, which must be one of 200, 300, 400, 600, or 1000
            (the only official ACP brevet distances)
        brevet_start_time:  An arrow object
    Returns:
        An arrow object indicating the control close time.
        This will be in the same time zone as the brevet start time.
    """
    # special cases

    # If the control distance is 0, the control closes 1 hour after the start time
    if control_dist_km == 0:
        return brevet_start_time.shift(hours=1)
    # If the control distance is less than or equal to 60 km, the control closes based on a formula
    # that depends on the control distance
    if control_dist_km <= 60:
        hours, minutes = divmod((control_dist_km / 20 + 1) * 60, 60)
        return brevet_start_time.shift(hours=hours, minutes=minutes)
    # If the control distance is greater than or equal to the brevet distance, the control closes
    # at the time limit for the brevet distance
    if control_dist_km >= brevet_dist_km:
        return brevet_start_time.shift(hours=time_limits[brevet_dist_km], minutes=0)
    # If the control distance is between 60 and 600 km, the control closes based on a formula that
    # depends on the control distance
    if control_dist_km <= 600:
        hours, minutes = divmod((control_dist_km / 15) * 60, 60)
    # If the control distance is greater than 600 km, the control closes based on a formula that
    # depends on the control distance subtract 600 km
    else:
        sub_six = control_dist_km - 600
        hours = 10 + sub_six / 11.428
        minutes = 0
    # Return an arrow object representing the control close time, rounded to the nearest minute
    return brevet_start_time.shift(hours=int(hours), minutes=int((hours % 1) * 60 + minutes))
