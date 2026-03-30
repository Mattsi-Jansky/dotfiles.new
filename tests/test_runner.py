from framework.runner import Runner, StepOutcome
from framework.result import ok, skipped, failed


def _outcomes(runner):
    return [e for e in runner.run_all() if isinstance(e, StepOutcome)]


def test_step_registration_order():
    r = Runner()

    @r.step(group="A", name="first")
    def s1():
        return ok()

    @r.step(group="A", name="second")
    def s2():
        return ok()

    outcomes = _outcomes(r)
    assert [o.name for o in outcomes] == ["first", "second"]


def test_step_returns_result():
    r = Runner()

    @r.step(group="G", name="n")
    def s():
        return ok("done")

    outcomes = _outcomes(r)
    assert outcomes[0].result.status == "ok"
    assert outcomes[0].result.message == "done"


def test_step_exception_becomes_failed():
    r = Runner()

    @r.step(group="G", name="bad")
    def s():
        raise ValueError("oops")

    outcomes = _outcomes(r)
    assert outcomes[0].result.status == "failed"
    assert "oops" in outcomes[0].result.message


def test_failure_does_not_short_circuit():
    r = Runner()
    call_order = []

    @r.step(group="G", name="fail")
    def s1():
        call_order.append("s1")
        raise RuntimeError("boom")

    @r.step(group="G", name="pass")
    def s2():
        call_order.append("s2")
        return ok()

    outcomes = _outcomes(r)
    assert call_order == ["s1", "s2"]
    assert len(outcomes) == 2
    assert outcomes[0].result.status == "failed"
    assert outcomes[1].result.status == "ok"


def test_outcome_group_and_name():
    r = Runner()

    @r.step(group="MyGroup", name="MyStep")
    def s():
        return skipped("nope")

    outcomes = _outcomes(r)
    assert outcomes[0].group == "MyGroup"
    assert outcomes[0].name == "MyStep"


def test_yields_started_before_outcome():
    from framework.runner import StepStarted

    r = Runner()

    @r.step(group="G", name="test")
    def s():
        return ok()

    events = list(r.run_all())
    assert len(events) == 2
    assert isinstance(events[0], StepStarted)
    assert isinstance(events[1], StepOutcome)
    assert events[0].name == "test"
