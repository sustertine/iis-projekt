import great_expectations as ge
from great_expectations.checkpoint.types.checkpoint_result import CheckpointResult


def main():
    context = ge.get_context()
    result: CheckpointResult = context.run_checkpoint(checkpoint_name="air_quality")
    if not result["success"]:
        print(result)
        print("Data validation failed")
        return

    print("Data validation passed!")


if __name__ == "__main__":
    main()
