import re

def triangular(x, a, b, c):
    if x < a:
        return 0
    elif a <= x < b:
        return (x - a) / (b - a)
    elif b <= x < c:
        return (c - x) / (c - b)
    elif x == c:
        return 1
    else:
        return 0

def trapezoidal(x, a, b, c, d):
    if x < a:
        return 0
    elif a <= x < b:
        return (x - a) / (b - a)
    elif b <= x <= c:
        return 1
    elif c < x < d:
        return (d - x) / (d - c)
    else:
        return 0

def load_knowledge_base(file_path):
    knowledge_base = {}
    rules = []

    with open(file_path, 'r') as f:
        current_var = None
        for line in f:
            line = line.strip()
            if not line or line.startswith("OUTPUT:") or line.startswith("RULE"):
                continue

            if line.startswith("INPUT:"):
                current_var = line.split(":")[1].strip()
                knowledge_base[current_var] = {}
                continue

            if ":" in line:
                key, value = line.split(":", 1)
                params = [float(x) for x in re.findall(r"[-+]?\d*\.\d+|\d+", value)]
                if "Triangular" in value:
                    knowledge_base[current_var][key.strip()] = params
                elif "Trapezoidal" in value:
                    knowledge_base[current_var][key.strip()] = params

            if line.startswith("RULE"):
                match = re.match(r"RULE \d+: IF (.*) THEN (.*);", line)
                if match:
                    condition = match.group(1).strip()
                    result = match.group(2).strip()
                    rules.append({"condition": condition, "result": result})

    knowledge_base["rules"] = rules
    return knowledge_base

def fuzzy_inference(gejala_user, knowledge_base):
    results = {"SAKIT": 0, "SEDANG": 0, "SEHAT": 0}

    for rule in knowledge_base["rules"]:
        condition = rule["condition"]
        result = rule["result"].replace("KesehatanTanah IS ", "").strip()

        conditions = condition.split(" AND ")
        condition_values = []

        for cond in conditions:
            if " OR " in cond:
                sub_conditions = cond.split(" OR ")
                sub_values = []
                for sub_cond in sub_conditions:
                    var, level = sub_cond.strip().split(" IS ")
                    level = level.upper()
                    value = gejala_user.get(var, 0)
                    params = knowledge_base[var][level]
                    if len(params) == 3:
                        sub_values.append(triangular(value, *params))
                    elif len(params) == 4:
                        sub_values.append(trapezoidal(value, *params))
                condition_values.append(max(sub_values))
            else:
                var, level = cond.strip().split(" IS ")
                level = level.upper()
                value = gejala_user.get(var, 0)
                params = knowledge_base[var][level]
                if len(params) == 3:
                    condition_values.append(triangular(value, *params))
                elif len(params) == 4:
                    condition_values.append(trapezoidal(value, *params))

        results[result] = max(results[result], min(condition_values))

    total = sum(results.values())
    if total > 0:
        for key in results:
            results[key] = (results[key] / total) * 100
    else:
        for key in results:
            results[key] = 0

    final_result = max(results, key=results.get)
    probability = results[final_result]
    return final_result, probability
