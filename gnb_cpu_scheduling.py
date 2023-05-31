import psutil
import subprocess
import time

gnb_pid = 23731  # Replace with your GNB process PID
initial_cpu_cores = list(range(16))  # Assign 16 CPU cores initially
load_threshold = 11  # Adjust the CPU load threshold as needed

def set_cpu_affinity(pid, cpu_list):
    cpu_list_str = ','.join(str(cpu) for cpu in cpu_list)
    subprocess.call(['taskset', '-cp', cpu_list_str, str(pid)])

def set_cpu_sleep_state(cpu):
    subprocess.call(['schedtool', '-a', str(cpu), '-e', 'nice', '-n18', 'sleep', '30', '&'])

def set_cpu_power_save_mode():
    subprocess.call(['cpupower', 'frequency-set', '-g', 'powersave'])

def set_cpu_performance_mode():
    subprocess.call(['cpupower', 'frequency-set', '-g', 'performance'])

def get_cpu_load():
    return psutil.cpu_percent(interval=1)

def main():
    print("Monitoring CPU load and dynamically adjusting CPU affinity for GNB process.")
    print("Press Ctrl+C to stop.")

    set_cpu_affinity(gnb_pid, initial_cpu_cores)
    print("Initial CPU Affinity: {}".format(subprocess.check_output(['taskset', '-pc', str(gnb_pid)]).decode()))

    active_cores = list(initial_cpu_cores)
    num_active_cores = 16

    while True:
        cpu_load = get_cpu_load()
        print("CPU Load: {}%".format(cpu_load))

        if cpu_load < load_threshold and num_active_cores > 1:
            set_cpu_sleep_state(active_cores[-1])
            active_cores.pop()
            set_cpu_affinity(gnb_pid, active_cores)
            num_active_cores -= 1
            set_cpu_power_save_mode()
            print("Put CPU core {} into sleep state and enabled power-saving mode.".format(active_cores[-1]))
        elif cpu_load >= load_threshold and num_active_cores < 16:
            set_cpu_affinity(gnb_pid, initial_cpu_cores[:num_active_cores + 1])
            set_cpu_sleep_state(initial_cpu_cores[num_active_cores])
            active_cores.append(initial_cpu_cores[num_active_cores])
            num_active_cores += 1
            set_cpu_performance_mode()
            print("Activated CPU core {} and restored performance mode.".format(active_cores[-1]))

        print("GNB PID: {}, CPU Affinity: {}".format(gnb_pid, subprocess.check_output(['taskset', '-pc', str(gnb_pid)]).decode()))

        time.sleep(5)

if __name__ == '__main__':
    main()

