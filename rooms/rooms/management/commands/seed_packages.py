# ── rooms/management/commands/seed_packages.py ────────────────────────────────
from django.core.management.base import BaseCommand
from rooms.models import ServicePackage

PACKAGES = [
    dict(name="Стандарт",   price=1500, duration_hours=2, max_guests=6,  includes_food=False,
         description="2 часа аренды комнаты для компании до 6 человек."),
    dict(name="Вечеринка",  price=3000, duration_hours=3, max_guests=15, includes_food=True,
         description="3 часа + лёгкие закуски и безалкогольные напитки."),
    dict(name="VIP",        price=5500, duration_hours=4, max_guests=20, includes_food=True,
         description="4 часа в VIP-зале + фуршет + персональный ведущий."),
    dict(name="День рождения", price=4000, duration_hours=3, max_guests=20, includes_food=True,
         description="3 часа + торт, украшение комнаты, поздравительный баннер."),
]

class Command(BaseCommand):
    help = "Создаёт стартовые пакеты услуг"

    def handle(self, *args, **kwargs):
        created = 0
        for data in PACKAGES:
            _, ok = ServicePackage.objects.get_or_create(name=data["name"], defaults=data)
            if ok:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Готово: создано {created} пакетов."))


# ── rooms/management/commands/generate_timeslots.py ──────────────────────────
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta, time
from rooms.models import Room, TimeSlot

# Слоты по 1 часу с 10:00 до 23:00
SLOT_STARTS = [time(h, 0) for h in range(10, 23)]
SLOT_ENDS   = [time(h, 0) for h in range(11, 24)]

class Command(BaseCommand):
    help = "Генерирует временны́е слоты для всех активных комнат"

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=14,
                            help="Количество дней вперёд (default: 14)")

    def handle(self, *args, **options):
        rooms   = Room.objects.filter(is_active=True)
        today   = timezone.localdate()
        total   = 0
        for offset in range(options["days"]):
            day = today + timedelta(days=offset)
            for room in rooms:
                for start, end in zip(SLOT_STARTS, SLOT_ENDS):
                    _, created = TimeSlot.objects.get_or_create(
                        room=room, date=day, start_time=start,
                        defaults={"end_time": end}
                    )
                    if created:
                        total += 1
        self.stdout.write(self.style.SUCCESS(f"Создано слотов: {total}"))
