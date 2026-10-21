.PHONY: install init demo build watch backtest test clean
install:  ; pip install -e ".[dev]"
init:     ; edge init
demo:     ; edge build --demo --entries 80 --open
build:    ; edge build $(M) --entries $(or $(N),150)
watch:    ; edge watch $(M)
backtest: ; edge backtest --demo
test:     ; pytest
clean:    ; rm -rf build dist *.egg-info .pytest_cache artifacts/* data/*.duckdb
