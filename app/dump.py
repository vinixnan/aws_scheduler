k1 = len(used_machines)
k2 = sum(machine["ecu"] for machine in used_machines)

if self.memo[k1] and False:
    selected_data = None
    diff = float("inf")
    for total_ecu, data in self.memo[k1].items():
        val = abs(total_ecu - k2)
        if val < diff:
            diff = val
            selected_data = data
    machines = {}
    for i, machine_data in enumerate(used_machines):
        mach = Machine("host" + str(i), machine_data, "link" + str(i))
        machines[mach.name] = mach
    resp = calc_makespan(machines, selected_data, self.problem_file_path)
    machines = {k: v for k, v in machines.items() if k in resp["tasks"].keys()}
    price = math.ceil(float(resp["makespan"]) / 3600) * sum(
        [machine.data["pricePerUnit"] for machine in machines.values()]
    )
    data = {}
    data["makespan"] = resp["makespan"]
    data["price"] = price
    data["tasks"] = resp["tasks"]
    print(self.ccc)
    self.ccc = self.ccc + 1
else:
    dc = self.memo[k1]
    makespan, price, tasks = self.pysim(used_machines)
    dc[len(tasks)] = tasks
    print(self.ccc)
    self.ccc = self.ccc + 1
    data = {}
    data["makespan"] = makespan
    data["price"] = price
    data["tasks"] = tasks
