#!/usr/bin/env bash

PYTHONPATH=. py.test --cov-report html --cov=nogamespy $@
