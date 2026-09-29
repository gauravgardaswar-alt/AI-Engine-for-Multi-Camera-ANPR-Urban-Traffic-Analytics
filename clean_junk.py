r"""
Removes junk rows from the database (test data such as plates 'IND', 'R', 'INDRJ...').

How to run (from C:\TrackSight, with the venv activated):
    python clean_junk.py            -> only SHOWS what would be deleted (safe, deletes nothing)
    python clean_junk.py --apply    -> deletes plates shorter than 8 characters or starting with IND
    python clean_junk.py --all --apply
                                    -> deletes ALL detections and alerts (fresh start for testing).
                                       Cameras and the watchlist are NOT touched.
"""
import sys
from sqlalchemy import func, or_

from app.database import get_db, Detection, Alert

MIN_LEN = 8


def open_session():
    g = get_db()
    return next(g) if hasattr(g, "__next__") else g


def main():
    apply = "--apply" in sys.argv
    wipe_all = "--all" in sys.argv
    db = open_session()
    try:
        for model, name in ((Detection, "detections"), (Alert, "alerts")):
            query = db.query(model)
            if not wipe_all:
                query = query.filter(or_(func.length(model.plate_number) < MIN_LEN,
                                         model.plate_number.like("IND%")))
            rows = query.all()
            print(f"{name}: {len(rows)} row(s) match")
            for r in rows[:10]:
                print(f"    {r.plate_number}   {r.camera_id}")
            if len(rows) > 10:
                print(f"    ... and {len(rows) - 10} more")
            if apply and rows:
                for r in rows:
                    db.delete(r)
        if apply:
            db.commit()
            print("Done. Rows deleted.")
        else:
            print("\nNothing was deleted. Add --apply to really delete.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
