"""Read-only aggregates used by the deterministic trend service."""

from datetime import date

from app.database import get_db_connection


def get_weekly_observations(
    disease: str | None = None,
    state: str | None = None,
    district: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> list[dict]:
    filters = ["reporting_date IS NOT NULL"]
    values = []
    for column, value in (
        ("disease", disease),
        ("state", state),
        ("district", district),
    ):
        if value is not None:
            filters.append(f"{column} = %s")
            values.append(value)
    if date_from is not None:
        filters.append("reporting_date >= %s")
        values.append(date_from)
    if date_to is not None:
        filters.append("reporting_date <= %s")
        values.append(date_to)

    query = f"""
        SELECT
            disease,
            state,
            district,
            DATE_FORMAT(
                DATE_SUB(reporting_date, INTERVAL WEEKDAY(reporting_date) DAY),
                '%x-W%v'
            ) AS reporting_week,
            DATE_SUB(reporting_date, INTERVAL WEEKDAY(reporting_date) DAY)
                AS reporting_week_start,
            SUM(cases) AS observed_cases,
            SUM(deaths) AS observed_deaths
        FROM outbreaks
        WHERE {' AND '.join(filters)}
        GROUP BY disease, state, district, reporting_week, reporting_week_start
        ORDER BY disease, state, district, reporting_week_start
    """
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, tuple(values))
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()
