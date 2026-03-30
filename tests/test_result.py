from framework.result import Result, ItemResult, ok, skipped, failed


def test_ok_defaults():
    r = ok()
    assert r.status == "ok"
    assert r.message == ""
    assert r.items == []


def test_ok_with_message():
    r = ok("done")
    assert r.status == "ok"
    assert r.message == "done"


def test_ok_with_items():
    items = [ItemResult("pkg", "ok")]
    r = ok(items=items)
    assert r.items == items


def test_skipped_defaults():
    r = skipped()
    assert r.status == "skipped"
    assert r.message == ""


def test_skipped_with_message():
    r = skipped("already installed")
    assert r.message == "already installed"


def test_failed_defaults():
    r = failed()
    assert r.status == "failed"


def test_failed_with_message():
    r = failed("boom")
    assert r.status == "failed"
    assert r.message == "boom"


def test_item_result():
    item = ItemResult(name="ripgrep", status="ok")
    assert item.name == "ripgrep"
    assert item.status == "ok"


def test_result_dataclass():
    r = Result(status="ok", message="hi", items=[ItemResult("a", "ok")])
    assert r.status == "ok"
    assert r.message == "hi"
    assert len(r.items) == 1


def test_ok_does_not_share_items_list():
    r1 = ok()
    r2 = ok()
    r1.items.append(ItemResult("x", "ok"))
    assert r2.items == []
