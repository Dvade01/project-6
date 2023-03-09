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
    (0, 600): 15,
    (600, 1000): 11.428,
    (1000, 1300): 13.333,
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
    elapsed = 0  
    if control_dist_km == 0:
        elapsed += 1
      
    control_dist_km = min(control_dist_km, brevet_dist_km)
    if control_dist_km <= 60:
        time_in_hours = control_dist_km / 20.0 + 1.0 
        return brevet_start_time.shift(minutes=int(time_in_hours * 60))
      
    max_speeds = [(0, 600, 15), (600, 1000, 11.428), (1000, 1300, 13.333), (200, 13.5), (300, 20), (400, 27), (600, 40), (1000, 75)]
    elapsed = control_dist_km / max([end - start for start, end, *_ in max_speeds if end - start <= control_dist_km]) * 60
    return brevet_start_time.shift(minutes=int(elapsed))

