def measurements_sum(measurements):
    if len(measurements) == 0:
        return {
            "width": 0,
            "depth": 0,
            "length": 0,
            "weight": 0
        }

    total = measurements[0]
    for measurement in measurements[1:]:
        total = {
            k: total[k] + measurement[k]
            for k in measurement
        }
    return total


class Measurements(object):
    def __init__(self, length, width, depth, weight):
        self.length = length
        self.width = width
        self.depth = depth
        self.weight = weight


class PackageSize(object):
    def __init__(self, measurement_limits, cost):
        self.limits = measurement_limits
        self.cost = cost

    def will_fit(self, measurements):
        if isinstance(measurements, list):
            measurements = measurements_sum(measurements)

        if isinstance(measurements, dict):
            measurements = Measurements(**measurements)

        return all([measurements.__dict__[k] <= self.limits.__dict__[k]
                    for k in self.limits.__dict__])

    def set_weight(self, w):
        if isinstance(w, list):
            w = measurements_sum(w)

        if isinstance(w, dict):
            w = w['weight']

        for k in sorted(self.cost.keys()):
            if w < k:
                w = k
                break

        return PackageSize(self.limits, self.cost[w])


class SIZES:
    SMALL = PackageSize(Measurements(45, 35, 16, 2), {
        # kg: [1st class £, 2nd class £]
        1: [3.40, 2.90],
        2: [5.50, 2.90]
    })
    MEDIUM = PackageSize(Measurements(61, 46, 46, 20), {
        1: [5.70, 5.00],
        2: [8.95, 5.00],
        5: [15.85, 13.75],
        10: [21.90, 20.25],
        20: [33.40, 28.55]
    })
    # LARGE = PackageSize()


def package(measurements):
    if SIZES.SMALL.will_fit(measurements):
        return [SIZES.SMALL.set_weight(measurements)]
    if SIZES.MEDIUM.will_fit(measurements):
        return [SIZES.MEDIUM.set_weight(measurements)]

    i = 0
    while SIZES.MEDIUM.will_fit(measurements[:i + 1]):
        i += 1

    extra = measurements[i:]
    return [SIZES.MEDIUM.set_weight(measurements[:i])] + package(extra)
