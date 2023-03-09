import subprocess
import os


gtfs = []
for path in os.listdir(os.path.join("cache", "ny-test-3boroughs", f"gtfs0")):
    if (
        os.path.isfile(os.path.join("cache", "ny-test-3boroughs", f"gtfs0", path))
        and os.path.splitext(
            os.path.join("cache", "ny-test-3boroughs", f"gtfs0", path)
        )[1]
        == ".zip"
    ):
        gtfs.append(
            [
                path.split(".")[0],
                os.path.join("cache", "ny-test-3boroughs", f"gtfs0", path),
            ]
        )

print(gtfs)
for g in gtfs:
    if not os.path.exists(f"validator-output/{g[0]}"):
        os.mkdir(f"validator-output/{g[0]}")
    subprocess.call(
        [
            "java",
            "-jar",
            "gtfs-validator-4.0.0-cli.jar",
            "-i",
            f"{g[1]}",
            "-o",
            f"validator-output/{g[0]}",
        ]
    )
