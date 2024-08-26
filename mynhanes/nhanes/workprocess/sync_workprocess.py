import time
from nhanes.models import DatasetCycle, WorkProcessNhanes, Dataset, Cycle
from nhanes.utils.logs import logger, start_logger


def check_and_sync_workprocess():
    # start Log monitor
    log_file = __name__
    v_time_start_process = time.time()
    log = start_logger(log_file)
    logger(log, "s", "Started Check and Sync WorkProcess")

    dataset_cycles = DatasetCycle.objects.all()

    for ds_cycle in dataset_cycles:
        if not WorkProcessNhanes.objects.filter(datasetcycle=ds_cycle).exists():
            WorkProcessNhanes.objects.create(
                datasetcycle=ds_cycle,
                cycle=ds_cycle.cycle,
                dataset=ds_cycle.dataset,
                status="standby"
            )
            logger(
                log,
                "i",
                f"WorkProcess created for {ds_cycle.dataset} - {ds_cycle.cycle}"
            )

    total_time = time.time() - v_time_start_process

    logger(
        log,
        "s",
        f"Check and Sync WorkProcess completed in {total_time} seconds"
    )

    return True


def check_and_sync_datasetcycle():
    # start Log monitor
    log_file = __name__
    v_time_start_process = time.time()
    log = start_logger(log_file)
    logger(log, "s", "Started Check and Sync DatasetCycle")

    try:
        datasets = Dataset.objects.all()
        cycles = Cycle.objects.all()
    except Exception as e:
        msm = f"Error getting datasets and cycles: {e}"
        logger(log, "e", msm)

    try:
        for dataset in datasets:
            for cycle in cycles:
                DatasetCycle.objects.get_or_create(
                    dataset=dataset,
                    cycle=cycle,
                    defaults={
                        'has_dataset': False
                    }
                )

        total_time = time.time() - v_time_start_process
        msm = f"DatasetCycle created for all datasets and cycles in {total_time} seconds".format(total_time)  # noqa E501
        logger(log, "s", msm)
        return True

    except Exception as e:
        msm = f"Error to create DataControl data: {e}"
        logger(log, "e", msm)
        return False
