.PHONY: test demo benchmark slurm

test:
	PYTHONPATH=src python -m unittest discover -s tests -v

demo:
	PYTHONPATH=src python -m matagent_lab discover --config configs/ar_glasses.json --out runs/ar_glasses_report.json

benchmark:
	PYTHONPATH=src python -m matagent_lab benchmark --config configs/robotics_actuator.json --out runs/robotics_benchmark.json

slurm:
	PYTHONPATH=src python -m matagent_lab slurm --formula BaTiO3 --workflow dft --out runs/BaTiO3_dft.slurm

