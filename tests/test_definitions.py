"""
test_definitions.py — Tests for definition wrappers.
"""

from __future__ import annotations

from core.domain.definitions import ActionDef, CivTemplate, ResonanceDef


class TestResonanceDef:
    """Tests for ResonanceDef."""

    def test_get_resonance(self):
        thelema = ResonanceDef.get("thelema")
        assert thelema is not None
        assert thelema.id == "thelema"
        assert thelema.name == "Thelema"

    def test_all_resonances(self):
        all_res = ResonanceDef.all()
        assert len(all_res) >= 20  # 20 essences
        names = [r.id for r in all_res]
        assert "thelema" in names
        assert "anarchism" in names

    def test_get_affinity(self):
        affinity = ResonanceDef.get_affinity("thelema", "anarchism")
        assert isinstance(affinity, (int, float))

    def test_get_attribute(self):
        will = ResonanceDef.get_attribute("thelema", "will")
        assert will > 0


class TestActionDef:
    """Tests for ActionDef."""

    def test_get_action(self):
        found_circle = ActionDef.get("found_circle")
        assert found_circle is not None
        assert found_circle.id == "found_circle"
        assert found_circle.cooldown == 5

    def test_all_actions(self):
        all_actions = ActionDef.all()
        assert len(all_actions) >= 6
        ids = [a.id for a in all_actions]
        assert "write_manifesto" in ids
        assert "propagate_idea" in ids


class TestCivTemplate:
    """Tests for CivTemplate."""

    def test_get_civ_template(self):
        default = CivTemplate.get("default")
        assert default is not None
        assert default.meta_id == "default"
        assert default.population == 10000

    def test_all_civ_templates(self):
        all_civs = CivTemplate.all()
        assert len(all_civs) >= 5  # default, theocracy, etc
        meta_ids = [c.meta_id for c in all_civs]
        assert "default" in meta_ids

    def test_civ_template_resources(self):
        default = CivTemplate.get("default")
        assert default.resources is not None
        assert "food" in default.resources

    def test_civ_template_dominant_resonances(self):
        default = CivTemplate.get("default")
        assert len(default.dominant_resonances) >= 1
        # Check format: list of (resonance_id, value)
        res, val = default.dominant_resonances[0]
        assert isinstance(res, str)
        assert isinstance(val, (int, float))
