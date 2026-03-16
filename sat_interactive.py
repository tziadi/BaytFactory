from pysat.solvers import Glucose3

class SATFeatureSolver:
    def __init__(self, fm_root, constraints):
        self.var_map = {}  # feature_name -> int
        self.rev_map = {}  # int -> feature_name
        self.clauses = []
        self.next_var = 1
        self.fm_root = fm_root
        self.constraints = constraints
        self.solver = Glucose3()
        self._build_model()

    def _get_var(self, feature_name):
        if feature_name not in self.var_map:
            self.var_map[feature_name] = self.next_var
            self.rev_map[self.next_var] = feature_name
            self.next_var += 1
        return self.var_map[feature_name]

    def _build_model(self):
        root_var = self._get_var(self.fm_root["key"])
        self.clauses.append([root_var])

        # Parse hierarchy
        def recurse(node):
            parent_var = self._get_var(node["key"])
            children = node.get("children", [])
            child_vars = []

            for child in children:
                child_var = self._get_var(child["key"])
                child_vars.append(child_var)
                self.clauses.append([-child_var, parent_var])  # child => parent
                if child.get("mandatory"):
                    self.clauses.append([-parent_var, child_var])  # parent => child
                recurse(child)

            group = node.get("group")
            if child_vars and group == "xor":
                self.clauses.append([-parent_var] + child_vars)  # parent => one child minimum
                for i, left in enumerate(child_vars):
                    for right in child_vars[i + 1:]:
                        self.clauses.append([-left, -right])  # at most one child
            elif child_vars and group == "or":
                self.clauses.append([-parent_var] + child_vars)  # parent => one child minimum

        recurse(self.fm_root)

        # Parse constraints
        for c in self.constraints:
            # Support current SPL format with "type": "requires" or "excludes"
            if "type" in c:
                if c["type"] == "requires":
                    src_var = self._get_var(c["source"])
                    tgt_var = self._get_var(c["target"])
                    self.clauses.append([-src_var, tgt_var])  # source => target
                elif c["type"] == "excludes":
                    src_var = self._get_var(c["source"])
                    tgt_var = self._get_var(c["target"])
                    self.clauses.append([-src_var, -tgt_var])  # not both

            # Optional support for "if"/"requires"/"excludes" format
            elif "if" in c:
                if_var = self._get_var(c["if"])
                for req in c.get("requires", []):
                    req_var = self._get_var(req)
                    self.clauses.append([-if_var, req_var])  # if => req
                for excl in c.get("excludes", []):
                    excl_var = self._get_var(excl)
                    self.clauses.append([-if_var, -excl_var])  # if => not excl

        # Add all clauses to the solver
        for clause in self.clauses:
            self.solver.add_clause(clause)

    def is_valid(self, selected_features):
        assumptions = [self._get_var(f) for f in selected_features if f in self.var_map]
        return self.solver.solve(assumptions=assumptions)

    def complete_model(self, selected_features):
        assumptions = [self._get_var(f) for f in selected_features if f in self.var_map]
        if self.solver.solve(assumptions=assumptions):
            model = self.solver.get_model()
            completed = {self.rev_map[v] for v in model if v > 0 and v in self.rev_map}
            required = set(selected_features)

            # Minimize auto-selected optional features. A feature can be dropped
            # only if the model remains satisfiable when user choices stay true
            # and that inferred feature is explicitly forced to false.
            for feature in sorted(completed - required):
                feature_var = self._get_var(feature)
                trial_assumptions = [self._get_var(f) for f in required if f in self.var_map]
                trial_assumptions.append(-feature_var)
                if self.solver.solve(assumptions=trial_assumptions):
                    completed.remove(feature)

            return sorted(completed)
        else:
            return None
