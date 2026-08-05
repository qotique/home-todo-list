from datetime import date

import flet as ft

from models import PRIORITY_HIGH, PRIORITY_LOW, PRIORITY_MEDIUM

_PRIORITY_COLORS = {
    PRIORITY_LOW: ft.Colors.GREEN,
    PRIORITY_MEDIUM: ft.Colors.ORANGE,
    PRIORITY_HIGH: ft.Colors.RED,
}

_PRIORITY_LABELS = {
    PRIORITY_LOW: "Низкий",
    PRIORITY_MEDIUM: "Средний",
    PRIORITY_HIGH: "Высокий",
}


def priority_color(priority: int):
    return _PRIORITY_COLORS.get(priority, ft.Colors.GREY)


def priority_label(priority: int) -> str:
    return _PRIORITY_LABELS.get(priority, "Низкий")


def format_date(d: date) -> str:
    return d.strftime("%d.%m.%Y")


def _make_meta(priority: int, due_date, assignee_name: str | None) -> ft.Row:
    parts: list[ft.Control] = []
    prio_text = ft.Text(priority_label(priority), size=12, color=priority_color(priority))
    parts.append(prio_text)

    if due_date is not None:
        overdue = due_date < date.today()
        parts.append(
            ft.Text(
                format_date(due_date) + (" (просрочено)" if overdue else ""),
                size=12,
                color=ft.Colors.RED if overdue else ft.Colors.GREY_700,
            )
        )

    if assignee_name:
        parts.append(ft.Text(assignee_name, size=12, color=ft.Colors.GREY_700))

    return ft.Row(spacing=10, controls=parts, wrap=True)


def task_assignee(task_assignee, users: list):
    if task_assignee is None:
        return None
    for u in users:
        if u.id == task_assignee:
            return u.name
    return None