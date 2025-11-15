"""Tests for workout library tools."""

import json
from unittest.mock import MagicMock

from httpx import Response

from intervals_icu_mcp.tools.workout_library import (
    add_workouts_to_plan,
    create_training_plan,
    delete_training_plan,
)


class TestCreateTrainingPlan:
    """Tests for create_training_plan tool."""

    async def test_create_training_plan_success(
        self,
        mock_config,
        respx_mock,
    ):
        """Test successful training plan creation."""
        # Create mock context with config
        mock_ctx = MagicMock()
        mock_ctx.get_state.return_value = mock_config

        # Mock response data
        mock_folder_data = {
            "id": 12345,
            "athlete_id": "i123456",
            "type": "PLAN",
            "name": "Marathon Training Plan",
            "description": "12-week marathon training plan",
            "visibility": "PRIVATE",
            "start_date_local": "2024-01-01",
            "num_workouts": 0,
        }

        # Mock the API endpoint
        respx_mock.post("/athlete/i123456/folders").mock(
            return_value=Response(200, json=mock_folder_data)
        )

        result = await create_training_plan(
            name="Marathon Training Plan",
            plan_type="PLAN",
            description="12-week marathon training plan",
            start_date="2024-01-01",
            visibility="PRIVATE",
            ctx=mock_ctx,
        )

        # Check for JSON response with expected fields
        import json

        response = json.loads(result)
        assert "data" in response
        assert response["data"]["id"] == 12345
        assert response["data"]["name"] == "Marathon Training Plan"
        assert response["data"]["type"] == "PLAN"
        assert response["data"]["visibility"] == "PRIVATE"
        assert response["data"]["start_date"] == "2024-01-01"

        # Check analysis section
        assert "analysis" in response
        assert response["analysis"]["type"] == "training_plan"
        assert "successfully" in response["analysis"]["message"].lower()

    async def test_create_folder_success(
        self,
        mock_config,
        respx_mock,
    ):
        """Test successful workout folder creation."""
        # Create mock context with config
        mock_ctx = MagicMock()
        mock_ctx.get_state.return_value = mock_config

        # Mock response data
        mock_folder_data = {
            "id": 54321,
            "athlete_id": "i123456",
            "type": "FOLDER",
            "name": "My Workouts",
            "visibility": "PRIVATE",
            "num_workouts": 0,
        }

        # Mock the API endpoint
        respx_mock.post("/athlete/i123456/folders").mock(
            return_value=Response(200, json=mock_folder_data)
        )

        result = await create_training_plan(
            name="My Workouts",
            plan_type="FOLDER",
            visibility="PRIVATE",
            ctx=mock_ctx,
        )

        # Check for JSON response with expected fields
        import json

        response = json.loads(result)
        assert "data" in response
        assert response["data"]["id"] == 54321
        assert response["data"]["name"] == "My Workouts"
        assert response["data"]["type"] == "FOLDER"

        # Check analysis section
        assert "analysis" in response
        assert response["analysis"]["type"] == "workout_folder"

    async def test_create_training_plan_invalid_type(
        self,
        mock_config,
    ):
        """Test error handling for invalid plan type."""
        # Create mock context with config
        mock_ctx = MagicMock()
        mock_ctx.get_state.return_value = mock_config

        result = await create_training_plan(
            name="Test Plan",
            plan_type="INVALID",
            ctx=mock_ctx,
        )

        # Check for error response
        import json

        response = json.loads(result)
        assert "error" in response
        assert "validation_error" in response["error"]["type"]

    async def test_create_training_plan_invalid_visibility(
        self,
        mock_config,
    ):
        """Test error handling for invalid visibility."""
        # Create mock context with config
        mock_ctx = MagicMock()
        mock_ctx.get_state.return_value = mock_config

        result = await create_training_plan(
            name="Test Plan",
            plan_type="PLAN",
            visibility="INVALID",
            ctx=mock_ctx,
        )

        # Check for error response
        import json

        response = json.loads(result)
        assert "error" in response
        assert "validation_error" in response["error"]["type"]


class TestAddWorkoutsToPlan:
    """Tests for add_workouts_to_plan tool."""

    async def test_add_workouts_to_plan_success(
        self,
        mock_config,
        respx_mock,
    ):
        """Test successful workout addition to plan."""
        # Create mock context with config
        mock_ctx = MagicMock()
        mock_ctx.get_state.return_value = mock_config

        # Mock workouts data
        workouts_json = json.dumps(
            [
                {
                    "name": "Easy Run",
                    "description": "30min Z2 HR",
                    "type": "Run",
                    "moving_time": 1800,
                    "day": 1,
                    "indoor": False,
                    "color": "blue",
                    "icu_training_load": 30,
                },
                {
                    "name": "Intervals",
                    "description": "Threshold intervals",
                    "type": "Ride",
                    "moving_time": 3600,
                    "day": 3,
                    "indoor": True,
                    "color": "red",
                    "icu_training_load": 85,
                },
            ]
        )

        # Mock response data
        mock_created_workouts = [
            {
                "id": 1001,
                "athlete_id": "i123456",
                "folder_id": 12345,
                "name": "Easy Run",
                "description": "30min Z2 HR",
                "type": "Run",
                "moving_time": 1800,
                "icu_training_load": 30,
                "indoor": False,
                "color": "blue",
            },
            {
                "id": 1002,
                "athlete_id": "i123456",
                "folder_id": 12345,
                "name": "Intervals",
                "description": "Threshold intervals",
                "type": "Ride",
                "moving_time": 3600,
                "icu_training_load": 85,
                "indoor": True,
                "color": "red",
            },
        ]

        # Mock the API endpoint
        respx_mock.post("/athlete/i123456/workouts/bulk").mock(
            return_value=Response(200, json=mock_created_workouts)
        )

        result = await add_workouts_to_plan(
            folder_id=12345,
            workouts=workouts_json,
            ctx=mock_ctx,
        )

        # Check for JSON response with expected fields
        response = json.loads(result)
        assert "data" in response
        assert "workouts" in response["data"]
        assert len(response["data"]["workouts"]) == 2

        # Check first workout
        assert response["data"]["workouts"][0]["id"] == 1001
        assert response["data"]["workouts"][0]["name"] == "Easy Run"
        assert response["data"]["workouts"][0]["type"] == "Run"
        assert response["data"]["workouts"][0]["duration_seconds"] == 1800
        assert response["data"]["workouts"][0]["training_load"] == 30

        # Check second workout
        assert response["data"]["workouts"][1]["id"] == 1002
        assert response["data"]["workouts"][1]["name"] == "Intervals"

        # Check summary
        assert "summary" in response["data"]
        assert response["data"]["summary"]["count"] == 2
        assert response["data"]["summary"]["total_duration_seconds"] == 5400
        assert response["data"]["summary"]["total_training_load"] == 115

        # Check analysis
        assert "analysis" in response
        assert response["analysis"]["workouts_created"] == 2
        assert response["analysis"]["folder_id"] == 12345

    async def test_add_workouts_invalid_json(
        self,
        mock_config,
    ):
        """Test error handling for invalid JSON."""
        # Create mock context with config
        mock_ctx = MagicMock()
        mock_ctx.get_state.return_value = mock_config

        result = await add_workouts_to_plan(
            folder_id=12345,
            workouts="invalid json {",
            ctx=mock_ctx,
        )

        # Check for error response
        response = json.loads(result)
        assert "error" in response
        assert "validation_error" in response["error"]["type"]
        assert "Invalid JSON" in response["error"]["message"]

    async def test_add_workouts_empty_array(
        self,
        mock_config,
    ):
        """Test error handling for empty workouts array."""
        # Create mock context with config
        mock_ctx = MagicMock()
        mock_ctx.get_state.return_value = mock_config

        result = await add_workouts_to_plan(
            folder_id=12345,
            workouts="[]",
            ctx=mock_ctx,
        )

        # Check for error response
        response = json.loads(result)
        assert "error" in response
        assert "validation_error" in response["error"]["type"]
        assert "cannot be empty" in response["error"]["message"]

    async def test_add_workouts_missing_required_field(
        self,
        mock_config,
    ):
        """Test error handling for missing required field."""
        # Create mock context with config
        mock_ctx = MagicMock()
        mock_ctx.get_state.return_value = mock_config

        # Missing "day" field
        workouts_json = json.dumps(
            [
                {
                    "name": "Easy Run",
                    "type": "Run",
                    "moving_time": 1800,
                    # "day" is missing
                }
            ]
        )

        result = await add_workouts_to_plan(
            folder_id=12345,
            workouts=workouts_json,
            ctx=mock_ctx,
        )

        # Check for error response
        response = json.loads(result)
        assert "error" in response
        assert "validation_error" in response["error"]["type"]
        assert "missing required field: day" in response["error"]["message"]


class TestDeleteTrainingPlan:
    """Tests for delete_training_plan tool."""

    async def test_delete_training_plan_success(
        self,
        mock_config,
        respx_mock,
    ):
        """Test successful training plan deletion."""
        # Create mock context with config
        mock_ctx = MagicMock()
        mock_ctx.get_state.return_value = mock_config

        # Mock existing folder data
        mock_folders = [
            {
                "id": 12345,
                "athlete_id": "i123456",
                "type": "PLAN",
                "name": "Test Plan",
                "description": "Test description",
                "visibility": "PRIVATE",
                "num_workouts": 10,
            }
        ]

        # Mock the API endpoints
        respx_mock.get("/athlete/i123456/folders").mock(
            return_value=Response(200, json=mock_folders)
        )
        respx_mock.delete("/athlete/i123456/folders/12345").mock(
            return_value=Response(204)  # DELETE typically returns 204 No Content
        )

        result = await delete_training_plan(
            folder_id=12345,
            ctx=mock_ctx,
        )

        # Check for JSON response with expected fields
        response = json.loads(result)
        assert "data" in response
        assert response["data"]["deleted"] is True
        assert response["data"]["folder_id"] == 12345
        assert response["data"]["name"] == "Test Plan"

        # Check analysis section
        assert "analysis" in response
        assert "workouts_deleted" in response["analysis"]
        assert response["analysis"]["workouts_deleted"] == 10

    async def test_delete_training_plan_not_found(
        self,
        mock_config,
        respx_mock,
    ):
        """Test error handling when folder not found."""
        # Create mock context with config
        mock_ctx = MagicMock()
        mock_ctx.get_state.return_value = mock_config

        # Mock empty folders list
        respx_mock.get("/athlete/i123456/folders").mock(return_value=Response(200, json=[]))

        result = await delete_training_plan(
            folder_id=99999,
            ctx=mock_ctx,
        )

        # Check for error response
        response = json.loads(result)
        assert "error" in response
        assert "not_found" in response["error"]["type"]
