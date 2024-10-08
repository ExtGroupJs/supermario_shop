from django.core.management import call_command
from django.core.management.base import BaseCommand
from termcolor import colored


class Command(BaseCommand):
    help = "Loads initial fixtures"

    def handle(self, *args, **options):
        # print(
        #     colored(
        #         "There's no fixtures to add yet",
        #         "red",
        #         attrs=["blink"],
        #     )
        # )

        call_command("loaddata", "auth.group.json")
        print(
            colored(
                "Successfully added group permissions",
                "green",
                attrs=["blink"],
            )
        )
        call_command("loaddata", "brands.json")
        print(
            colored(
                "Successfully added brands",
                "green",
                attrs=["blink"],
            )
        )
        call_command("loaddata", "models.json")
        print(
            colored(
                "Successfully added models",
                "green",
                attrs=["blink"],
            )
        )
        call_command("loaddata", "products.json")
        print(
            colored(
                "Successfully added products",
                "green",
                attrs=["blink"],
            )
        )
