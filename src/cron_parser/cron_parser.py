import csv
import argparse
import math
import os

def get_categorical_frequency(cron_expr):
    special = {
        '@reboot': 'On Startup',
        '@yearly': 'Yearly',
        '@annually': 'Yearly',
        '@monthly': 'Monthly',
        '@weekly': 'Weekly',
        '@daily': 'Daily',
        '@midnight': 'Daily',
        '@hourly': 'Hourly'
    }
    
    if cron_expr in special:
        return special[cron_expr]
    
    parts = cron_expr.split()
    if len(parts) < 5:
        return "Unknown"
    
    m, h, dom, mon, dow = parts[:5]

    def get_step(val):
        if val.startswith('*/'):
            try: return int(val[2:])
            except: pass
        return None

    if mon != '*':
        step = get_step(mon)
        if step == 3 or (',' in mon and len(mon.split(',')) == 4):
            return 'Quarterly'
        if step == 6 or (',' in mon and len(mon.split(',')) == 2):
            return 'Biannually'
        if ',' in mon:
            return 'Multiple times a year'
        return 'Yearly'

    if dom != '*' or dow != '*':
        dom_step = get_step(dom)
        if dom_step:
            if 5 <= dom_step <= 7: return 'Weekly'
            if 13 <= dom_step <= 15: return 'Biweekly'
            if dom_step >= 25: return 'Monthly'
            return f'Every {dom_step} days'
            
        if dow != '*' and '-' in dow:
            return 'Daily'
            
        if ',' in dom:
            return 'Multiple times a month'
        if ',' in dow:
            return 'Multiple times a week'
            
        if dom != '*' and dow == '*': return 'Monthly'
        if dow != '*' and dom == '*': return 'Weekly'
        return 'Weekly'

    if h != '*':
        h_step = get_step(h)
        if h_step:
            return f'Every {h_step} hours'
        if '-' in h or ',' in h:
            return 'Multiple times a day'
        return 'Daily'

    if m != '*':
        m_step = get_step(m)
        if m_step:
            rounded_m = math.ceil(m_step / 5.0) * 5
            if rounded_m >= 60: return 'Hourly'
            if rounded_m == 30: return 'Half-hourly'
            return f'Every {rounded_m} minutes'
        if '-' in m or ',' in m:
            return 'Multiple times an hour'
        return 'Hourly'

    return 'Every minute'

def process_cron_file(input_file, output_file):
    try:
        with open(input_file, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Could not find {input_file}")
        return
        
    data = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        is_commented = line.startswith('#')
        cleaned_line = line.lstrip('#').strip() if is_commented else line
            
        parts = cleaned_line.split()
        if not parts:
            continue
            
        cron_expr = ""
        raw_command = ""
        
        if parts[0].startswith('@'):
            cron_expr = parts[0]
            raw_command = " ".join(parts[1:])
        elif len(parts) >= 5 and any(char.isdigit() or char == '*' for char in parts[0]):
            cron_expr = " ".join(parts[:5])
            raw_command = " ".join(parts[5:])
        else:
            continue
            
        frequency = get_categorical_frequency(cron_expr)
        
        # Strip the directory path from the executable
        executable = ""
        if raw_command:
            executable_path = raw_command.split()[0]
            executable = os.path.basename(executable_path)

        data.append({
            'Executable': executable,
            'Command/Task': raw_command,
            'Frequency Bucket': frequency,
            'Commented Out': 'Yes' if is_commented else 'No',
            'Raw Cron Expression': cron_expr
        })
        
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['Executable', 'Command/Task', 'Frequency Bucket', 'Commented Out', 'Raw Cron Expression']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"Successfully processed {len(data)} cron jobs. Output saved to {output_file}.")

def main():
    parser = argparse.ArgumentParser(description="Parse and categorize cron job expressions into structured CSV reports")
    parser.add_argument("input_file", help="The text file containing cron jobs")
    parser.add_argument("-o", "--output", default="cron_analysis.csv", help="The output CSV file name")
    
    args = parser.parse_args()
    process_cron_file(args.input_file, args.output)

if __name__ == "__main__":
    main()