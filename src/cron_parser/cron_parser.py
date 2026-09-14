import csv

def parse_cron_frequency_rounded(cron_expr):
    """
    Translates a raw cron expression into a human-readable, rounded frequency string.
    """
    # 1. Handle standard special strings (macros) that start with '@'
    special = {
        '@reboot': 'At startup',
        '@yearly': 'Once a year',
        '@annually': 'Once a year',
        '@monthly': 'Once a month',
        '@weekly': 'Once a week',
        '@daily': 'Once a day',
        '@midnight': 'Once a day',
        '@hourly': 'Once an hour'
    }
    
    # If the expression is in our predefined dictionary, return the human-readable version immediately
    if cron_expr in special:
        return special[cron_expr]
    
    # Split the cron expression into its individual parts (minute, hour, day of month, month, day of week)
    parts = cron_expr.split()
    
    # A standard cron expression must have at least 5 parts. If it doesn't, it's invalid.
    if len(parts) < 5:
        return "Invalid/Unknown"
    
    # Unpack the first 5 parts into variables for easier reading
    m, h, dom, mon, dow = parts[:5]
    
    # Helper function to extract the integer value from step expressions (like "*/50")
    def get_step(val):
        if val.startswith('*/'):
            try: 
                # Extract everything after "*/" and convert it to an integer
                return int(val[2:])
            except: 
                return None
        return None

    # Check if any of the time fields use the step syntax
    m_step = get_step(m)       # Minute step
    h_step = get_step(h)       # Hour step
    dom_step = get_step(dom)   # Day of month step

    # --- Section 1: Rounding Step Values ---
    
    # If a minute step is defined (e.g., */50) and all other fields are wildcards (*)
    if m_step and h == '*' and dom == '*' and mon == '*' and dow == '*':
        if m_step >= 45: return 'About once an hour'
        elif m_step >= 20: return 'About every half hour'
        elif m_step >= 10: return 'About every 15 minutes'
        else: return f'About every 5 minutes'

    # If an hour step is defined (e.g., * */12 * * *) and date fields are wildcards
    if h_step and dom == '*' and mon == '*' and dow == '*':
        if h_step >= 20: return 'About once a day'
        elif h_step >= 10: return 'About twice a day'
        else: return f'About every {h_step} hours'

    # If a day step is defined and month/day-of-week are wildcards
    if dom_step and mon == '*' and dow == '*':
        if dom_step >= 25: return 'About once a month'
        elif dom_step >= 10: return 'About twice a month'
        else: return f'About every {dom_step} days'

    # --- Section 2: Simplifying Exact Values ---
    
    # If a specific minute is set (no commas, dashes, or steps) and the rest are wildcards
    if m != '*' and ',' not in m and '-' not in m and not m.startswith('*/') and h == '*' and dom == '*' and mon == '*' and dow == '*':
        return 'Once an hour'
    
    # If a specific hour and minute are set, but the rest are wildcards
    if m != '*' and h != '*' and ',' not in h and '-' not in h and not h.startswith('*/') and dom == '*' and mon == '*' and dow == '*':
        return 'Once a day'
        
    # If a specific day of the month is set
    if dom != '*' and ',' not in dom and '-' not in dom and not dom.startswith('*/') and mon == '*' and dow == '*':
        return 'Once a month'
        
    # If a specific day of the week is set
    if dow != '*' and ',' not in dow and '-' not in dow and not dow.startswith('*/') and dom == '*' and mon == '*':
        return 'Once a week'

    # --- Section 3: Catch-all ---
    
    # If all fields are wildcards, it runs every single minute
    if m == '*' and h == '*' and dom == '*' and mon == '*' and dow == '*':
        return 'Every minute'

    # If the expression is too complex to round/simplify easily, return the raw cron string
    return f"Custom schedule: {cron_expr}"


def process_cron_file(input_file, output_file):
    """
    Reads a file containing cron jobs, parses each line, and outputs the organized data to a CSV file.
    """
    try:
        # Open the input file in read mode ('r') and read all lines into a list
        with open(input_file, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        # Handle the case where the user provided a bad file path
        print(f"Error: Could not find {input_file}")
        return
        
    # This list will hold the dictionaries of parsed data for each cron job
    data = []
    
    # Iterate through every line in the file
    for line in lines:
        # Remove leading/trailing whitespace and newline characters
        line = line.strip()
        
        # Skip empty lines to avoid errors
        if not line:
            continue
            
        # Check if the line is commented out (starts with '#')
        is_commented = False
        if line.startswith('#'):
            is_commented = True
            # Remove the '#' and leading spaces so we can still parse the cron job behind it
            cleaned_line = line.lstrip('#').strip()
        else:
            # Line is active, keep it as is
            cleaned_line = line
            
        # Split the cleaned line by spaces to separate the time fields from the command
        parts = cleaned_line.split()
        
        # If the line was just a '#' with nothing else, parts will be empty. Skip it.
        if not parts:
            continue
            
        cron_expr = ""
        raw_command = ""
        
        # Determine if the line actually contains a cron schedule
        # Case A: It uses a macro like '@daily'
        if parts[0].startswith('@'):
            cron_expr = parts[0]
            # The command is everything after the macro
            raw_command = " ".join(parts[1:])
            
        # Case B: It uses standard 5-part cron syntax (checks if the first part has numbers or a '*')
        elif len(parts) >= 5 and any(char.isdigit() or char == '*' for char in parts[0]):
            cron_expr = " ".join(parts[:5])
            # The command is everything after the 5th part
            raw_command = " ".join(parts[5:])
            
        else:
            # If it doesn't match Case A or B, it's likely just a descriptive comment. Skip it.
            continue
            
        # Convert the raw cron expression into a human-readable frequency
        frequency = parse_cron_frequency_rounded(cron_expr)
        
        # Isolate the script name
        # If the command starts directly with an absolute path (e.g., /opt/script.sh -v)
        if raw_command.startswith('/'):
            # Split the command by spaces and only take the first element (the file path)
            # This drops trailing arguments/flags like '-v' or '--force'
            command = raw_command.split()[0]
        else:
            # If it starts with a command word (e.g., "python3 /path/script.py"), keep the whole thing
            command = raw_command

        # Add the parsed data to our list as a dictionary
        data.append({
            'Command/Task': command,
            'Frequency': frequency,
            'Commented Out': 'Yes' if is_commented else 'No',
            'Raw Cron Expression': cron_expr
        })
        
    # Open the output file in write mode ('w')
    with open(output_file, 'w', newline='') as csvfile:
        # Define the column headers for the CSV
        fieldnames = ['Command/Task', 'Frequency', 'Commented Out', 'Raw Cron Expression']
        
        # Create a CSV DictWriter object which maps dictionaries onto output rows
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write the top row (headers)
        writer.writeheader()
        
        # Write all the parsed data rows
        writer.writerows(data)
    
    # Notify the user that the process is complete
    print(f"Successfully processed {len(data)} cron jobs. Output saved to {output_file}.")

# This block ensures the script only runs if executed directly (not if imported as a module)
if __name__ == "__main__":
    # Specify the input txt file and desired csv output name here
    process_cron_file('cron_jobs.txt', 'cron_analysis.csv')