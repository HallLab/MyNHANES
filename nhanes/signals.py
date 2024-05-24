from django.db.models.signals import post_save
from django.dispatch import receiver
# from django.conf import settings
from .models import DatasetControl, Data, Dataset, Cycle, SystemConfig


@receiver(post_save, sender=DatasetControl)
def handle_deletion(sender, instance, **kwargs):
    if instance.status == 'delete':
        Data.objects.filter(
            dataset=instance.dataset,
            cycle=instance.cycle
            ).delete()
        print(
            f"All data for {instance.dataset.dataset} in cycle \
                {instance.cycle.cycle} has been deleted due \
                to status 'delete'."
            )  # noqa E501

        instance.status = 'pending'
        instance.save()


@receiver(post_save, sender=Dataset)
def create_dataset_controls_by_dataset(sender, instance, created, **kwargs):
    if created:
        auto_create = SystemConfig.objects.filter(
            config_key='auto_create_dataset_controls'
            ).first()
        if auto_create and str(auto_create.config_value).lower() == 'true':
            cycles = Cycle.objects.all()
            for cycle in cycles:
                DatasetControl.objects.create(
                    dataset=instance,
                    cycle=cycle,
                    status='standby'  # Status inicial
                )
            print("DatasetControls created for all cycles.")


@receiver(post_save, sender=Cycle)
def create_dataset_controls_by_cycles(sender, instance, created, **kwargs):
    if created:
        auto_create = SystemConfig.objects.filter(
            config_key='auto_create_dataset_controls'
            ).first()
        if auto_create and str(auto_create.config_value).lower() == 'true':
            datasets = Dataset.objects.all()
            for dataset in datasets:
                DatasetControl.objects.create(
                    dataset=dataset,
                    cycle=instance,
                    status='standby'  # Status inicial
                )
            print("DatasetControls created for all Datasets.")
