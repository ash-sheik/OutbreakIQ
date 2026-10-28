
from app.database import get_db_connection
from app.models.outbreak import Outbreak


INSERT_OUTBREAK_QUERY = """
    INSERT INTO outbreaks (
        unique_id,
        state,
        district,
        disease,
        cases,
        deaths,
        outbreak_start_date,
        reporting_date,
        status,
        comments,
        data_quality_note,
        source_pdf_file,
        source_week,
        source_page,
        source_table_number
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""


def outbreak_values(outbreak: Outbreak) -> tuple:
    return (
        outbreak.unique_id,
        outbreak.state,
        outbreak.district,
        outbreak.disease,
        outbreak.cases,
        outbreak.deaths,
        outbreak.outbreak_start_date,
        outbreak.reporting_date,
        outbreak.status,
        outbreak.comments,
        outbreak.data_quality_note,
        outbreak.source_pdf_file,
        outbreak.source_week,
        outbreak.source_page,
        outbreak.source_table_number
    )


def save_outbreak(outbreak: Outbreak):
    connection = get_db_connection()
    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute(INSERT_OUTBREAK_QUERY, outbreak_values(outbreak))
        connection.commit()

        return outbreak.unique_id

    except Exception:
        connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


def save_outbreaks(outbreaks: list[Outbreak]):
    """Save multiple outbreaks with one connection and one final commit."""
    connection = get_db_connection()
    cursor = None
    outcomes = []

    try:
        cursor = connection.cursor()

        for outbreak in outbreaks:
            try:
                cursor.execute(INSERT_OUTBREAK_QUERY, outbreak_values(outbreak))
                outcomes.append((outbreak, None))
            except Exception as error:
                outcomes.append((outbreak, error))

        connection.commit()
        return outcomes

    except Exception:
        connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()

def get_all_outbreaks():
    connection = get_db_connection()
    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM outbreaks")

        outbreaks = cursor.fetchall()

        return outbreaks

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()

def get_outbreak_by_id(unique_id: str):
    connection = get_db_connection()
    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT *
            FROM outbreaks
            WHERE unique_id = %s
        """

        cursor.execute(query, (unique_id,))

        outbreak = cursor.fetchone()

        return outbreak

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()
