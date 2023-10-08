from itertools import permutations


def filter_perms(perms, key, position):
    """
    A way to filter the perms, so we only start flights from Dublin.

    :param perms: the list of permutations
    :param key: the airport code we want to filter for in the list
    :param position: the position we want it to be in.
    :return: list
    """
    valid = []

    for check in perms:
        if key == check[position]:
            valid.append('_'.join(str(item) for item in (list(check))))
    return valid


def generate_perms(start,mid,return_codes):
    permutations_list = [start] + return_codes + mid
    print(F"TOTAL {list(permutations(permutations_list))}")
    return list(permutations(permutations_list))


def permutation_by_location(perms,codes,location):
    results = []

    for code in codes:
        results += filter_perms(perms, code, location)

    return results


def calculate_distance(route):

    distances = {
    "DUB_NRT": 9500,
    "DUB_HIJ": 9473,
    "DUB_KIX": 9548,
    "DUB_PUS": 9269,
    "DUB_GMP": 9000,
    "NRT_HIJ": 850,
    "NRT_KIX": 530,
    "NRT_PUS": 959,
    "NRT_GMP": 1147,
    "HIJ_KIX": 50,
    "HIJ_PUS": 322,
    "HIJ_GMP": 589,
    "KIX_PUS": 1550,
    "KIX_GMP": 820,
    "PUS_GMP": 320
}

    total = 0
    route = route.split("_")
    for location in route:
        index = route.index(location)
        if index+1 < len(route):
            check = f"{location}_{route[index+1]}"
            rev = f"{route[index + 1]}_{location}"
            if check in distances:
                total += distances[check]
            elif rev in distances:
                total += distances[rev]

    return total

def skyscanner_format(depart,arrive,depart_date,arrive_date):
    return f"https://www.skyscanner.ie/transport/flights/{depart}/{arrive}/{depart_date}/{arrive_date}/?adultsv2=1"

def get_optimal_order():
    start = "DUB"
    mid = ["PUS"]
    return_codes = ["GMP", "NRT", "KIX"]
    last_perm_location = (len(mid) + len(return_codes))


    print(f"START : {start}")
    perms = generate_perms(start,mid,return_codes)
    print(f"tot perms {len(perms)}")


    start_dub= filter_perms(perms, "DUB", 0)
    land_perms = permutation_by_location(perms,return_codes,1)
    depart_perms = permutation_by_location(perms,return_codes, last_perm_location)

    valid_perms = list(set(start_dub) & set(land_perms) & set(depart_perms))
    print(len(valid_perms))

    option_distance = {}
    for option in valid_perms:
        option_distance[option] = (calculate_distance(option))
    # print({k: v for k, v in sorted(option_distance.items(), key=lambda item: item[1])})
    sorted_flights = sorted(option_distance.items(), key=lambda item: item[1])

    return sorted_flights[:5]

"[('DUB_GMP_PUS_NRT_KIX', 10809), ('DUB_KIX_NRT_PUS_GMP', 11357), ('DUB_GMP_PUS_KIX_NRT', 11400), ('DUB_NRT_PUS_GMP_KIX', 11599), ('DUB_KIX_GMP_PUS_NRT', 11647)]"

if __name__ == '__main__':
    # sorted(data['dub_osk'], key=lambda k: k.get('val'))
    flights = get_optimal_order()
    print(flights)


