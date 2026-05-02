import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.restore_legacy_testcases import RESTORE, TARGET, append_case, existing_descriptions, normalize

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".codex_deps"))
from openpyxl import load_workbook


def main():
    wb = load_workbook(TARGET)
    repaired = {}
    for sheet, (prefix, cases) in RESTORE.items():
        ws = wb[sheet]
        seen = existing_descriptions(ws)
        added = 0
        for offset, case in enumerate(cases, start=21):
            if normalize(case["desc"]) in seen:
                continue
            # Reuse the original legacy numbering gap where possible.
            append_case(ws, prefix, case, offset)
            seen.add(normalize(case["desc"]))
            added += 1
        repaired[sheet] = added
    wb.save(TARGET)
    print(repaired)


if __name__ == "__main__":
    main()
