import csv
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from difflib import get_close_matches

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_date, parse_time

from customers.models import Customer
from .models import Job, JobStatus, JobType


User = get_user_model()

FIELD_MAP = {
    "id": "pk",
    "job_id": "pk",
    "job id": "pk",
    "job": "pk",
    "customer": "customer",
    "client name": "customer",
    "customer_name": "customer",
    "customer name": "customer",
    "client number": "customer_phone",
    "client phone": "customer_phone",
    "customer phone": "customer_phone",
    "phone number": "customer_phone",
    "phone #": "customer_phone",
    "customer_id": "customer",
    "customer id": "customer",
    "client": "customer",
    "client name": "customer",
    "customer_name": "customer",
    "customer name": "customer",
    "client address": "customer_address",
    "street address": "customer_address",
    "billing address": "customer_address",
    "address": "customer_address",
    "customer_address": "customer_address",
    "customer address": "customer_address",
    "type": "job_type",
    "service": "job_type",
    "service type": "job_type",
    "job_type": "job_type",
    "job type": "job_type",
    "task": "job_type",
    "status": "status",
    "current status": "status",
    "description": "description",
    "desc": "description",
    "estimated_time": "estimated_time",
    "estimated time": "estimated_time",
    "estimated": "estimated_time",
    "duration": "estimated_time",
    "price": "price",
    "amount": "price",
    "quote price": "price",
    "scheduled_date": "scheduled_date",
    "scheduled date": "scheduled_date",
    "date": "scheduled_date",
    "job date": "scheduled_date",
    "scheduled": "scheduled_date",
    "est completion": "completion_date",
    "completion_date": "completion_date",
    "completion date": "completion_date",
    "completion": "completion_date",
    "completed": "completion_date",
    "start_time": "scheduled_start_time",
    "start time": "scheduled_start_time",
    "scheduled_start_time": "scheduled_start_time",
    "end_time": "scheduled_end_time",
    "end time": "scheduled_end_time",
    "scheduled_end_time": "scheduled_end_time",
    "assigned cleaner": "assigned_cleaner",
    "assigned to": "assigned_cleaner",
    "cleaner assigned": "assigned_cleaner",
    "cleaner 1": "assigned_cleaner",
    "cleaner 2": "assigned_cleaner_2",
    "cleaner": "assigned_cleaner",
    "phone": "customer_phone",
    "seller": "seller",
    "seller commission": "seller_commission",
    "cleaner 1 pay": "cleaner1_pay",
    "cleaner 2 pay": "cleaner2_pay",
    "company": "company",
    "total revenue": "total_revenue",
    "total profit": "total_profit",
}

EXPECTED_HEADERS = list(FIELD_MAP.keys())


def normalize_header(text):
    if text is None:
        return ""
    cleaned = re.sub(r"[^a-z0-9]+", " ", str(text).strip().lower())
    return cleaned.strip()


def map_header(header):
    normalized = normalize_header(header)
    if normalized in FIELD_MAP:
        return FIELD_MAP[normalized]
    match = get_close_matches(normalized, EXPECTED_HEADERS, n=1, cutoff=0.65)
    if match:
        return FIELD_MAP[match[0]]
    return None


def parse_decimal(value):
    if value is None:
        return None
    raw = str(value).strip()
    if raw == "":
        return None
    cleaned = re.sub(r"[^0-9.-]+", "", raw)
    if cleaned in ("", "-", "."):
        return None
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def parse_int(value):
    if value is None:
        return None
    value = str(value).strip()
    if value == "":
        return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def parse_date_value(value):
    if value is None:
        return None
    raw = str(value).strip()
    if not raw:
        return None
    date_formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%m/%d/%y",
        "%m-%d-%Y",
        "%m-%d-%y",
        "%b %d %Y",
        "%B %d %Y",
        "%d-%b-%Y",
        "%d %b %Y",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y/%m/%d",
        "%m.%d.%Y",
        "%d.%m.%Y",
        "%B %d, %Y",
        "%b %d, %Y",
    ]
    for fmt in date_formats:
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    try:
        return parse_date(raw)
    except (TypeError, ValueError):
        return None


def parse_time_value(value):
    if value is None:
        return None
    raw = str(value).strip()
    if not raw:
        return None
    time_formats = [
        "%H:%M",
        "%I:%M %p",
        "%I:%M%p",
        "%H:%M:%S",
        "%I %p",
    ]
    for fmt in time_formats:
        try:
            return datetime.strptime(raw, fmt).time()
        except ValueError:
            continue
    try:
        return parse_time(raw)
    except (TypeError, ValueError):
        return None


def parse_customer(value):
    if value is None:
        return None
    raw = str(value).strip()
    if raw == "":
        return None
    if raw.isdigit():
        try:
            return Customer.objects.get(pk=int(raw))
        except Customer.DoesNotExist:
            customers = Customer.objects.filter(phone__icontains=raw)
            return customers.first() if customers.exists() else None

    if "," in raw:
        last, first = [part.strip() for part in raw.split(",", 1)]
    else:
        parts = raw.split()
        first = parts[0] if parts else ""
        last = " ".join(parts[1:]) if len(parts) > 1 else ""
    queryset = Customer.objects.filter(first_name__iexact=first)
    if last:
        queryset = queryset.filter(last_name__iexact=last)
    if queryset.exists():
        return queryset.first()
    queryset = Customer.objects.filter(first_name__icontains=first)
    if last:
        queryset = queryset.filter(last_name__icontains=last)
    if queryset.exists():
        return queryset.first()
    queryset = Customer.objects.filter(address__icontains=raw)
    return queryset.first() if queryset.exists() else None


def parse_user(value, role=None):
    if value is None:
        return None
    raw = str(value).strip()
    if raw == "":
        return None
    qs = User.objects.all()
    if role is not None:
        qs = qs.filter(role=role)
    if raw.isdigit():
        try:
            return qs.get(pk=int(raw))
        except User.DoesNotExist:
            pass
    if "@" in raw:
        try:
            return qs.get(email__iexact=raw)
        except User.DoesNotExist:
            pass
    if "," in raw:
        last, first = [part.strip() for part in raw.split(",", 1)]
    else:
        parts = raw.split()
        first = parts[0] if parts else ""
        last = " ".join(parts[1:]) if len(parts) > 1 else ""
    if raw:
        exact_matches = qs.filter(username__iexact=raw) | qs.filter(email__iexact=raw)
        if exact_matches.exists():
            return exact_matches.first()
    matches = qs.filter(first_name__iexact=first)
    if last:
        matches = matches.filter(last_name__iexact=last)
    if matches.exists():
        return matches.first()
    if first:
        matches = qs.filter(first_name__istartswith=first) | qs.filter(last_name__istartswith=first)
        if matches.exists():
            return matches.first()
        matches = qs.filter(first_name__icontains=first) | qs.filter(last_name__icontains=first)
        if matches.exists():
            return matches.first()
    if last:
        matches = qs.filter(first_name__istartswith=last) | qs.filter(last_name__istartswith=last)
        if matches.exists():
            return matches.first()
        matches = qs.filter(first_name__icontains=last) | qs.filter(last_name__icontains=last)
        if matches.exists():
            return matches.first()
    matches = qs.filter(username__icontains=raw)
    return matches.first() if matches.exists() else None


def parse_choice(value, choices):
    if value is None:
        return None
    raw = str(value).strip()
    if raw == "":
        return None
    # direct match on value
    for choice_value, display in choices:
        if raw.lower() == str(choice_value).lower():
            return choice_value
    # match on human label
    for choice_value, display in choices:
        if raw.lower() == str(display).lower():
            return choice_value
    # fuzzy label match
    labels = [str(display).lower() for _, display in choices]
    matches = get_close_matches(raw.lower(), labels, n=1, cutoff=0.7)
    if matches:
        for choice_value, display in choices:
            if str(display).lower() == matches[0]:
                return choice_value
    return None


def parse_value(field_name, raw):
    if raw is None:
        return None
    if field_name == "customer":
        return parse_customer(raw)
    if field_name == "customer_phone":
        return str(raw).strip()
    if field_name == "customer_address":
        return str(raw).strip()
    if field_name == "price":
        return parse_decimal(raw)
    if field_name == "estimated_time":
        return parse_int(raw)
    if field_name in {"scheduled_date", "completion_date"}:
        normalized = str(raw).strip().lower()
        if normalized in {"tbd", "n/a", "na", "none", ""}:
            return None
        return parse_date_value(raw)
    if field_name in {"scheduled_start_time", "scheduled_end_time"}:
        normalized = str(raw).strip().lower()
        if normalized in {"tbd", "n/a", "na", "none", ""}:
            return None
        return parse_time_value(raw)
    if field_name == "job_type":
        result = parse_choice(raw, JobType.choices)
        return result
    if field_name == "status":
        return parse_choice(raw, JobStatus.choices)
    if field_name == "assigned_cleaner":
        return parse_user(raw, role="CLEANER") or parse_user(raw)
    if field_name == "assigned_cleaner_2":
        return parse_user(raw, role="CLEANER") or parse_user(raw)
    return str(raw).strip() if str(raw).strip() != "" else None


def find_or_create_customer(row_data):
    customer = None
    if row_data.get("customer"):
        customer = parse_customer(row_data["customer"])
    if customer is None and row_data.get("customer_phone"):
        phone = str(row_data["customer_phone"]).strip()
        customer = Customer.objects.filter(phone__icontains=phone).first()
    if customer is None and row_data.get("customer_address"):
        customer = Customer.objects.filter(address__icontains=row_data["customer_address"]).first()
    if customer:
        return customer

    name_raw = row_data.get("customer")
    address_raw = row_data.get("customer_address")
    phone_raw = row_data.get("customer_phone")
    if not name_raw and not address_raw:
        return None

    first = last = ""
    if name_raw:
        name = str(name_raw).strip()
        if "," in name:
            last, first = [part.strip() for part in name.split(",", 1)]
        else:
            parts = name.split()
            first = parts[0] if parts else ""
            last = " ".join(parts[1:]) if len(parts) > 1 else ""

    customer, _ = Customer.objects.get_or_create(
        first_name=first,
        last_name=last,
        defaults={
            "address": address_raw or "",
            "phone": str(phone_raw).strip() if phone_raw else "",
        },
    )
    return customer


def detect_dialect(sample):
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;\t|")
    except csv.Error:
        return csv.excel


def parse_job_csv(file_obj, created_by):
    content = file_obj.read()
    if isinstance(content, bytes):
        content = content.decode("utf-8-sig", errors="replace")
    sample = content[:4096]
    dialect = detect_dialect(sample)
    reader = csv.reader(content.splitlines(), dialect)
    rows = list(reader)
    if not rows:
        return {"processed": 0, "updated": 0, "created": 0, "errors": ["CSV file is empty."]}

    raw_headers = rows[0]
    header_map = [map_header(header) for header in raw_headers]
    if not any(header_map):
        return {"processed": 0, "updated": 0, "created": 0, "errors": ["Could not map any CSV headers to job fields."]}

    processed = 0
    updated = 0
    created = 0
    errors = []

    for row_index, row in enumerate(rows[1:], start=2):
        if not any(cell.strip() for cell in row):
            continue
        processed += 1
        row_data = {}
        for idx, raw in enumerate(row):
            if idx >= len(header_map):
                continue
            field_name = header_map[idx]
            if not field_name:
                continue
            row_data[field_name] = raw

        target_pk = row_data.get("pk")
        target_job = None
        if target_pk:
            try:
                target_job = Job.objects.get(pk=int(str(target_pk).strip()))
            except (Job.DoesNotExist, ValueError):
                errors.append(f"Row {row_index}: invalid job id '{target_pk}'.")
                continue

        customer = find_or_create_customer(row_data)
        if customer is None and target_job is None:
            has_any_job_data = any(
                row_data.get(key)
                for key in ["price", "scheduled_date", "scheduled_start_time", "scheduled_end_time", "description"]
            )
            if not has_any_job_data:
                continue
            errors.append(f"Row {row_index}: could not resolve customer from uploaded data.")
            continue

        job_fields = {}
        for field_name, raw_value in row_data.items():
            if field_name == "pk":
                continue
            if field_name in {"customer_phone", "customer_address", "seller", "seller_commission", "cleaner1_pay", "cleaner2_pay", "company", "total_revenue", "total_profit", "assigned_cleaner_2"}:
                continue
            parsed = parse_value(field_name, raw_value)
            if parsed is None and raw_value not in (None, ""):
                if field_name not in {"assigned_cleaner", "job_type", "status", "scheduled_date", "scheduled_start_time", "scheduled_end_time", "completion_date", "price", "estimated_time"}:
                    errors.append(f"Row {row_index}: could not parse field '{field_name}' value '{raw_value}'.")
            else:
                job_fields[field_name] = parsed

        if customer is not None:
            job_fields["customer"] = customer
        if "assigned_cleaner" not in job_fields or job_fields.get("assigned_cleaner") is None:
            if row_data.get("assigned_cleaner_2"):
                cleaner2 = parse_value("assigned_cleaner_2", row_data["assigned_cleaner_2"])
                if cleaner2 is not None:
                    job_fields["assigned_cleaner"] = cleaner2
        if "assigned_cleaner" not in job_fields or job_fields.get("assigned_cleaner") is None:
            job_fields["assigned_cleaner"] = created_by

        try:
            if target_job is not None:
                for field_name, value in job_fields.items():
                    setattr(target_job, field_name, value)
                target_job.full_clean()
                target_job.save()
                updated += 1
            else:
                if "customer" not in job_fields:
                    errors.append(f"Row {row_index}: missing customer.")
                    continue
                if "job_type" not in job_fields:
                    job_fields["job_type"] = JobType.WINDOW_WASH
                if "status" not in job_fields:
                    job_fields["status"] = JobStatus.PENDING
                if "price" not in job_fields:
                    job_fields["price"] = Decimal("0.00")
                job = Job(**job_fields)
                job.created_by = created_by
                job.full_clean()
                job.save()
                created += 1
        except ValidationError as exc:
            errors.append(f"Row {row_index}: validation failed: {exc.messages}")
        except Exception as exc:
            errors.append(f"Row {row_index}: unexpected error: {exc}")

    return {
        "processed": processed,
        "updated": updated,
        "created": created,
        "errors": errors,
    }
