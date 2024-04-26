from datetime import datetime
from csv import DictReader
from collections import defaultdict
from pathlib import Path
import pytest
from src.hp_4 import (
    reformat_dates,
    date_range,
    add_date_range,
    fees_report
)

TEMP_DIR = Path(__file__).parent / 'fixtures'

argument_fixture = ['2000-10-01', '2000-10-02', '2000-10-03']
expected_fixture = ['01 Oct 2000', '02 Oct 2000', '03 Oct 2000']

@pytest.mark.parametrize(
    'arg,expected',
    (
            (argument_fixture, expected_fixture),
    )
)
def test_reformat_dates_should_correctly_reformat(arg, expected):
    assert sorted(reformat_dates(arg)) == sorted(expected)

def test_date_range_returns_list_of_datetime_objects():
    actual = date_range('2000-01-01', 3)
    assert isinstance(actual, list)
    assert isinstance(actual[0], datetime)

def test_date_range_raises_type_error_for_start():
    with pytest.raises(TypeError):
        date_range(datetime(2000, 1, 1), 3)

def test_date_range_raises_type_error_for_n():
    with pytest.raises(TypeError):
        date_range('2000-01-01', '3')

def test_date_range_returns_correct_values():
    actual = date_range('2000-01-01', 3)
    expected = [
        datetime(2000, 1, 1),
        datetime(2000, 1, 2),
        datetime(2000, 1, 3),
    ]
    assert actual == expected

def test_add_date_range_returns_correct_values_input_1():
    values = [1, 2, 3]
    start_date = '2000-01-01'
    expected_dates = [
        datetime(2000, 1, 1),
        datetime(2000, 1, 2),
        datetime(2000, 1, 3),
    ]
    expected = list(zip(expected_dates, values))
    assert add_date_range(values, start_date) == expected

def test_add_date_range_returns_correct_values_input_2():
    values = [11, 12, 13]
    start_date = '2001-01-31'
    expected_dates = [
        datetime(2001, 1, 31),
        datetime(2001, 2, 1),
        datetime(2001, 2, 2),
    ]
    expected = list(zip(expected_dates, values))
    assert add_date_range(values, start_date) == expected

@pytest.fixture
def book_returns_short():
    return TEMP_DIR / 'book_returns_short.csv'

@pytest.fixture
def book_returns():
    return TEMP_DIR / 'book_returns.csv'

@pytest.fixture
def fees_report_out_short(book_returns_short):
    outfile = TEMP_DIR / 'fees_report_out_short.txt'
    fees_report(
        str(book_returns_short),
        str(outfile)
    )
    with open(outfile) as f:
        reader = DictReader(f)
        rows = [row for row in reader]

    return rows

@pytest.fixture
def fees_report_out(book_returns):
    outfile = TEMP_DIR / 'fees_report_out.txt'
    fees_report(
        str(book_returns),
        str(outfile)
    )
    with open(outfile) as f:
        reader = DictReader(f)
        rows = [row for row in reader]

    return rows

def test_fees_report_has_correct_fieldnames(fees_report_out_short):
    assert 'patron_id' in fees_report_out_short[0].keys()
    assert 'late_fees' in fees_report_out_short[0].keys()

def test_fees_report_has_correct_currency_format(fees_report_out_short):
    fees = [row['late_fees'] for row in fees_report_out_short]
    assert all('$' not in fee for fee in fees)
    assert all('.' in fee for fee in fees)
    assert all(len(fee.split('.')[1]) == 2 for fee in fees)

def test_fees_report_includes_all_patrons(fees_report_out_short):
    expected_fees = {
        '17-873-8783': '15.00',
        '83-279-0036': '0.00'
    }
    actual_patrons = [fee['patron_id'] for fee in fees_report_out_short]
    expected_patrons = list(expected_fees.keys())
    assert set(actual_patrons) == set(expected_patrons)

def test_fees_report_has_one_row_per_patron(fees_report_out):
    from collections import Counter
    patron_counts = Counter(row['patron_id'] for row in fees_report_out)
    assert all(count == 1 for count in patron_counts.values())
