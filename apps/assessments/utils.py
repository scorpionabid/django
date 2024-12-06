from datetime import datetime

def get_current_semester():
    """Cari semestri təyin et"""
    month = datetime.now().month
    return 1 if month < 7 else 2

def get_current_academic_year():
    """Cari tədris ilini təyin et"""
    now = datetime.now()
    year = now.year
    month = now.month
    
    if month < 7:  # İkinci semestr
        return f"{year-1}-{year}"
    else:  # Birinci semestr
        return f"{year}-{year+1}" 