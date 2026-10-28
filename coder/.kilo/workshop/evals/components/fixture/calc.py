import datetime


def add(a, b):
    return a + b


def mean(xs):
    return sum(xs) / len(xs)


def normalize(s):
    return s.lower()


def parse_date(s):
    return datetime.date.fromisoformat(s)
