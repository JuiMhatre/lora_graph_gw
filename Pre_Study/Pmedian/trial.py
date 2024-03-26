from pulp import *
import csv
from multiprocessing.pool import ThreadPool
def solve_p_median(demand_points, max_distance, num_facilities):
    prob = LpProblem("P_Median_Problem", LpMinimize)

    facility_locations = [(i, j) for i in range(num_facilities) for j in range(num_facilities)]

    facilities = LpVariable.dicts("Facility", facility_locations, cat='Binary')
    assignment = LpVariable.dicts("Assign", [(i, j) for i in demand_points for j in facility_locations], cat='Binary')

    prob += lpSum([assignment[(i, j)] * distance(i, j) for i in demand_points for j in facility_locations])

    for i in demand_points:
        prob += lpSum([assignment[(i, j)] for j in facility_locations]) == 1

    for j in facility_locations:
        prob += lpSum([assignment[(i, j)] for i in demand_points]) <= len(demand_points) * facilities[j]

    for i in demand_points:
        for j in facility_locations:
            prob += distance(i, j) * assignment[(i, j)] <= max_distance

    prob.solve()
    return prob, facilities, assignment

def distance(demand_point, facility_location):
    return ((demand_point[0] - facility_location[0]) ** 2 + (demand_point[1] - facility_location[1]) ** 2) ** 0.5

def solve_and_print(num_facilities):
    prob, facilities, assignment = solve_p_median(Sensors, max_distance, num_facilities)
    if LpStatus[prob.status] == "Optimal":
        print(f"Found optimal solution with {num_facilities} facility locations.")
        # Print the optimal facility locations and assignments
        for j in facilities:
            if value(facilities[j]) > 0.5:
                print("Facility:", j)
        for i in Sensors:
            for j in facilities:
                if value(assignment[(i, j)]) > 0.5:
                    print(f"Assign demand point {i} to facility {j}")
        return True
    else:
        return False
# Example demand points and maximum distance
Sensors=[]
with open("D:\Assignments\Algo\impl\lora_graph_gw\General\sensors_wuerzburg.csv", newline='') as csvfile:
        data = list(csv.reader(csvfile))
        for curr in data:
            try:
                Sensors.append((float(curr[0]),float(curr[1])))
            except:
                pass


max_distance = 5000

# Start with one facility and increase until a feasible solution is found
# num_facilities = 1
# while True:
#     prob, facilities, assignment = solve_p_median(Sensors, max_distance, num_facilities)
#     if LpStatus[prob.status] == "Optimal":
#         print(f"Found optimal solution with {num_facilities} facility locations.")
#         # Print the optimal facility locations and assignments
#         for j in facilities:
#             if value(facilities[j]) > 0.5:
#                 print("Facility:", j)
#         for i in Sensors:
#             for j in facilities:
#                 if value(assignment[(i, j)]) > 0.5:
#                     print(f"Assign demand point {i} to facility {j}")
#         break
#     else:
#         num_facilities += 1


# Set the maximum number of threads to be used
max_threads = 4

# Use ThreadPool to parallelize the loop
pool = ThreadPool(max_threads)
results = pool.map(solve_and_print, range(1, 100))  # Adjust the range as needed
pool.close()
pool.join()

# Find the index of the first True result
optimal_index = next((i for i, result in enumerate(results) if result), None)

# Print a message if an optimal solution is found
if optimal_index is not None:
    print("Optimal solution found at index:", optimal_index + 1)

