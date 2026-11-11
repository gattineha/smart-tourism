from django.core.management.base import BaseCommand
from tourism.models import Category, Destination

CATEGORIES = ["Hill Station", "Beach", "Fort", "Temple", "Wildlife", "Caves"]

# name, district, category, min_days, max_days,
# transport, stay_per_day, food_per_day, activity, best_months, description
DESTINATIONS = [
    ("Lonavala", "Pune", "Hill Station", 1, 3, 600, 1200, 500, 400,
     "6,7,8,9,10,11,12,1,2",
     "Popular hill station with waterfalls, viewpoints and caves. Very green in monsoon."),
    ("Mahabaleshwar", "Satara", "Hill Station", 2, 3, 900, 1500, 600, 600,
     "10,11,12,1,2,6,7,8",
     "Cool hill station known for viewpoints, Venna Lake and strawberry farms."),
    ("Matheran", "Raigad", "Hill Station", 1, 2, 500, 1500, 500, 500,
     "10,11,12,1,2,3",
     "Vehicle-free hill station reached by walking, horse or toy train, with many sunset points."),
    ("Bhandardara", "Ahilyanagar", "Hill Station", 1, 2, 800, 1300, 500, 300,
     "6,7,8,9,10",
     "Lake and waterfall region around Arthur Lake, beautiful during and after monsoon."),
    ("Alibaug", "Raigad", "Beach", 1, 3, 500, 1400, 600, 500,
     "10,11,12,1,2,3",
     "Weekend beach town near Mumbai with calm beaches, a sea fort and water sports."),
    ("Ganpatipule", "Ratnagiri", "Beach", 2, 3, 1200, 1100, 500, 300,
     "10,11,12,1,2,3",
     "Clean beach with a famous coastal Ganesh temple on the Konkan coast."),
    ("Tarkarli", "Sindhudurg", "Beach", 2, 4, 1800, 1300, 600, 1200,
     "10,11,12,1,2,3,4,5",
     "Clear-water beach known for scuba diving, snorkelling and Konkani food."),
    ("Raigad Fort", "Raigad", "Fort", 1, 2, 700, 900, 400, 300,
     "10,11,12,1,2,6,7,8,9",
     "Capital fort of Chhatrapati Shivaji Maharaj, reached by ropeway or steps."),
    ("Sinhagad Fort", "Pune", "Fort", 1, 2, 300, 800, 350, 100,
     "6,7,8,9,10,11,12,1,2",
     "Historic hill fort near Pune, famous for the trek, views and local snacks."),
    ("Daulatabad Fort", "Chhatrapati Sambhajinagar", "Fort", 1, 2, 1500, 1200, 450, 200,
     "10,11,12,1,2,3",
     "Massive medieval hill fort with a dark winding passage and strong defences."),
    ("Nashik-Trimbakeshwar", "Nashik", "Temple", 1, 3, 700, 1100, 450, 200,
     "10,11,12,1,2,3,7,8",
     "Pilgrimage city on the Godavari with Trimbakeshwar Jyotirlinga and Panchavati."),
    ("Shirdi", "Ahilyanagar", "Temple", 1, 2, 700, 1000, 400, 100,
     "10,11,12,1,2,3",
     "Major pilgrimage town of Sai Baba with a well-organised temple complex."),
    ("Tadoba Andhari Tiger Reserve", "Chandrapur", "Wildlife", 2, 3, 2500, 2500, 800, 3500,
     "11,12,1,2,3,4,5",
     "Maharashtra's oldest national park, known for tiger sightings on jeep safaris."),
    ("Sanjay Gandhi National Park", "Mumbai Suburban", "Wildlife", 1, 1, 300, 1500, 500, 100,
     "10,11,12,1,2,3",
     "Forest park inside Mumbai with Kanheri Caves, nature trails and a lion safari."),
    ("Ajanta Caves", "Chhatrapati Sambhajinagar", "Caves", 1, 2, 1500, 1500, 500, 300,
     "10,11,12,1,2,3",
     "UNESCO site with ancient Buddhist cave paintings and carved monasteries."),
    ("Ellora Caves", "Chhatrapati Sambhajinagar", "Caves", 1, 2, 1500, 1400, 500, 250,
     "10,11,12,1,2,3",
     "UNESCO site with Buddhist, Hindu and Jain rock-cut caves, including Kailasa Temple."),
]


class Command(BaseCommand):
    help = "Loads sample categories and destinations (safe to run more than once)"

    def handle(self, *args, **options):
        categories = {}
        for name in CATEGORIES:
            categories[name], _ = Category.objects.get_or_create(name=name)

        for (name, district, cat, min_d, max_d, transport, stay, food,
             activity, months, description) in DESTINATIONS:
            Destination.objects.update_or_create(
                name=name,
                defaults={
                    "district": district,
                    "category": categories[cat],
                    "description": description,
                    "min_days": min_d,
                    "max_days": max_d,
                    "transport_cost": transport,
                    "stay_cost_per_day": stay,
                    "food_cost_per_day": food,
                    "activity_cost": activity,
                    "best_months": months,
                    "is_active": True,
                },
            )

        self.stdout.write(self.style.SUCCESS(
            f"Done: {Category.objects.count()} categories, "
            f"{Destination.objects.count()} destinations."
        ))