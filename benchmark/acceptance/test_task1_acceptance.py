"""External acceptance tests for Task 1 (txreconcile.py). Read-only for agents."""
import json
import os
import subprocess
import sys

import pytest

TASK_DIR = os.environ.get("BENCH_TASK_DIR")
if not TASK_DIR:
    pytest.skip("BENCH_TASK_DIR not set", allow_module_level=True)
SCRIPT = os.path.join(TASK_DIR, "txreconcile.py")

HEADER = "id,amount,currency,timestamp,status"


def cli(args):
    return subprocess.run([sys.executable, SCRIPT, *args],
                          capture_output=True, text=True, cwd=TASK_DIR)


def make_csv(tmp_path, rows):
    p = tmp_path / "tx.csv"
    p.write_text(HEADER + "\n" + "\n".join(rows) + "\n", encoding="utf-8")
    return str(p)


def parse(stdout):
    return json.loads(stdout)


def test_csv_totals(tmp_path):
    path = make_csv(tmp_path, [
        "a,10.00,USD,2024-01-01,settled",
        "b,3.50,USD,2024-01-02,refunded",
        "c,7.00,USD,2024-01-03,pending",
        "d,2.00,EUR,2024-01-04,settled",
    ])
    r = cli([path])
    assert r.returncode == 0, r.stderr
    rep = parse(r.stdout)
    assert rep["total_records"] == 4
    assert rep["valid_records"] == 4
    assert rep["invalid_records"] == 0
    assert rep["duplicate_ids"] == []
    assert rep["totals"]["USD"] == {"settled_sum": 10.0, "refunded_sum": 3.5, "net": 6.5}
    assert rep["totals"]["EUR"] == {"settled_sum": 2.0, "refunded_sum": 0.0, "net": 2.0}


def test_jsonl_totals(tmp_path):
    p = tmp_path / "tx.jsonl"
    recs = [
        {"id": "a", "amount": 10.00, "currency": "USD", "timestamp": "2024-01-01", "status": "settled"},
        {"id": "b", "amount": 3.50, "currency": "USD", "timestamp": "2024-01-02", "status": "refunded"},
        {"id": "c", "amount": 2.00, "currency": "GBP", "timestamp": "2024-01-03", "status": "failed"},
    ]
    p.write_text("\n".join(json.dumps(r) for r in recs) + "\n", encoding="utf-8")
    r = cli([str(p)])
    assert r.returncode == 0, r.stderr
    rep = parse(r.stdout)
    assert rep["valid_records"] == 3
    assert rep["totals"]["USD"]["net"] == 6.5
    assert "GBP" not in rep["totals"]


def test_duplicate_id_keeps_first(tmp_path):
    path = make_csv(tmp_path, [
        "a,10.00,USD,2024-01-01,settled",
        "b,5.00,USD,2024-01-02,settled",
        "a,99.00,USD,2024-01-03,settled",
    ])
    r = cli([path])
    assert r.returncode == 0, r.stderr
    rep = parse(r.stdout)
    assert rep["duplicate_ids"] == ["a"]
    assert rep["total_records"] == 3
    assert rep["valid_records"] == 2
    assert rep["invalid_records"] == 0
    assert rep["totals"]["USD"]["net"] == 15.0


def test_invalid_records_counted(tmp_path):
    path = make_csv(tmp_path, [
        "x,,USD,2024-01-01,settled",      # missing amount
        "y,5,USD,2024-01-01,xyz",         # bad status
        "z,5,U,2024-01-01,settled",       # bad currency
    ])
    r = cli([path])
    assert r.returncode == 0, r.stderr
    rep = parse(r.stdout)
    assert rep["invalid_records"] == 3
    assert rep["valid_records"] == 0
    assert len(rep["errors"]) == 3


def test_errors_report_line_numbers(tmp_path):
    path = make_csv(tmp_path, ["x,,USD,2024-01-01,settled"])
    r = cli([path])
    rep = parse(r.stdout)
    err = rep["errors"][0]
    assert isinstance(err["line"], int) and err["line"] >= 2
    assert isinstance(err["reason"], str) and err["reason"]


def test_malformed_csv_row_invalid(tmp_path):
    path = make_csv(tmp_path, ["oops"])
    r = cli([path])
    assert r.returncode == 0, r.stderr
    rep = parse(r.stdout)
    assert rep["invalid_records"] == 1
    assert rep["errors"][0]["line"] == 2


def test_malformed_jsonl_line_invalid(tmp_path):
    p = tmp_path / "tx.jsonl"
    p.write_text("not json\n" + json.dumps({"id": "a", "amount": 1, "currency": "USD",
                                            "timestamp": "2024-01-01", "status": "settled"}) + "\n",
                 encoding="utf-8")
    r = cli([str(p)])
    rep = parse(r.stdout)
    assert rep["invalid_records"] == 1
    assert rep["valid_records"] == 1
    assert rep["errors"][0]["line"] == 1


def test_refunds_reduce_net(tmp_path):
    path = make_csv(tmp_path, [
        "a,8.00,USD,2024-01-01,settled",
        "b,3.00,USD,2024-01-02,refunded",
    ])
    rep = parse(cli([path]).stdout)
    assert rep["totals"]["USD"]["settled_sum"] == 8.0
    assert rep["totals"]["USD"]["refunded_sum"] == 3.0
    assert rep["totals"]["USD"]["net"] == 5.0


def test_currency_lowercase_normalized(tmp_path):
    path = make_csv(tmp_path, ["a,1.00,usd,2024-01-01,settled"])
    rep = parse(cli([path]).stdout)
    assert rep["totals"]["USD"]["settled_sum"] == 1.0


def test_currency_invalid(tmp_path):
    path = make_csv(tmp_path, ["a,1.00,xy,2024-01-01,settled"])
    rep = parse(cli([path]).stdout)
    assert rep["invalid_records"] == 1


def test_negative_amount_invalid(tmp_path):
    path = make_csv(tmp_path, ["a,-5.00,USD,2024-01-01,settled"])
    rep = parse(cli([path]).stdout)
    assert rep["invalid_records"] == 1


def test_timestamp_validation(tmp_path):
    good = make_csv(tmp_path, ["a,1.00,USD,2024-01-01T10:00:00,settled"])
    assert parse(cli([good]).stdout)["valid_records"] == 1
    bad = make_csv(tmp_path, ["b,1.00,USD,not-a-date,settled"])
    rep = parse(cli([bad]).stdout)
    assert rep["invalid_records"] == 1


def test_status_case_insensitive(tmp_path):
    path = make_csv(tmp_path, ["a,4.00,USD,2024-01-01,SETTLED"])
    rep = parse(cli([path]).stdout)
    assert rep["valid_records"] == 1
    assert rep["totals"]["USD"]["settled_sum"] == 4.0


def test_empty_file(tmp_path):
    path = make_csv(tmp_path, [])
    r = cli([path])
    assert r.returncode == 0, r.stderr
    rep = parse(r.stdout)
    assert rep["total_records"] == 0
    assert rep["totals"] == {}
    assert rep["errors"] == []


def test_missing_file_exit_2(tmp_path):
    r = cli([str(tmp_path / "nope.csv")])
    assert r.returncode == 2
    assert r.stderr.strip()


def test_missing_args_exit_2():
    r = cli([])
    assert r.returncode == 2


def test_unsupported_extension_exit_1(tmp_path):
    p = tmp_path / "tx.bin"
    p.write_text("data", encoding="utf-8")
    r = cli([str(p)])
    assert r.returncode == 1


def test_output_file_matches_stdout(tmp_path):
    path = make_csv(tmp_path, ["a,1.00,USD,2024-01-01,settled"])
    out = tmp_path / "report.json"
    r = cli([path, "--output", str(out)])
    assert r.returncode == 0, r.stderr
    assert out.exists()
    assert json.loads(out.read_text(encoding="utf-8")) == json.loads(r.stdout)


def test_deterministic_output(tmp_path):
    path = make_csv(tmp_path, [
        "b,2.00,EUR,2024-01-02,settled",
        "a,1.00,USD,2024-01-01,settled",
    ])
    s1 = cli([path]).stdout
    s2 = cli([path]).stdout
    assert s1 == s2


def test_rounding_two_decimals(tmp_path):
    path = make_csv(tmp_path, [
        "a,0.10,USD,2024-01-01,settled",
        "b,0.20,USD,2024-01-02,settled",
    ])
    rep = parse(cli([path]).stdout)
    assert rep["totals"]["USD"]["settled_sum"] == 0.3
    assert rep["totals"]["USD"]["net"] == 0.3
