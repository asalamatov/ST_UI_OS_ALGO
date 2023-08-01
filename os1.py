import streamlit as st
import pandas as pd
import random
from abc import ABC, abstractmethod

class Process:
    def __init__(self, process_id, arrival_time, burst_time, priority=None):
        self.process_id = process_id
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority
        self.start_time = None
        self.completion_time = None

    def __repr__(self):
        return f"Process {self.process_id}"


class Scheduler(ABC):
    def __init__(self, processes):
        self.processes = processes
        self.completed_processes = []

    @abstractmethod
    def run(self):
        pass

    def get_completed_processes(self):
        return self.completed_processes


class FCFS(Scheduler):
    def run(self):
        current_time = 0
        for process in self.processes:
            if current_time < process.arrival_time:
                current_time = process.arrival_time
            process.start_time = current_time
            current_time += process.burst_time
            process.completion_time = current_time
            self.completed_processes.append(process)


class SJF(Scheduler):
    def run(self):
        current_time = 0
        remaining_processes = self.processes.copy()
        while remaining_processes:
            remaining_processes.sort(key=lambda x: (x.burst_time, x.arrival_time))
            process = remaining_processes.pop(0)
            if current_time < process.arrival_time:
                current_time = process.arrival_time
            process.start_time = current_time
            current_time += process.burst_time
            process.completion_time = current_time
            self.completed_processes.append(process)


class Priority(Scheduler):
    def run(self):
        current_time = 0
        remaining_processes = self.processes.copy()
        while remaining_processes:
            remaining_processes.sort(key=lambda x: (x.priority, x.arrival_time))
            process = remaining_processes.pop(0)
            if current_time < process.arrival_time:
                current_time = process.arrival_time
            process.start_time = current_time
            current_time += process.burst_time
            process.completion_time = current_time
            self.completed_processes.append(process)


class RoundRobin(Scheduler):
    def __init__(self, processes, time_quantum):
        super().__init__(processes)
        self.time_quantum = time_quantum

    def run(self):
        remaining_processes = self.processes.copy()
        current_time = 0
        while remaining_processes:
            process = remaining_processes.pop(0)
            if current_time < process.arrival_time:
                current_time = process.arrival_time
            process.start_time = current_time
            if process.burst_time > self.time_quantum:
                current_time += self.time_quantum
                process.burst_time -= self.time_quantum
                remaining_processes.append(process)
            else:
                current_time += process.burst_time
                process.completion_time = current_time
                self.completed_processes.append(process)


class SRTF(Scheduler):
    def run(self):
        current_time = 0
        remaining_processes = self.processes.copy()
        while remaining_processes:
            remaining_processes.sort(key=lambda x: (x.burst_time, x.arrival_time))
            process = remaining_processes[0]
            if current_time < process.arrival_time:
                current_time = process.arrival_time
            process.start_time = current_time
            current_time += process.burst_time
            process.completion_time = current_time
            self.completed_processes.append(remaining_processes.pop(0))
            for p in remaining_processes:
                if p.arrival_time <= current_time:
                    p.burst_time -= process.burst_time
            remaining_processes = [p for p in remaining_processes if p.burst_time > 0]


def calculate_average_waiting_time(processes):
    return sum(process.start_time - process.arrival_time for process in processes) / len(processes)


def calculate_average_turnaround_time(processes):
    return sum(process.completion_time - process.arrival_time for process in processes) / len(processes)


def generate_random_processes(num_processes, arrival_time_range, burst_time_range, priority_range=None):
    processes = []
    for i in range(num_processes):
        arrival_time = random.randint(*arrival_time_range)
        burst_time = random.randint(*burst_time_range)
        priority = random.randint(*priority_range) if priority_range else None
        process = Process(process_id=i + 1, arrival_time=arrival_time, burst_time=burst_time, priority=priority)
        processes.append(process)
    return processes


def main():
    st.title("💻 CPU Scheduling Simulator 💡")
    st.write("Select the scheduling algorithm and enter the process details.")

    algorithms = {
        "🎬 First-Come-First-Serve (FCFS)": FCFS,
        "🔍 Shortest Job Next (SJF)": SJF,
        "🏆 Priority Scheduling": Priority,
        "🔄 Round Robin": RoundRobin,
        "🔍 Shortest Remaining Time First (SRTF)": SRTF
    }
    selected_algorithm = st.selectbox("🎯 Select Scheduling Algorithm", list(algorithms.keys()))

    process_count = st.number_input("🔢 Enter the number of processes", min_value=1, value=4)

    arrival_time_range = st.slider("🕒 Arrival Time Range", 0, 20, (0, 10))
    burst_time_range = st.slider("⏳ Burst Time Range", 1, 20, (1, 10))
    priority_range = None
    if selected_algorithm == "🏆 Priority Scheduling":
        priority_range = st.slider("🏅 Priority Range", 1, 10, (1, 5))

    time_quantum = None
    if selected_algorithm == "🔄 Round Robin":
        time_quantum = st.number_input("⏱ Enter the Time Quantum for Round Robin", min_value=1, value=2)

    if st.button("Generate Random Processes 🎲"):
        processes = generate_random_processes(process_count, arrival_time_range, burst_time_range, priority_range)

        if selected_algorithm == "🔄 Round Robin":
            scheduler = algorithms[selected_algorithm](processes, time_quantum)
        else:
            scheduler = algorithms[selected_algorithm](processes)

        scheduler.run()

        st.write("✅ Simulation Finished.")
        st.write("🔄 Process Execution Order:")
        execution_order_df = pd.DataFrame([
            {
                "Process ID": process.process_id,
                "Start Time": process.start_time,
                "Completion Time": process.completion_time,
            }
            for process in scheduler.get_completed_processes()
        ])
        st.table(execution_order_df)

        avg_waiting_time = calculate_average_waiting_time(scheduler.get_completed_processes())
        avg_turnaround_time = calculate_average_turnaround_time(scheduler.get_completed_processes())

        metrics_df = pd.DataFrame({
            "Metric": ["🕰 Average Waiting Time", "⏱ Average Turnaround Time"],
            "Value": [f"{avg_waiting_time:.2f} units", f"{avg_turnaround_time:.2f} units"]
        })

        st.write("📊 Performance Metrics:")
        st.table(metrics_df)


if __name__ == "__main__":
    main()





