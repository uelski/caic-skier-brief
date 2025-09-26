from server.baseline import rule_based_predict

def test_rules_basic():
    r = rule_based_predict("High danger above treeline due to wind slab.")
    assert r["above_treeline"] >= 3
