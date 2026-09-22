# Chibuike Chinedu Nwosu
# 3142395

import unittest
import math
import csv
import random
import copy
# import numpy as np
# import pyswarms as ps
# from deap import base, creator, tools
from simanneal import Annealer


# constants that define the likely hood of two individuals having crossover
# performed and the probability that a child will be mutated. needed for the
# DEAP library
CXPB = 0.5
MUTPB = 0.2

# define a spurious best solution and cost. We will update this as we update the cost of each particle
swarm_best_cost = 1000000
swarm_best_itinerary = []
itineraries = []
home = 11

# the unit tests to check that the simulation has been implemented correctly
class UnitTests (unittest.TestCase):
    # this will read in the track locations file and will pick out 5 fields to see if the file has been read correctly
    def testReadCSV(self):
        # read in the locations file
        rows = readCSVFile('track-locations.csv')

        # test that the corners and a middle value are read in correctly
        self.assertEqual('GP', rows[0][0])
        self.assertEqual('Valencia', rows[0][22])
        self.assertEqual('Temp week 52', rows[55][0])
        self.assertEqual('16.25', rows[55][22])
        self.assertEqual('12.5', rows[11][8])

    # this will test to see if the row conversion works. here we will convert the latitude rwo and will test 5 values
    # as we are dealing with floating point we will use almost equals rather than a direct equality
    def testRowToFloat(self):
        # read in the locations file and convert the latitude column to floats
        rows = readCSVFile('track-locations.csv')
        convertRowToFloat(rows, 2)

        # check that 5 of the values have converted correctly
        self.assertAlmostEqual(14.957883, rows[2][1], delta=0.0001)
        self.assertAlmostEqual(39.484786, rows[2][22], delta=0.0001)
        self.assertAlmostEqual(36.532176, rows[2][17], delta=0.0001)
        self.assertAlmostEqual(-38.502284, rows[2][19], delta=0.0001)
        self.assertAlmostEqual(36.709896, rows[2][5], delta=0.0001)

        # check that the conversion of a temperature row to floating point is also correct
        convertRowToFloat(rows, 5)

        # check that 5 of the values have converted correctly
        self.assertAlmostEqual(31.5, rows[5][1], delta=0.0001)
        self.assertAlmostEqual(16.5, rows[5][22], delta=0.0001)
        self.assertAlmostEqual(8.5, rows[5][17], delta=0.0001)
        self.assertAlmostEqual(23.5, rows[5][19], delta=0.0001)
        self.assertAlmostEqual(16.5, rows[5][5], delta=0.0001)

    # # this will test to see if the file conversion overall is successful for the track locations
    # # it will read in the file and will test a string, float, and int from 2 rows to verify it worked correctly
    def testReadTrackLocations(self):
        # read in the locations file
        rows = readTrackLocations()

        # check the name, latitude, and final temp of the first race
        self.assertEqual(rows[0][0], 'Thailand')
        self.assertAlmostEqual(rows[2][0], 14.957883, delta=0.0001)
        self.assertAlmostEqual(rows[55][0], 30.75, delta=0.0001)

        # check the name, longitude, and initial temp of the last race
        self.assertEqual(rows[0][21], 'Valencia')
        self.assertAlmostEqual(rows[2][21], 39.484786, delta=0.0001)
        self.assertAlmostEqual(rows[4][21], 16, delta=0.0001)

    # # tests to see if the race weekends file is read in correctly
    def testReadRaceWeekends(self):
        # read in the race weekends file
        weekends = readRaceWeekends()

        # check that thailand is weekend 8 and valencia is weekend 45
        self.assertEqual(weekends[0], 8)
        self.assertEqual(weekends[21], 45)

        # check that Austria is weekend 32
        self.assertEqual(weekends[12], 32)

    # # this will test to see if the haversine function will work correctly we will test 4 sets of locations
    def testHaversine(self):
        # read in the locations file with conversion
        rows = readTrackLocations()

        # check the distance of Thailand against itself this should be zero
        self.assertAlmostEqual(haversine(rows, 0, 0), 0.0, delta=0.01)

        # check the distance of Thailand against Silverstone this should be 9632.57 km
        self.assertAlmostEqual(haversine(rows, 0, 6), 9632.57, delta=0.01)

        # check the distance of silverstone against mugello this should be 1283.1 Km
        self.assertAlmostEqual(haversine(rows, 6, 8), 1283.12, delta=0.01)

        # check the distance of mugello to the red bull ring this should be 445.06 Km
        self.assertAlmostEqual(haversine(rows, 8, 12), 445.06, delta=0.01)

    # # will test to see if the season distance calculation is correct using the 2025 calendar
    def testDistanceCalculation(self):
        # read in the locations & race weekends, generate the weekends, and calculate the season distance
        tracks = readTrackLocations()
        weekends = readRaceWeekends()

        # calculate the season distance using mugello as the home track as this will be the case for almost all of the teams we will use silverstone for the others
        self.assertAlmostEqual(calculateSeasonDistance(tracks, weekends, 8), 146768.1778, delta=0.0001)
        self.assertAlmostEqual(calculateSeasonDistance(tracks, weekends, 6), 151481.2754, delta=0.0001)

    # # will test that the temperature constraint is working this should fail as azerbijan should fail the test
    def testTempConstraint(self):
        # load in the tracks, race weekends, and the sundays
        tracks = readTrackLocations()
        weekends1 = [8, 10, 12, 14, 16, 18, 20, 22, 24, 25, 27, 28, 32, 33, 35, 36, 38, 39, 41, 42, 44, 45]
        weekends2 = [8, 10, 12, 14, 16, 18, 30, 22, 24, 25, 27, 28, 32, 33, 35, 36, 38, 39, 48, 42, 40, 41]

        # the test with the default calender should be false because of Great Britian at 17.25
        self.assertEqual(checkTemperatureConstraint(tracks, weekends1, 20, 35), False)
        self.assertEqual(checkTemperatureConstraint(tracks, weekends2, 20, 35), True)

    # # will test that we can detect a period for a summer shutdown in the prescribed weeks
    def testSummerShutdown(self):
        # weekend patterns the first has a summer shutdown the second doesn't
        weekends1 = [8, 10, 12, 14, 16, 18, 20, 22, 24, 25, 27, 28, 32, 33, 35, 36, 38, 39, 41, 42, 44, 45]
        weekends2 = [8, 10, 12, 14, 16, 18, 20, 22, 24, 25, 27, 28, 31, 33, 35, 36, 38, 39, 41, 42, 44, 45]

        # the first should pass and the second should fail
        self.assertEqual(checkSummerShutdown(weekends1), True)
        self.assertEqual(checkSummerShutdown(weekends2), False)

# implementation of an annealer that will attempt to come up with a better calendar. it will allow the free movement of weekends with the exception of
# monaco. bahrain and abu dhabi will open and close the season respectively. the summer shutdown should still be respected. Double and triple header weekends
# are permitted but for or more races in a row is not allowed.
class CalendarAnnealer(Annealer):
    # used to initialise the annealer the state here will be the list of race weekends and the locations. we take in all the extra parameters
    # to help calculate the distance and temperature requirements on the way
    def __init__(self, weekends, home, tracks, min_temp=15, max_temp=35):
        # Store references needed for energy calculation
        self.tracks = tracks
        self.home = home
        self.min_temp = min_temp
        self.max_temp = max_temp

        # Annealer stores the solution in self.state
        super().__init__(weekends)

    # used to make a move this will take two race weekends and will swap their locations as this is the smallest change we can make
    def move(self):
        """
              Perform a move according to the priority rules:
              1) Fix coldest race below min temperature
              2) Fix hottest race above max temperature
              3) Otherwise perform a random swap

              Valencia (final race) must never be moved.
              """
        valencia_index = 21  # Valencia is fixed as the final race

        # Priority 1: fix too-cold race
        cold_index = indexLowestTemp(self.tracks, self.state, self.min_temp)
        if cold_index != -1 and cold_index != valencia_index:
            swapIndex(self.state, cold_index)
            return

        # Priority 2: fix too-hot race
        hot_index = indexHighestTemp(self.tracks, self.state, self.max_temp)
        if hot_index != -1 and hot_index != valencia_index:
            swapIndex(self.state, hot_index)
            return

        # Priority 3: random swap (must respect Valencia lock)
        swapPair(self.state)
        
    # used to calculate the energy. smaller values represent smaller distances. A default value of 1,000,000 will be returned if the
    # temperature requirement is not satisfied
    def energy(self):
        """
               Energy = total season distance + penalties.
               Smaller values are better.
               """
        distance = calculateSeasonDistance(self.tracks, self.state, self.home)
        penalty = 0

        # Temperature constraint penalty
        if not checkTemperatureConstraint(
                self.tracks, self.state, self.min_temp, self.max_temp
        ):
            penalty += 100000

        # Summer shutdown penalty
        if not checkSummerShutdown(self.state):
            penalty += 100000

        return distance + penalty

# class that will hold the weekends for genetic algorithms
class CalendarGA:
    def __init__(self, weekends):
        self.weekends = weekends[:]
        
# function that will calculate the total distance for the season assuming a given racetrack as the home racetrack
# the following will be assumed:
# - on a weekend where there is no race the team will return home
# - on a weekend in a double or triple header a team will travel straight to the next race and won't go back home
# - the preseason test will always take place in Bahrain
# - for the summer shutdown and off season the team will return home
def calculateSeasonDistance(tracks, weekends, home):
    total_distance = 0
    current_location = home

    # Sort weekends with their corresponding race indices
    race_week_pairs = sorted(enumerate(weekends), key=lambda x: x[1])

    for i, (race_index, race_week) in enumerate(race_week_pairs):
        # Travel from current location to race
        total_distance += haversine(tracks, current_location, race_index)
        current_location = race_index

        # Check if next race exists and is consecutive
        if i < len(race_week_pairs) - 1:
            next_week = race_week_pairs[i + 1][1]
            if next_week != race_week + 1:
                total_distance += haversine(tracks, current_location, home)
                current_location = home
        else:
            total_distance += haversine(tracks, current_location, home)
            current_location = home

    return total_distance


# # function that will calculate the season distance and will include the cost of penalties in the calculation
def calculateSeasonDistancePenalties(tracks, weekends, home, min_temp, max_temp):

    distance = calculateSeasonDistance(tracks, weekends, home)
    penalty = 0

    # Temperature constraint penalty
    if not checkTemperatureConstraint(tracks, weekends, min_temp, max_temp):
        penalty += 100000

    # Summer shutdown penalty
    if not checkSummerShutdown(weekends):
        penalty += 100000

    return distance + penalty

# function that will check to see if the temperature constraint for all races is satisfied. The temperature
# constraint is that a minimum temperature of min degrees for the month is required for a race to run
def checkTemperatureConstraint(tracks, weekends, min, max):
    # Months mapped from weekend numbers (Sunday of race weekend)
    # Week numbers roughly map to months assuming ISO weeks
    # Jan: 1–4, Feb: 5–8, Mar: 9–13, Apr: 14–17, May: 18–21,
    # Jun: 22–26, Jul: 27–30, Aug: 31–35, Sep: 36–39,
    # Oct: 40–43, Nov: 44–48, Dec: 49–52

    for track_index, race_week in enumerate(weekends):
        # Convert week number to temperature row
        week_row_index = race_week + 3
        temp = tracks[week_row_index][track_index]

        if temp < min or temp > max:
            return False

    return True


# function that will check to see if there is a four week gap anywhere in july and august. we will need this for the summer shutdown.
# the way this is defined is that we have a gap of three weekends between successive races. this will be weeks 29, 30, and 31, they are not
# permitted to have a race during these weekends
def checkSummerShutdown(weekends):
    """
        Checks if the summer shutdown period (weekends 29, 30, 31) has no races.
        Returns True if all three weekends are free (i.e., not in the weekends list), otherwise False.
        """
    # Summer shutdown weekends
    shutdown_weeks = [29, 30, 31]

    # Check if any of the shutdown weekends have a race
    for week in shutdown_weeks:
        if week in weekends:
            return False  # There is a race during shutdown

    return True  # All shutdown weekends are free

# will go through the genetic code of this child and will make sure that all the required weekends are in it.
# it's highly likely that with crossover that there will be weekends missing and others duplicated. we will
# randomly replace the duplicated ones with the missing ones
def childGeneticCodeFix(child):
    """
    Fix duplicated and missing race weekends after crossover.
    """
    from collections import Counter

    required = set(child)
    counts = Counter(child)

    # Identify duplicates and missing weekends
    duplicates = [w for w, c in counts.items() if c > 1]
    missing = [w for w in set(child) if counts[w] == 0]

    # Fix duplicates by replacing them with missing weekends
    child_fixed = child[:]
    miss_idx = 0
    for i in range(len(child_fixed)):
        if counts[child_fixed[i]] > 1:
            counts[child_fixed[i]] -= 1
    if miss_idx < len(missing):
        child_fixed[i] = missing[miss_idx]
    miss_idx += 1

    return child_fixed


# function that will take in the set of rows and will convert the given row index into floating point values
# this assumes the header in the CSV file is still present so it will skip the first column
def convertRowToFloat(rows, row_index):
    # started from the column index 1 to skip the first column
    for i in range(1, len(rows[row_index])):
        try:
            rows[row_index][i] = float(rows[row_index][i])
        except ValueError:

            pass # leave non-numeric entries as-is because anything that is not a floating point number should not be changed.


# function that will count how many elements in the given array are greater equal a specific value
def countGreaterEqual(array, value):
    count = 0
    for x in array:
        if x >= value:
            count += 1
    return count

# function that will perform roulette wheel crossover to generate children
def crossoverStrategy(ind1, ind2):
    child = []
    for g1, g2 in zip(ind1, ind2):
        child.append(rouletteWheel(g1, g2))
    return child

# function that will evaluate the strategy for a stock
def evaluateStrategy(individual):
    global  GA_HOME
    """
    Evaluate GA individual fitness (distance + penalties).
    """
    return (calculateSeasonDistancePenalties(
        GA_TRACKS, individual, GA_HOME, GA_MIN_TEMP, GA_MAX_TEMP
    ),)

# function that will generate the initial itineraries for particle swarm optimisation
# this will take the initial solution and will shuffle it to create new solutions
def generateInitialItineraries(num_particles, initial_solution):
    """
    Generate initial swarm of itineraries for PSO by shuffling the base solution.
    Valencia (index 21) remains fixed.
    """
    swarm = []
    for _ in range(num_particles):
        sol = initial_solution[:]
    swapPair(sol)
    swarm.append(sol)
    return swarm

# function that will generate a shuffled itinerary. However, this will make sure that the bahrain, abu dhabi, and monaco
# will retain their fixed weeks in the calendar
def generateShuffledItinerary(weekends):
    """
    Shuffle the itinerary while keeping Valencia (index 21) fixed.
    """
    import random

    valencia_index = 21
    fixed_value = weekends[valencia_index]

    indices = [i for i in range(len(weekends)) if i != valencia_index]
    values = [weekends[i] for i in indices]
    random.shuffle(values)

    new_weekends = weekends[:]
    for idx, val in zip(indices, values):
        new_weekends[idx] = val

    new_weekends[valencia_index] = fixed_value
    return new_weekends

# function that will use the haversine formula to calculate the distance in Km given two latitude/longitude pairs
# it will take in an index to two rows, and extract the latitude and longitude before the calculation.
def haversine(rows, location1, location2):
    # Rows for latitudes and longitudes
    lat_row = 2  # based on your earlier convertRowToFloat example
    lon_row = 3  # adjust if longitude is in a different row

    # Extract lat/lon for the two locations
    lat1 = float(rows[lat_row][location1])
    lon1 = float(rows[lon_row][location1])
    lat2 = float(rows[lat_row][location2])
    lon2 = float(rows[lon_row][location2])

    # Convert to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    R = 6371.0
    distance = R * c

    return distance

# function that will initialise a strategy for the stocks. we will randomise all the weights here
def initIndividual(ind_class):
    individual = ind_class()
    for i in range(len(individual)):
        individual[i] = random.random()
    return individual

# function that will give us the index of the lowest temp below min. will return -1 if none found
def indexHighestTemp(tracks, weekends, max_temp):
    highest_temp = max_temp
    highest_index = -1

    for track_index, race_week in enumerate(weekends):
        week_row_index = race_week + 3
        temp = tracks[week_row_index][track_index]

        if temp > highest_temp:
            highest_temp = temp
            highest_index = track_index

    return highest_index



# function that will give us the index of the lowest temp below min. will return -1 if none found
def indexLowestTemp(tracks, weekends, min_temp):
    lowest_temp = min_temp
    lowest_index = -1

    for track_index, race_week in enumerate(weekends):
        week_row_index = race_week + 3
        temp = tracks[week_row_index][track_index]

        if temp < lowest_temp:
            lowest_temp = temp
            lowest_index = track_index

    return lowest_index



# function that will mutate an individual
def mutateIndividual(individual, indpb=0.1):
    global GA_TRACKS, GA_MIN_TEMP, GA_MAX_TEMP
    import random

    if random.random() > indpb:
        return individual

    # Fix coldest race first
    cold_index = indexLowestTemp(GA_TRACKS, individual, GA_MIN_TEMP)
    if cold_index != -1 and cold_index != 21:
        swapIndex(individual, cold_index)
        return individual

    # Fix hottest race
    hot_index = indexHighestTemp(GA_TRACKS, individual, GA_MAX_TEMP)
    if hot_index != -1 and hot_index != 21:
        swapIndex(individual, hot_index)
        return individual

    # Otherwise random swap
    swapPair(individual)
    return individual


# objective function for particle swarm optimisation
def objectiveCalendar(particles):
    """
    Objective function for PSO. Each particle represents an itinerary.
    Returns an array of energy values (distance + penalties).
    """
    global PSO_TRACKS, PSO_HOME, PSO_MIN_TEMP, PSO_MAX_TEMP

    energies = []
    for itinerary in particles:
        energy = calculateSeasonDistancePenalties(
            PSO_TRACKS, itinerary, PSO_HOME, PSO_MIN_TEMP, PSO_MAX_TEMP
        )
        energies.append(energy)

    return energies


# prints out the itinerary that was generated on a weekend by weekend basis starting from the preaseason test
def printItinerary(tracks, weekends, home):
    """
    Prints a high-clarity, professional MotoGP season calendar.
    Designed for readability, analysis, and documentation screenshots.
    """

    # Build weekend → track mapping
    weekend_to_track = {wk: i for i, wk in enumerate(weekends)}

    home_name = tracks[0][home]
    current_location = home

    # ===== HEADER =====
    print("\n" + "═" * 78)
    print("🏁  MOTOGP SEASON CALENDAR".center(78))
    print(f"🏠  HOME BASE: {home_name}".center(78))
    print("═" * 78)

    # ===== SEASON FLOW =====
    for week in range(1, 53):

        # ─────────────────────────────
        # RACE WEEK
        # ─────────────────────────────
        if week in weekend_to_track:
            idx = weekend_to_track[week]
            track_name = tracks[0][idx]
            temp = tracks[week + 3][idx]

            print(f"\n📅  WEEK {week:02d}")

            if current_location == home:
                print(f"   ✈️  Departure : {home_name}")
            else:
                print(f"   ✈️  Departure : {tracks[0][current_location]}")

            print(f"   🏁  Race Venue : {track_name}")
            print(f"   🌡️  Temperature: {temp:.2f} °C")

            current_location = idx

        # ─────────────────────────────
        # NO RACE WEEK
        # ─────────────────────────────
        else:
            if current_location != home:
                print(f"\n📅  WEEK {week:02d}")
                print(f"   🏠  Returning Home → {home_name}")
                current_location = home
            else:
                print(f"   · Week {week:02d} | No race scheduled")

    # ===== FOOTER =====
    print("\n" + "═" * 78)
    print("✅  END OF SEASON — TEAM FINISHES AT HOME".center(78))
    print("═" * 78)




# function that will take in the given CSV file and will read in its entire contents
# and return a list of lists
def readCSVFile(file):
    # the rows to return
    rows = []

    # open the file for reading and give it to the CSV reader
    csv_file = open(file)
    csv_reader = csv.reader(csv_file, delimiter=',')

    # read in each row and append it to the list of rows.
    for row in csv_reader:
        rows.append(row)

    # close the file when reading is finished
    csv_file.close()

    # return the rows at the end of the function
    return rows

# function that will read in the race weekends file and will perform all necessary conversions on it
def readRaceWeekends():
    rows = readCSVFile('race-weekends.csv')

    # Skipped the header row
    data_rows = rows[1:]

    # Weekend numbers are in column 1
    weekends = [int(row[1]) for row in data_rows]

    return weekends

# function that will read the track locations file and will perform all necessary conversions on it.
# this should also strip out the first column on the left which is the header information for all the rows
def readTrackLocations():
    rows = readCSVFile('track-locations.csv')

    #Use the for loop to remove the header column (first column in CSV)
    for i in range(len(rows)):
        rows[i] = rows[i][1:]

    # Used the for loop to convert ONLY rows 2–55 to float (skip 0=name, skip 1=circuit name)
    for row_index in range(2, len(rows)):
        for col in range(len(rows[row_index])):
            rows[row_index][col] = float(rows[row_index][col])

    return rows

# function that performs a roulette wheel randomisation on the two given values and returns the chosen on
def rouletteWheel(a, b):
    import random
    return a if random.random() < 0.5 else b

# function that will take an itinearary and will swap the elements based on the values in the particle. If only one element is selected
# for swapping it will be randomly swapped with another element. if two or more are selected we will take those elements and shuffle them
def swapElements(itinerary, particle):
    indexes = swapIndexes(particle)

    if len(indexes) == 0:
        return itinerary
    elif len(indexes) == 1:
        idx = indexes[0]
        if idx == len(itinerary) - 1:  # Don't swap Valencia
            return itinerary

        # Swap with random non-Valencia index
        other_idx = random.randint(0, len(itinerary) - 2)
        while other_idx == idx:
            other_idx = random.randint(0, len(itinerary) - 2)

        itinerary[idx], itinerary[other_idx] = itinerary[other_idx], itinerary[idx]
    else:
        # Shuffle selected indexes (but keep Valencia if included)
        selected_vals = []
        selected_idx_list = []

        for idx in indexes:
            if idx != len(itinerary) - 1:  # Not Valencia
                selected_vals.append(itinerary[idx])
                selected_idx_list.append(idx)

        if selected_vals:
            random.shuffle(selected_vals)
            for i, idx in enumerate(selected_idx_list):
                itinerary[idx] = selected_vals[i]

    return itinerary

# function that will return a list of the indexes to be swaped according to the particle
def swapIndexes(particle):
    indexes = []
    for i, val in enumerate(particle):
        if val >= 0.5:
            indexes.append(i)
    return indexes

# function that will take an itineary and will swap a pair of weekends without changing valencia
def swapPair(itinerary):
    # Choose two random indices (not the last one which is Valencia)
    # Randomly swap two elements in the itinerary, excluding Valencia (index 21).
    import random

    valencia_index = 21

    valid_indices = [i for i in range(len(itinerary)) if i != valencia_index]
    if len(valid_indices) < 2:
        return

    i, j = random.sample(valid_indices, 2)
    itinerary[i], itinerary[j] = itinerary[j], itinerary[i]

# function that will swap the values at the given index with another randomly chosen index
def swapIndex(itinerary, index):
    # Swap the element at the given index with another randomly chosen index,
    # excluding Valencia (index 21).
    # Don't swap Valencia (last element)
    import random

    valencia_index = 21

    # Do nothing if trying to move Valencia
    if index == valencia_index:
        return

    valid_indices = [i for i in range(len(itinerary)) if i != index and i != valencia_index]
    if not valid_indices:
        return

    j = random.choice(valid_indices)
    itinerary[index], itinerary[j] = itinerary[j], itinerary[index]

# function that will run the simulated annealing case for shortening the distance seperately for both silverstone and monza
def SAcases():
    print("=" * 60)
    print("SIMULATED ANNEALING OPTIMIZATION")
    print("=" * 60)


    # Load data
    tracks = readTrackLocations()
    weekends = readRaceWeekends()


    home = 8 # Mugello index (based on track order in CSV)

    # Create annealer
    annealer = CalendarAnnealer(weekends[:], home, tracks, min_temp=15, max_temp=35)

    # Set annealing parameters as per brief
    annealer.steps = 100000

    # Run annealing
    best_state, best_energy = annealer.anneal()

    # Output results
    print("\n=== Simulated Annealing Result ===")
    print("Best calendar (weekends):")
    print(best_state)
    print(f"Total distance (km): {best_energy:.2f}")

    print("\n=== Detailed Travel Itinerary ===")
    printItinerary(tracks, best_state, home)


# function that will run the genetic algorithms cases for all four situations
def GAcases():
    from deap import base, creator, tools
    import numpy as np

    print("\n" + "=" * 60)
    print("GENETIC ALGORITHM OPTIMIZATION")
    print("=" * 60)

    import random
    from deap import base, creator, tools

    global GA_TRACKS, GA_HOME, GA_MIN_TEMP, GA_MAX_TEMP

    # Load data
    GA_TRACKS = readTrackLocations()
    base_weekends = readRaceWeekends()

    GA_HOME = 8  # Mugello
    GA_MIN_TEMP = 15
    GA_MAX_TEMP = 35

    # DEAP setup
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMin)

    toolbox = base.Toolbox()
    toolbox.register("attr_weekends", generateShuffledItinerary, base_weekends)
    toolbox.register(
        "individual",
        tools.initIterate,
        creator.Individual,
        toolbox.attr_weekends
    )
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    toolbox.register("evaluate", evaluateStrategy)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", mutateIndividual, indpb=0.1)
    toolbox.register("select", tools.selTournament, tournsize=3)

    # Create population
    population = toolbox.population(n=300)

    # Run GA
    NGEN = 1000
    for gen in range(NGEN):
        offspring = toolbox.select(population, len(population))
        offspring = list(map(toolbox.clone, offspring))

        # Apply crossover
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < 0.5:
                toolbox.mate(child1, child2)
                child1[:] = childGeneticCodeFix(child1)
                child2[:] = childGeneticCodeFix(child2)
                del child1.fitness.values
                del child2.fitness.values

        # Apply mutation
        for mutant in offspring:
            toolbox.mutate(mutant)
            del mutant.fitness.values

        # Evaluate individuals
        invalid = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid)
        for ind, fit in zip(invalid, fitnesses):
            ind.fitness.values = fit

        population[:] = offspring

    # Get best solution
    best = tools.selBest(population, 1)[0]

    print("\n=== Genetic Algorithm Result ===")
    print(f"Total distance (km): {best.fitness.values[0]:.2f}")
    print("\nPrinting full season itinerary:\n")
    printItinerary(GA_TRACKS, list(best), GA_HOME)


# function that will run particle swarm optimisation in an attempt to find a solution
def PSOcases():
    import pyswarms as ps
    import numpy as np

    print("\n" + "=" * 60)
    print("PARTICLE SWARM OPTIMIZATION")
    print("=" * 60)

    global PSO_TRACKS, PSO_HOME, PSO_MIN_TEMP, PSO_MAX_TEMP

    # Load data
    PSO_TRACKS = readTrackLocations()
    weekends = readRaceWeekends()

    PSO_HOME = 8  # Mugello
    PSO_MIN_TEMP = 15
    PSO_MAX_TEMP = 35

    num_particles = 100
    dimensions = len(weekends)

    # Create initial swarm (as object arrays of itineraries)
    initial_swarm = generateInitialItineraries(num_particles, weekends)

    # PSO operates numerically, so we maintain particles as indices controlling swaps
    # Use binary PSO to indicate which indices to perturb
    options = {
        'c1': 0.5,
        'c2': 0.3,
        'w': 0.9,
        'k': 5,
        'p': 2
    }

    optimizer = ps.discrete.BinaryPSO(
        n_particles=num_particles,
        dimensions=dimensions,
        options=options
    )

    # Run optimisation
    cost, pos = optimizer.optimize(objectiveCalendar, iters=1000)

    # Apply the best particle swaps to get the best calendar
    best_calendar = weekends[:]
    best_calendar = swapElements(best_calendar, pos)

    print("\n=== Particle Swarm Optimisation Result ===")
    print(f"Total distance (km): {cost:.2f}")
    print("\n=== Optimised Season Calendar ===")
    printItinerary(PSO_TRACKS, best_calendar, PSO_HOME)


if __name__ == '__main__':
    # uncomment this run all the unit tests. when you have satisfied all the unit tests you will have a working simulation
    # you can then comment this out and move onto your SA and GA solutions
    unittest.main()

    # just to check that the itinerary printing mechanism works. we will assume that silverstone is the home track for this
    #weekends = readRaceWeekends()
    #print(generateShuffledItinerary(weekends))
    #tracks = readTrackLocations()
    #printItinerary(tracks, weekends, 11)

    # run the cases for simulated annealing
    # SAcases()


    # run the cases for genetic algorithms
    # GAcases()

    # run the cases for particle swarm optimisation
    # PSOcases()