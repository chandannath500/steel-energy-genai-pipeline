from __future__ import annotations

from pathlib import Path
from urllib.request import Request, urlopen
from zipfile import ZipFile

from src.config import RAW_DIR

UCI_ZIP_URL = (
    "https://archive.ics.uci.edu/static/public/851/"
    "steel%2Bindustry%2Benergy%2Bconsumption.zip"
)
OUTPUT_NAME = "Steel_industry_data.csv"


def main() -> None:
    """Download UCI Dataset 851 without requiring Kaggle credentials."""
    print("Downloading UCI Steel Industry Energy Consumption dataset...")

    request = Request(
        UCI_ZIP_URL,
        headers={"User-Agent": "steel-energy-genai/1.0"},
    )

    with urlopen(request, timeout=60) as response:
        archive_bytes = response.read()

    archive_path = RAW_DIR / "uci_steel_energy_dataset.zip"
    archive_path.write_bytes(archive_bytes)

    with ZipFile(archive_path) as archive:
        members = [
            member
            for member in archive.namelist()
            if member.lower().endswith("steel_industry_data.csv")
        ]

        if not members:
            raise FileNotFoundError(
                "Steel_industry_data.csv was not found inside the UCI archive."
            )

        member = members[0]
        target = RAW_DIR / OUTPUT_NAME
        with archive.open(member) as source, target.open("wb") as destination:
            destination.write(source.read())

    archive_path.unlink(missing_ok=True)

    print(f"Saved dataset to {target}")


if __name__ == "__main__":
    main()
