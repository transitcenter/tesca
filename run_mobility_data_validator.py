import subprocess

subprocess.call(['java', '-jar', 'gtfs-validator-4.0.0-cli.jar', '-i', 'ny_data/feeds_2023_01_27/lirr.zip', '-o', 'validator-output'])