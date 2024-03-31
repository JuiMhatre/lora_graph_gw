import numpy as np
import random
import math
import csv
# Define distance function
def euclidean_distance(p1, p2):
    return np.linalg.norm(p1 - p2)

# Objective function: Average intra-cluster distance
def objective_function(data, centers, labels):
    total_distance = 0
    for i, center in enumerate(centers):
        cluster_points = data[labels == i]
        if len(cluster_points) > 0:
            total_distance += np.mean([euclidean_distance(p, center) for p in cluster_points])
    return total_distance / len(centers)

# Generate initial solution (random number of clusters)
def initial_solution(data):
    k = random.randint(1, len(data))  # Random number of clusters
    centers = random.sample(data.tolist(), k)
    return k, centers

# Generate neighbor solution (add or remove a cluster)
def neighbor_solution(data, current_centers):
    new_centers = current_centers.copy()
    if random.random() < 0.5:  # Add a cluster
        new_centers.append(random.choice(data))
    else:  # Remove a cluster
        if len(new_centers) > 1:
            random_center = random.choice(range(len(new_centers)))  # Choose an index
            del new_centers[random_center]
    return new_centers
# Function to calculate maximum distance between any data point and cluster centers
def max_cluster_distance(data, centers, labels):
    max_distance = 0
    for i, center in enumerate(centers):
        cluster_points = data[labels == i]
        if len(cluster_points) > 0:
            distances = [euclidean_distance(p, center) for p in cluster_points]
            max_distance = max(max_distance, max(distances))
    return max_distance

# Simulated Annealing algorithm
def simulated_annealing(data, max_iterations, initial_temperature, cooling_rate, max_distance_threshold):
    current_temperature = initial_temperature
    current_solution_count, current_centers = initial_solution(data)
    current_labels = np.array([np.argmin([euclidean_distance(p, center) for center in current_centers]) for p in data])
    current_max_distance = max_cluster_distance(data, current_centers, current_labels)
    
    best_solution_count = current_solution_count
    best_centers = current_centers
    best_max_distance = current_max_distance
    
    for iteration in range(max_iterations):
        neighbor_centers = neighbor_solution(data, current_centers)
        neighbor_labels = np.array([np.argmin([euclidean_distance(p, center) for center in neighbor_centers]) for p in data])
        neighbor_max_distance = max_cluster_distance(data, neighbor_centers, neighbor_labels)
        
        delta_distance = neighbor_max_distance - current_max_distance
        if delta_distance < 0 or random.random() < math.exp(-delta_distance / current_temperature):
            current_centers = neighbor_centers
            current_labels = neighbor_labels
            current_max_distance = neighbor_max_distance
            current_solution_count = len(neighbor_centers)
            
            if current_max_distance < best_max_distance:
                best_centers = current_centers
                best_max_distance = current_max_distance
                best_solution_count = current_solution_count
        
        current_temperature *= cooling_rate
        
        # Early termination if the maximum distance threshold is met
        if best_max_distance <= max_distance_threshold:
            break
    
    return best_solution_count, best_centers, best_max_distance


# Example usage
if __name__ == "__main__":
    # Generate some random data points
    np.random.seed(0)
    Sensors=[]
    with open("sensors.csv", newline='') as csvfile:
        data = list(csv.reader(csvfile))
        for curr in data:
            try:
                Sensors.append([float(curr[0]),float(curr[1])])
            except:
                pass
    data = np.random.rand(100, 2)
    data = np.asarray(Sensors)
    # Parameters for simulated annealing
    max_iterations = 50000
    initial_temperature = 1.0
    cooling_rate = 0.95
    max_distance_threshold = 300     # Maximum distance between any two points in clusters
    
    # Run simulated annealing
    num_clusters, centers, max_distance = simulated_annealing(data, max_iterations, initial_temperature, cooling_rate, max_distance_threshold)
    
    print("Number of clusters:", num_clusters)
    print("Cluster centers:", centers)
    print("Maximum distance between any two points in clusters:", max_distance)
