from django.db.models.signals import post_save
from django.dispatch import receiver
from nhanes.models import WorkProcess, RawData, SystemConfig, Dataset, Cycle
from nhanes.utils.logs import logger, start_logger


@receiver(post_save, sender=WorkProcess)
def handle_deletion(sender, instance, **kwargs):
    if instance.status == 'delete':

        # Start Log monitor
        log_file = __name__
        log = start_logger(log_file)
        logger(log, "s", "Deleting data due to status 'delete'.")

        try:
            # Attempt to delete the RawData
            deleted_count, _ = RawData.objects.filter(
                dataset=instance.dataset,
                cycle=instance.cycle
            ).delete()

            # Log the successful deletion
            msm = f"Successfully deleted {deleted_count} records for {instance.dataset.dataset} in cycle {instance.cycle.cycle} due to status 'delete'."  # noqa E501
            logger(log, "i", msm)

            # Update the WorkProcess instance
            instance.status = 'pending'
            instance.chk_raw = False
            instance.chk_normalization = False
            instance.records_raw = 0
            instance.n_samples = 0
            instance.source_file_size = 0
            instance.time_raw = 0
            instance.save(update_fields=[
                'status', 'chk_raw', 'chk_normalization', 
                'records_raw', 'n_samples', 'source_file_size', 'time_raw'
            ])

        except Exception as e:
            # Log any errors that occur during the deletion process
            msm = f"Error occurred while deleting data for {instance.dataset.dataset} in cycle {instance.cycle.cycle}: {e}"  # noqa E501
            logger(log, "e", msm)
            # Optionally, update the status to reflect that an error occurred
            instance.status = 'error'
            instance.save(update_fields=['status'])

        # TODO: Add NormalizationData


@receiver(post_save, sender=Dataset)
def create_workprocess_by_dataset(sender, instance, created, **kwargs):
    if created:
        # Start Log monitor
        log_file = __name__
        log = start_logger(log_file)
        logger(log, "i", "Start Signal create_workprocess_by_dataset.")

        auto_create = SystemConfig.objects.filter(
            config_key='auto_create_workprocess'
            ).first()
        if auto_create and str(auto_create.config_value).lower() == 'true':
            cycles = Cycle.objects.all()
            for cycle in cycles:
                WorkProcess.objects.create(
                    dataset=instance,
                    cycle=cycle,
                    status='standby'  # Status inicial
                )
            msm = "Work Process created for all cycles."
            logger(log, "s", msm)  # TODO: add the model object to the log


@receiver(post_save, sender=Cycle)
def create_workprocess_by_cycles(sender, instance, created, **kwargs):
    if created:
        # Start Log monitor
        log_file = __name__
        log = start_logger(log_file)
        logger(log, "i", "Start Signal create_workprocess_by_dataset.")

        auto_create = SystemConfig.objects.filter(
            config_key='auto_create_workprocess'
            ).first()
        if auto_create and str(auto_create.config_value).lower() == 'true':
            datasets = Dataset.objects.all()
            for dataset in datasets:
                WorkProcess.objects.create(
                    dataset=dataset,
                    cycle=instance,
                    status='standby'  # Status inicial
                )
            msm = "Work Process created for all dataset."
            logger(log, "s", msm)  
            # TODO: add the model object to the log
            # logger(
            # log,
            # "s",
            # "Started WorkProcessMasterData",
            # content_object=qs_wp.first()
            # )
