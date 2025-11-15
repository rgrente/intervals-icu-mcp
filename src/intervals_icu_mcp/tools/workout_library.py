"""Workout library tools for Intervals.icu MCP server."""

from typing import Annotated, Any

from fastmcp import Context

from ..auth import ICUConfig
from ..client import ICUAPIError, ICUClient
from ..response_builder import ResponseBuilder


async def get_workout_library(
    ctx: Context | None = None,
) -> str:
    """Get workout library folders and training plans.

    Returns all workout folders and training plans available to you, including
    your personal workouts, shared workouts, and any training plans you follow.

    Each folder contains structured workouts that can be applied to your calendar.

    Returns:
        JSON string with workout folders/plans
    """
    assert ctx is not None
    config: ICUConfig = ctx.get_state("config")

    try:
        async with ICUClient(config) as client:
            folders = await client.get_workout_folders()

            if not folders:
                return ResponseBuilder.build_response(
                    data={"folders": [], "count": 0},
                    metadata={
                        "message": "No workout folders found. Create folders in Intervals.icu to organize your workouts."
                    },
                )

            folders_data: list[dict[str, Any]] = []
            for folder in folders:
                folder_item: dict[str, Any] = {
                    "id": folder.id,
                    "name": folder.name,
                }

                if folder.description:
                    folder_item["description"] = folder.description
                if folder.num_workouts:
                    folder_item["num_workouts"] = folder.num_workouts

                # Training plan info
                if folder.start_date_local:
                    folder_item["start_date"] = folder.start_date_local
                if folder.duration_weeks:
                    folder_item["duration_weeks"] = folder.duration_weeks
                if folder.hours_per_week_min or folder.hours_per_week_max:
                    folder_item["hours_per_week"] = {
                        "min": folder.hours_per_week_min,
                        "max": folder.hours_per_week_max,
                    }

                # Include workouts (children) if present
                if folder.children:
                    workouts: list[dict[str, Any]] = []
                    for workout in folder.children:
                        workout_data: dict[str, Any] = {
                            "id": workout.id,
                            "name": workout.name,
                        }
                        if workout.description:
                            workout_data["description"] = workout.description
                        if workout.type:
                            workout_data["type"] = workout.type
                        if workout.moving_time:
                            workout_data["duration_seconds"] = workout.moving_time
                        if workout.day is not None:
                            workout_data["day"] = workout.day
                        if workout.icu_training_load:
                            workout_data["training_load"] = workout.icu_training_load
                        if workout.icu_intensity:
                            workout_data["intensity_factor"] = workout.icu_intensity
                        if workout.indoor is not None:
                            workout_data["indoor"] = workout.indoor
                        if workout.color:
                            workout_data["color"] = workout.color

                        workouts.append(workout_data)

                    folder_item["workouts"] = workouts
                    folder_item["workouts_count"] = len(workouts)

                folders_data.append(folder_item)

            # Categorize folders
            training_plans = [f for f in folders if f.duration_weeks is not None]
            regular_folders = [f for f in folders if f.duration_weeks is None]

            summary = {
                "total_folders": len(folders),
                "training_plans": len(training_plans),
                "regular_folders": len(regular_folders),
                "total_workouts": sum(f.num_workouts or 0 for f in folders),
            }

            result_data = {
                "folders": folders_data,
                "summary": summary,
            }

            return ResponseBuilder.build_response(
                data=result_data,
                query_type="workout_library",
            )

    except ICUAPIError as e:
        return ResponseBuilder.build_error_response(e.message, error_type="api_error")
    except Exception as e:
        return ResponseBuilder.build_error_response(
            f"Unexpected error: {str(e)}", error_type="internal_error"
        )


async def get_workouts_in_folder(
    folder_id: Annotated[int, "Folder ID to get workouts from"],
    ctx: Context | None = None,
) -> str:
    """Get all workouts in a specific folder or training plan.

    Returns detailed information about all workouts stored in a folder,
    including their structure, intensity, and training load.

    Args:
        folder_id: ID of the folder to browse

    Returns:
        JSON string with workout details
    """
    assert ctx is not None
    config: ICUConfig = ctx.get_state("config")

    try:
        async with ICUClient(config) as client:
            workouts = await client.get_workouts_in_folder(folder_id)

            if not workouts:
                return ResponseBuilder.build_response(
                    data={"workouts": [], "count": 0, "folder_id": folder_id},
                    metadata={"message": f"No workouts found in folder {folder_id}"},
                )

            workouts_data: list[dict[str, Any]] = []
            for workout in workouts:
                workout_item: dict[str, Any] = {
                    "id": workout.id,
                    "name": workout.name,
                }

                if workout.description:
                    workout_item["description"] = workout.description
                if workout.type:
                    workout_item["type"] = workout.type

                # Workout metrics
                metrics: dict[str, Any] = {}
                if workout.moving_time:
                    metrics["duration_seconds"] = workout.moving_time
                if workout.distance:
                    metrics["distance_meters"] = workout.distance
                if workout.icu_training_load:
                    metrics["training_load"] = workout.icu_training_load
                if workout.icu_intensity:
                    metrics["intensity_factor"] = workout.icu_intensity
                if workout.joules:
                    metrics["joules"] = workout.joules
                if workout.joules_above_ftp:
                    metrics["joules_above_ftp"] = workout.joules_above_ftp

                if metrics:
                    workout_item["metrics"] = metrics

                # Other properties
                if workout.indoor is not None:
                    workout_item["indoor"] = workout.indoor
                if workout.color:
                    workout_item["color"] = workout.color

                workouts_data.append(workout_item)

            # Calculate summary
            total_duration = sum(w.moving_time or 0 for w in workouts)
            total_load = sum(w.icu_training_load or 0 for w in workouts)
            indoor_count = sum(1 for w in workouts if w.indoor)

            summary = {
                "total_workouts": len(workouts),
                "total_duration_seconds": total_duration,
                "total_training_load": total_load,
                "indoor_workouts": indoor_count,
            }

            result_data = {
                "folder_id": folder_id,
                "workouts": workouts_data,
                "summary": summary,
            }

            return ResponseBuilder.build_response(
                data=result_data,
                query_type="folder_workouts",
            )

    except ICUAPIError as e:
        return ResponseBuilder.build_error_response(e.message, error_type="api_error")
    except Exception as e:
        return ResponseBuilder.build_error_response(
            f"Unexpected error: {str(e)}", error_type="internal_error"
        )


async def create_training_plan(
    name: Annotated[str, "Name of the training plan"],
    plan_type: Annotated[
        str,
        "Type of folder: 'FOLDER' for workout folder or 'PLAN' for training plan",
    ] = "PLAN",
    description: Annotated[str | None, "Description of the plan"] = None,
    start_date: Annotated[
        str | None,
        "Start date in ISO format (YYYY-MM-DD) for training plans. If not specified for PLAN type, defaults to next Monday",
    ] = None,
    visibility: Annotated[str, "Visibility: 'PRIVATE' or 'PUBLIC'"] = "PRIVATE",
    workouts: Annotated[
        str | None,
        "Optional JSON array of workout definitions. Each workout should have: name, description, type (activity type), moving_time (seconds), day (day number in plan), and optionally: indoor (bool), color, icu_training_load, workout_doc (structured workout)",
    ] = None,
    ctx: Context | None = None,
) -> str:
    """Create a new workout folder or training plan with optional workouts.

    Creates a new folder to organize workouts or a complete training plan with schedule.
    Training plans can have start dates and automatic rollout settings. Workouts can
    optionally be added during plan creation.

    For training plans (type='PLAN'), if no start_date is provided, it will automatically
    be set to the next Monday. This ensures plans start at the beginning of a week.

    IMPORTANT: Workout descriptions must follow Intervals.icu Markdown format:
    - Section headers (Warmup/Main Set/Cooldown) on separate lines
    - Steps begin with "- " followed by duration and intensity
    - Duration: 5m, 30s, 1m30
    - Intensity for cycling: % of FTP (e.g., 85%, 95-105%)
    - Intensity for running/trail:
      * IMPORTANT: Cannot mix pace and HR in the same workout. Choose one mode for entire session.
      * For intensive flat intervals/VMA: Use PACE for entire workout (warmup, main set, cooldown)
        - Warmup: "Press lap 15m 60-75% pace" (typical duration: 15m)
        - Main Set: pace (e.g., 100-105% pace)
        - Cooldown: pace (e.g., "10m 60-70% pace", typical duration: 10m)
      * For all other workouts (easy runs, tempo, long runs, uphill/trail): Use HR for entire workout
        - Warmup: "Press lap 15m Z1-Z2 HR" (typical duration: 15m)
        - Main Set: HR zones (e.g., Z2 HR, Z3 HR, Z4 HR)
        - Cooldown: HR zones (e.g., "10m Z1-Z2 HR", typical duration: 10m)
      * NEVER use ramp for warmup or cooldown.
    - Zones: Z2, Z3 HR, Z2 Pace
    - Optional: cadence (90rpm), ramp (ramp 60-80%)
    - Repeats: use "Nx" on its own line before the block
    - Leave blank lines between sections

    Example cycling workout:
    Warmup
    - 10m ramp 55-75% FTP 90rpm

    Main Set 3x
    - 5m 90% FTP 95rpm
    - 3m 65% FTP 85rpm

    Cooldown
    - 10m ramp 75-55% FTP 85rpm

    Example running easy run (HR-based):
    Warmup
    - Press lap 15m Z1-Z2 HR

    Main Set
    - 30m Z2 HR

    Cooldown
    - 10m Z1-Z2 HR

    Example running VMA intervals on flat (pace for entire workout):
    Warmup
    - Press lap 15m 60-75% pace

    Main Set 6x
    - 3m 100-105% pace
    - 2m 70% pace

    Cooldown
    - 10m 60-70% pace

    Example trail/uphill workout (HR-based):
    Warmup
    - Press lap 15m Z1-Z2 HR

    Main Set 5x
    - 5m Z4 HR
    - 3m Z2 HR

    Cooldown
    - 10m Z1-Z2 HR

    Args:
        name: Name of the plan/folder
        plan_type: 'FOLDER' for simple workout folder or 'PLAN' for training plan
        description: Optional description
        start_date: Start date for training plans (YYYY-MM-DD format). Auto-set to next Monday if not provided for PLAN type
        visibility: 'PRIVATE' (default) or 'PUBLIC'
        workouts: Optional JSON string array of workout definitions

    Returns:
        JSON string with created plan/folder details and workouts if provided

    Example workouts JSON:
    [
      {
        "name": "Easy Run",
        "description": "Warmup\\n- Press lap 15m Z1-Z2 HR\\n\\nMain Set\\n- 30m Z2 HR\\n\\nCooldown\\n- 10m Z1-Z2 HR",
        "type": "Run",
        "moving_time": 1800,
        "day": 1,
        "indoor": false,
        "color": "blue",
        "icu_training_load": 30,
        "targets": ["HR"]
      }
    ]
    """
    assert ctx is not None
    config: ICUConfig = ctx.get_state("config")

    # Validate plan_type
    if plan_type not in ["FOLDER", "PLAN"]:
        return ResponseBuilder.build_error_response(
            "plan_type must be either 'FOLDER' or 'PLAN'",
            error_type="validation_error",
        )

    # Validate visibility
    if visibility not in ["PRIVATE", "PUBLIC"]:
        return ResponseBuilder.build_error_response(
            "visibility must be either 'PRIVATE' or 'PUBLIC'",
            error_type="validation_error",
        )

    # Parse and validate workouts if provided
    import json

    workouts_list: list[dict[str, Any]] | None = None
    if workouts:
        try:
            workouts_list = json.loads(workouts)
        except json.JSONDecodeError as e:
            return ResponseBuilder.build_error_response(
                f"Invalid JSON format: {str(e)}",
                error_type="validation_error",
            )

        if not isinstance(workouts_list, list):
            return ResponseBuilder.build_error_response(
                "workouts must be a JSON array",
                error_type="validation_error",
            )

        if len(workouts_list) == 0:
            return ResponseBuilder.build_error_response(
                "workouts array cannot be empty",
                error_type="validation_error",
            )

        # Validate each workout
        for i, workout in enumerate(workouts_list):
            if not isinstance(workout, dict):  # type: ignore[reportUnnecessaryIsInstance]
                return ResponseBuilder.build_error_response(
                    f"Workout at index {i} must be an object",
                    error_type="validation_error",
                )

            # Required fields
            required_fields = ["name", "type", "moving_time", "day"]
            for field in required_fields:
                if field not in workout:
                    return ResponseBuilder.build_error_response(
                        f"Workout at index {i} missing required field: {field}",
                        error_type="validation_error",
                    )

            # Set defaults for optional fields
            if "indoor" not in workout:
                workout["indoor"] = False
            if "attachments" not in workout:
                workout["attachments"] = []
            if "joules" not in workout:
                workout["joules"] = 0
            if "joules_above_ftp" not in workout:
                workout["joules_above_ftp"] = 0
            if "sub_type" not in workout:
                workout["sub_type"] = "NONE"

    # Auto-set start_date to next Monday if not provided for PLAN type
    from datetime import datetime, timedelta

    auto_set_date = False
    if plan_type == "PLAN" and not start_date:
        today = datetime.now().date()
        # Calculate days until next Monday (0=Monday, 6=Sunday)
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:  # If today is Monday
            days_until_monday = 7  # Set to next Monday
        next_monday = today + timedelta(days=days_until_monday)
        start_date = next_monday.isoformat()
        auto_set_date = True

    try:
        # Build folder data
        folder_data: dict[str, Any] = {
            "name": name,
            "type": plan_type,
            "visibility": visibility,
        }

        if description:
            folder_data["description"] = description

        if start_date:
            folder_data["start_date_local"] = start_date

        async with ICUClient(config) as client:
            folder = await client.create_folder(folder_data)

            # Build response data
            result_data: dict[str, Any] = {
                "id": folder.id,
                "name": folder.name,
                "type": folder.type,
                "visibility": folder.visibility,
            }

            if folder.description:
                result_data["description"] = folder.description
            if folder.start_date_local:
                result_data["start_date"] = folder.start_date_local
            if folder.num_workouts:
                result_data["num_workouts"] = folder.num_workouts

            # Create workouts if provided
            created_workouts = None
            if workouts_list:
                # Add folder_id to each workout
                for workout in workouts_list:
                    workout["folder_id"] = folder.id

                # Create workouts
                created_workouts = await client.bulk_create_workouts(workouts_list)

                # Add workouts to response
                workouts_data: list[dict[str, Any]] = []
                for workout in created_workouts:
                    workout_item: dict[str, Any] = {
                        "id": workout.id,
                        "name": workout.name,
                        "type": workout.type,
                    }

                    if workout.description:
                        workout_item["description"] = workout.description
                    if workout.moving_time:
                        workout_item["duration_seconds"] = workout.moving_time
                    if workout.icu_training_load:
                        workout_item["training_load"] = workout.icu_training_load
                    if workout.folder_id:
                        workout_item["folder_id"] = workout.folder_id

                    workouts_data.append(workout_item)

                # Calculate summary
                total_duration = sum(w.moving_time or 0 for w in created_workouts)
                total_load = sum(w.icu_training_load or 0 for w in created_workouts)

                result_data["workouts"] = workouts_data
                result_data["num_workouts"] = len(created_workouts)
                result_data["summary"] = {
                    "count": len(created_workouts),
                    "total_duration_seconds": total_duration,
                    "total_training_load": total_load,
                }

            # Add analysis for training plans
            analysis_data: dict[str, Any]
            if plan_type == "PLAN":
                analysis_data = {
                    "type": "training_plan",
                    "message": f"Training plan '{name}' created successfully",
                }
                if start_date:
                    if auto_set_date:
                        analysis_data["schedule"] = (
                            f"Plan starts on {start_date} (auto-set to next Monday)"
                        )
                    else:
                        analysis_data["schedule"] = f"Plan starts on {start_date}"
            else:
                analysis_data = {
                    "type": "workout_folder",
                    "message": f"Workout folder '{name}' created successfully",
                }

            # Add workout analysis if workouts were created
            if created_workouts:
                total_duration = sum(w.moving_time or 0 for w in created_workouts)
                total_load = sum(w.icu_training_load or 0 for w in created_workouts)
                analysis_data["workouts_created"] = len(created_workouts)
                analysis_data["total_duration_seconds"] = total_duration
                analysis_data["total_training_load"] = total_load

            return ResponseBuilder.build_response(
                data=result_data,
                analysis=analysis_data,
                query_type="create_plan",
            )

    except ICUAPIError as e:
        return ResponseBuilder.build_error_response(e.message, error_type="api_error")
    except Exception as e:
        return ResponseBuilder.build_error_response(
            f"Unexpected error: {str(e)}", error_type="internal_error"
        )


async def add_workouts_to_plan(
    folder_id: Annotated[int, "Folder/plan ID to add workouts to"],
    workouts: Annotated[
        str,
        "JSON array of workout definitions. Each workout should have: name, description, type (activity type), moving_time (seconds), day (day number in plan), and optionally: indoor (bool), color, icu_training_load, workout_doc (structured workout)",
    ],
    ctx: Context | None = None,
) -> str:
    """Add multiple workouts to an existing training plan or folder.

    Allows bulk creation of workouts in an existing plan. Each workout can be a simple description
    or a structured workout with specific intensity targets (power zones, HR zones, pace zones).

    IMPORTANT: Workout descriptions must follow Intervals.icu Markdown format:
    - Section headers (Warmup/Main Set/Cooldown) on separate lines
    - Steps begin with "- " followed by duration and intensity
    - Duration: 5m, 30s, 1m30
    - Intensity for cycling: % of FTP (e.g., 85%, 95-105%)
    - Intensity for running/trail:
      * IMPORTANT: Cannot mix pace and HR in the same workout. Choose one mode for entire session.
      * For intensive flat intervals/VMA: Use PACE for entire workout (warmup, main set, cooldown)
        - Warmup: "Press lap 15m 60-75% pace" (typical duration: 15m)
        - Main Set: pace (e.g., 100-105% pace)
        - Cooldown: pace (e.g., "10m 60-70% pace", typical duration: 10m)
      * For all other workouts (easy runs, tempo, long runs, uphill/trail): Use HR for entire workout
        - Warmup: "Press lap 15m Z1-Z2 HR" (typical duration: 15m)
        - Main Set: HR zones (e.g., Z2 HR, Z3 HR, Z4 HR)
        - Cooldown: HR zones (e.g., "10m Z1-Z2 HR", typical duration: 10m)
      * NEVER use ramp for warmup or cooldown.
    - Zones: Z2, Z3 HR, Z2 Pace
    - Optional: cadence (90rpm), ramp (ramp 60-80%)
    - Repeats: use "Nx" on its own line before the block
    - Leave blank lines between sections

    Example cycling workout:
    Warmup
    - 10m ramp 55-75% FTP 90rpm

    Main Set 3x
    - 5m 90% FTP 95rpm
    - 3m 65% FTP 85rpm

    Cooldown
    - 10m ramp 75-55% FTP 85rpm

    Example running easy run (HR-based):
    Warmup
    - Press lap 15m Z1-Z2 HR

    Main Set
    - 30m Z2 HR

    Cooldown
    - 10m Z1-Z2 HR

    Example running VMA intervals on flat (pace for entire workout):
    Warmup
    - Press lap 15m 60-75% pace

    Main Set 6x
    - 3m 100-105% pace
    - 2m 70% pace

    Cooldown
    - 10m 60-70% pace

    Example trail/uphill workout (HR-based):
    Warmup
    - Press lap 15m Z1-Z2 HR

    Main Set 5x
    - 5m Z4 HR
    - 3m Z2 HR

    Cooldown
    - 10m Z1-Z2 HR

    Args:
        folder_id: ID of the folder/plan to add workouts to
        workouts: JSON string array of workout definitions

    Returns:
        JSON string with created workouts details

    Example workouts JSON:
    [
      {
        "name": "Easy Run",
        "description": "Warmup\\n- Press lap 15m Z1-Z2 HR\\n\\nMain Set\\n- 30m Z2 HR\\n\\nCooldown\\n- 10m Z1-Z2 HR",
        "type": "Run",
        "moving_time": 1800,
        "day": 1,
        "indoor": false,
        "color": "blue",
        "icu_training_load": 30,
        "targets": ["HR"]
      }
    ]
    """
    assert ctx is not None
    config: ICUConfig = ctx.get_state("config")

    # Parse workouts JSON
    import json
    from typing import cast

    workouts_list: list[dict[str, Any]]
    try:
        parsed: Any = json.loads(workouts)
        if not isinstance(parsed, list):
            return ResponseBuilder.build_error_response(
                "workouts must be a JSON array",
                error_type="validation_error",
            )
        # Cast to proper type after validation
        workouts_list = cast(list[dict[str, Any]], parsed)
    except json.JSONDecodeError as e:
        return ResponseBuilder.build_error_response(
            f"Invalid JSON format: {str(e)}",
            error_type="validation_error",
        )

    if len(workouts_list) == 0:
        return ResponseBuilder.build_error_response(
            "workouts array cannot be empty",
            error_type="validation_error",
        )

    # Validate and enrich each workout with folder_id
    for i, workout in enumerate(workouts_list):
        if not isinstance(workout, dict):  # type: ignore[reportUnnecessaryIsInstance]
            return ResponseBuilder.build_error_response(
                f"Workout at index {i} must be an object",
                error_type="validation_error",
            )

        # Required fields
        required_fields = ["name", "type", "moving_time", "day"]
        for field in required_fields:
            if field not in workout:
                return ResponseBuilder.build_error_response(
                    f"Workout at index {i} missing required field: {field}",
                    error_type="validation_error",
                )

        # Set folder_id for each workout
        workout["folder_id"] = folder_id

        # Set defaults for optional fields
        if "indoor" not in workout:
            workout["indoor"] = False
        if "attachments" not in workout:
            workout["attachments"] = []
        if "joules" not in workout:
            workout["joules"] = 0
        if "joules_above_ftp" not in workout:
            workout["joules_above_ftp"] = 0
        if "sub_type" not in workout:
            workout["sub_type"] = "NONE"

    try:
        async with ICUClient(config) as client:
            created_workouts = await client.bulk_create_workouts(workouts_list)

            # Build response data
            workouts_data: list[dict[str, Any]] = []
            for workout in created_workouts:
                workout_item: dict[str, Any] = {
                    "id": workout.id,
                    "name": workout.name,
                    "type": workout.type,
                }

                if workout.description:
                    workout_item["description"] = workout.description
                if workout.moving_time:
                    workout_item["duration_seconds"] = workout.moving_time
                if workout.icu_training_load:
                    workout_item["training_load"] = workout.icu_training_load
                if workout.folder_id:
                    workout_item["folder_id"] = workout.folder_id

                workouts_data.append(workout_item)

            # Calculate summary
            total_duration = sum(w.moving_time or 0 for w in created_workouts)
            total_load = sum(w.icu_training_load or 0 for w in created_workouts)

            analysis_data = {
                "workouts_created": len(created_workouts),
                "total_duration_seconds": total_duration,
                "total_training_load": total_load,
                "folder_id": folder_id,
            }

            result_data = {
                "workouts": workouts_data,
                "summary": {
                    "count": len(created_workouts),
                    "total_duration_seconds": total_duration,
                    "total_training_load": total_load,
                },
            }

            return ResponseBuilder.build_response(
                data=result_data,
                analysis=analysis_data,
                query_type="add_workouts_to_plan",
            )

    except ICUAPIError as e:
        return ResponseBuilder.build_error_response(e.message, error_type="api_error")
    except Exception as e:
        return ResponseBuilder.build_error_response(
            f"Unexpected error: {str(e)}", error_type="internal_error"
        )


async def delete_training_plan(
    folder_id: Annotated[int, "ID of the folder/plan to delete"],
    ctx: Context | None = None,
) -> str:
    """Delete a workout folder or training plan.

    Permanently deletes a training plan or workout folder. This action cannot be undone.
    All workouts within the folder/plan will also be deleted.

    Args:
        folder_id: ID of the folder/plan to delete

    Returns:
        JSON string confirming deletion
    """
    assert ctx is not None
    config: ICUConfig = ctx.get_state("config")

    try:
        async with ICUClient(config) as client:
            # First, fetch the folder to get its name for the confirmation message
            folders = await client.get_workout_folders()
            folder_to_delete = None
            for folder in folders:
                if folder.id == folder_id:
                    folder_to_delete = folder
                    break

            if not folder_to_delete:
                return ResponseBuilder.build_error_response(
                    f"Folder/plan with ID {folder_id} not found",
                    error_type="not_found",
                )

            folder_name = folder_to_delete.name
            folder_type = folder_to_delete.type or "FOLDER"
            num_workouts = folder_to_delete.num_workouts or 0

            # Delete the folder
            await client.delete_folder(folder_id)

            # Build response
            result_data = {
                "deleted": True,
                "folder_id": folder_id,
                "name": folder_name,
                "type": folder_type,
            }

            analysis_data = {
                "message": f"Successfully deleted {folder_type.lower()} '{folder_name}'",
                "workouts_deleted": num_workouts,
            }

            return ResponseBuilder.build_response(
                data=result_data,
                analysis=analysis_data,
                query_type="delete_plan",
            )

    except ICUAPIError as e:
        return ResponseBuilder.build_error_response(e.message, error_type="api_error")
    except Exception as e:
        return ResponseBuilder.build_error_response(
            f"Unexpected error: {str(e)}", error_type="internal_error"
        )
