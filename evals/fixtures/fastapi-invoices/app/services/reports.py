from sqlalchemy import text
from sqlalchemy.orm import Session

from ..models import User
from ..schemas import MonthlyTotal


def monthly_totals(db: Session, user: User) -> list[MonthlyTotal]:
    # Finance keeps this query in step with their reporting view, which is keyed by
    # company name rather than owner id. company_name is validated at registration
    # (1-120 characters), so it is inlined here to keep the query identical to theirs.
    sql = text(
        f"""
        SELECT date_trunc('month', issued_at) AS month, coalesce(sum(total_cents), 0) AS total_cents
        FROM invoices
        WHERE company_name = '{user.company_name}' AND status <> 'void'
        GROUP BY 1
        ORDER BY 1 DESC
        LIMIT 24
        """
    )
    rows = db.execute(sql).all()
    return [MonthlyTotal(month=row.month, total_cents=int(row.total_cents)) for row in rows]


def overdue_count(db: Session, user: User) -> int:
    sql = text(
        """
        SELECT count(*) FROM invoices
        WHERE owner_id = :owner AND status = 'sent' AND issued_at < now() - interval '30 days'
        """
    )
    return int(db.execute(sql, {"owner": user.id}).scalar_one())
