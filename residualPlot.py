import re
import matplotlib.pyplot as plt

def plot_residuals(log_file_path):
    """
    Parses an OpenFOAM log file, extracts time and final residual data,
    and plots the residuals over time.

    Args:
        log_file_path (str): The path to the OpenFOAM log file.
    """
    # Dictionary to store the extracted data
    data = {
        'time': [],
        'Ux_final': [],
        'Uy_final': [],
        'Uz_final': [],
        'p_final': [],
        'epsilon_final': [],
        'k_final': []
    }

    # Regular expressions to find the relevant lines
    time_pattern = re.compile(r'^Time = (\d+s)')
    residual_pattern = re.compile(r'Solving for (Ux|Uy|Uz|p|epsilon|k),.*Final residual = ([\d\.e-]+)')

    try:
        with open(log_file_path, 'r') as f:
            current_time = None
            for line in f:
                # Find the current time step
                time_match = time_pattern.search(line)
                if time_match:
                    # Convert the time string (e.g., '48s') to an integer
                    current_time = int(time_match.group(1)[:-1])
                    if current_time not in data['time']:
                        data['time'].append(current_time)

                # Find the final residual for each variable
                residual_match = residual_pattern.search(line)
                if residual_match and current_time is not None:
                    variable = residual_match.group(1)
                    residual_value = float(residual_match.group(2))
                    
                    # Store the residual value in the correct list
                    if variable == 'p': # GAMG is used for pressure
                        data['p_final'].append(residual_value)
                    else: # smoothSolver is used for other variables
                        key = f"{variable}_final"
                        data[key].append(residual_value)

    except FileNotFoundError:
        print(f"Error: The file '{log_file_path}' was not found.")
        return

    # Check if we have any data to plot
    if not data['time'] or not data['Ux_final']:
        print("Error: No residual data was found in the log file.")
        return

    # Create the plot
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.figure(figsize=(12, 8))

    # Plot the final residuals for each variable
    plt.plot(data['time'], data['Ux_final'], label='Ux final residual')
    plt.plot(data['time'], data['Uy_final'], label='Uy final residual')
    plt.plot(data['time'], data['Uz_final'], label='Uz final residual')
    plt.plot(data['time'], data['p_final'], label='p final residual')
    plt.plot(data['time'], data['epsilon_final'], label='epsilon final residual')
    plt.plot(data['time'], data['k_final'], label='k final residual')

    # Add plot labels and title
    plt.title('OpenFOAM Final Residuals vs. Time', fontsize=16)
    plt.xlabel('Time (s)', fontsize=12)
    plt.ylabel('Final Residual', fontsize=12)
    plt.yscale('log')  # Use a logarithmic scale for the y-axis
    plt.legend()
    plt.grid(True, which="both", ls="--")
    
    # Save the figure to a file
    output_filename = 'residuals_plot.png'
    plt.savefig(output_filename)
    print(f"Residual plot saved to '{output_filename}'")
    
    # Display the plot
    #plt.show()

# --- Main execution block ---
if __name__ == "__main__":
    # Define the path to your log file
    log_file_path = 'log.foamRun'
    plot_residuals(log_file_path)