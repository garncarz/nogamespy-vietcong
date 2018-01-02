#!/usr/bin/env bash

PYTHONPATH=.:build/lib.linux-x86_64-3.6 py.test --cov-report html --cov=nogamespy $@
