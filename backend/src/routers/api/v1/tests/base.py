"""Base test class for API endpoint testing."""

from uuid import UUID, uuid4
from core.types import CurrentUserData
import pytest

from tests.utils import token_admin_read_write, current_user_data_admin


class AbstractTestMixin:
    """Mixin to prevent pytest collection of abstract test classes."""

    def __init_subclass__(cls):
        # Mark as test only if not directly inheriting from AbstractTestMixin
        cls.__test__ = AbstractTestMixin not in cls.__bases__


class BaseTest:
    # __test__ = False
    """Base class for API endpoint tests with common fixtures and test methods.

    Subclasses must define these class attributes:
        crud: The CRUD class for this resource (e.g., PresentationCRUD)
        model: The SQLModel table model (e.g., Presentation)
        router_path: The API router path (e.g., "/api/v1/presentation")
        _test_data_single: Single test data dict for POST (e.g., one_test_presentation)
        _test_data_wrong: List of invalid test data dicts for negative tests (e.g., wrong_test_presentations)
        _test_data_many: List of test data dicts for bulk operations (e.g., many_test_presentations)
        _test_data_update: Update data dict for PUT (e.g., presentation_update_data)

    Optional attributes for hierarchical resources:
        _hierarchical_router_path: Path pattern with {parent_id} placeholder (e.g., "/api/v1/quiz/question/{parent_id}/message/")
        _parent_model: The SQLModel table model for parent (e.g., Question)
    """

    # Optional: Override in child classes that require parent resources
    _hierarchical_router_path = None
    _parent_model = None

    ## Fixtures
    @pytest.fixture(autouse=True)
    def setup(self, async_client, app_override_provide_http_token_payload):
        """Auto-inject common fixtures for all tests."""
        self.async_client = async_client
        self.app = app_override_provide_http_token_payload

    @pytest.fixture(scope="function")
    def test_data_single(self):
        """Provides single test data for POST."""
        return self._test_data_single

    @pytest.fixture(scope="function")
    def update_data(self):
        """Provides update data for PUT."""
        return self._test_data_update

    @pytest.fixture(scope="function")
    def test_data_wrong(self):
        """Provides invalid test data for negative tests."""
        return self._test_data_wrong

    @pytest.fixture(scope="function")
    async def added_resources(
        self,
        add_many_test_resources,
        mocked_provide_http_token_payload,
        access_to_one_parent,
    ):
        """
        Provides pre-added resources for tests.
        Returns a factory function that can be called with optional parent_id.
        If _parent_resource_type is defined, automatically creates a parent resource.
        """
        token_payload = None
        if not mocked_provide_http_token_payload:
            token_payload = token_admin_read_write
        else:
            token_payload = mocked_provide_http_token_payload

        async def _added_resources(parent_id: UUID = None):
            """Factory function to add resources with optional parent_id."""
            # If no parent_id provided but this resource requires a parent, create one
            if parent_id is None and self._parent_model is not None:
                parent_id = await access_to_one_parent(
                    self._parent_model, token_payload
                )

            return await add_many_test_resources(
                self.crud,
                self._test_data_many,
                token_payload,
                parent_id=parent_id,
            )

        # Return the factory function itself, not the result
        return _added_resources

    ## POST Tests
    async def run_post_success(
        self,
        test_data_single,
        mocked_provide_http_token_payload,
        access_to_one_parent=None,
    ):
        """Test successful POST creation."""
        # Determine which path to use (hierarchical or standalone)
        if self._hierarchical_router_path and self._parent_model:
            parent_id = await access_to_one_parent(
                self._parent_model, mocked_provide_http_token_payload
            )
            path = self._hierarchical_router_path.format(parent_id=parent_id)
        else:
            path = self.router_path

        response = await self.async_client.post(path, json=test_data_single)
        assert response.status_code == 201
        data = response.json()

        # Validate response matches Read model
        validated = self.model.Read(**data)
        assert validated is not None

        # Check all input fields are present in response
        for key, value in test_data_single.items():
            assert data[key] == value

    async def run_post_missing_auth(self, test_data_single, access_to_one_parent=None):
        """Test POST fails without authentication."""
        # For hierarchical resources, we still need the path format (even though auth will fail)
        if self._hierarchical_router_path and self._parent_model:
            # Create parent with admin token for the path, but don't use auth for the actual request
            parent_id = await access_to_one_parent(
                self._parent_model, token_admin_read_write
            )
            path = self._hierarchical_router_path.format(parent_id=parent_id)
        else:
            path = self.router_path

        response = await self.async_client.post(path, json=test_data_single)
        assert response.status_code == 401

    async def run_post_fails_authorization(
        self,
        test_data_single,
        mocked_provide_http_token_payload,
        access_to_one_parent=None,
    ):
        """Test POST fails without proper authorization."""
        # Determine which path to use
        if self._hierarchical_router_path and self._parent_model:
            parent_id = await access_to_one_parent(
                self._parent_model, mocked_provide_http_token_payload
            )
            path = self._hierarchical_router_path.format(parent_id=parent_id)
        else:
            path = self.router_path

        response = await self.async_client.post(path, json=test_data_single)
        assert response.status_code == 401

    async def run_post_invalid_data(
        self,
        test_data_wrong,
        mocked_provide_http_token_payload,
        access_to_one_parent=None,
    ):
        """Test POST with invalid data fails."""
        # Determine which path to use
        if self._hierarchical_router_path and self._parent_model:
            parent_id = await access_to_one_parent(
                self._parent_model, mocked_provide_http_token_payload
            )
            path = self._hierarchical_router_path.format(parent_id=parent_id)
        else:
            path = self.router_path

        for invalid_data in test_data_wrong:
            response = await self.async_client.post(path, json=invalid_data)
            assert response.status_code == 422  # Unprocessable Entity

    # async def run_post_with_parent_success(
    #     self, test_data_single, access_to_one_parent, mocked_provide_http_token_payload
    # ):
    #     """Test successful POST creation with parent resource."""
    #     if not self._hierarchical_router_path or not self._parent_model:
    #         pytest.skip("Hierarchical path or parent resource type not defined")

    #     # Get parent resource ID
    #     parent_id = await access_to_one_parent(
    #         self._parent_model, mocked_provide_http_token_payload
    #     )

    #     # Format the hierarchical path with parent_id
    #     path = self._hierarchical_router_path.format(parent_id=parent_id)

    #     response = await self.async_client.post(path, json=test_data_single)
    #     assert response.status_code == 201
    #     data = response.json()

    #     # Validate response matches Read model
    #     validated = self.model.Read(**data)
    #     assert validated is not None

    #     # Check all input fields are present in response
    #     for key, value in test_data_single.items():
    #         assert data[key] == value

    ## GET Tests
    async def run_get_all_success(
        self, added_resources, mocked_provide_http_token_payload
    ):
        """Test successful GET all resources."""
        resources = await added_resources()
        response = await self.async_client.get(self.router_path)

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) >= len(resources)

        # Validate each item matches Read model
        for item in data:
            validated = self.model.Read(**item)
            assert validated is not None

    async def run_get_all_missing_auth(self, added_resources):
        """Test GET all fails without authentication."""
        response = await self.async_client.get(self.router_path)
        assert response.status_code == 401

    async def run_get_all_fails_authorization(
        self, added_resources, mocked_provide_http_token_payload
    ):
        """Test GET all fails without proper authorization."""
        response = await self.async_client.get(self.router_path)
        assert response.status_code == 401

    async def run_get_by_id_not_found(self, mocked_provide_http_token_payload):
        """Test GET by ID returns 404 for non-existent resource."""
        fake_id = uuid4()

        response = await self.async_client.get(f"{self.router_path}{fake_id}")

        assert response.status_code == 404

    async def run_get_by_id_missing_auth(self, added_resources):
        """Test GET by ID fails without authentication."""
        resources = await added_resources()
        resource_id = resources[0].id

        response = await self.async_client.get(f"{self.router_path}{resource_id}")

        assert response.status_code == 401

    async def run_get_by_id_fails_authorization(
        self, added_resources, mocked_provide_http_token_payload
    ):
        """Test GET by ID fails without proper authorization."""
        resources = await added_resources()
        resource_id = resources[0].id

        response = await self.async_client.get(f"{self.router_path}{resource_id}")

        assert response.status_code == 401

    async def run_get_by_id_success(
        self, added_resources, mocked_provide_http_token_payload
    ):
        """Test successful GET by ID with authentication."""
        resources = await added_resources()
        resource_id = resources[0].id

        response = await self.async_client.get(f"{self.router_path}{resource_id}")

        assert response.status_code == 200
        data = response.json()

        # Validate response
        validated = self.model.Read(**data)
        assert validated is not None
        assert data["id"] == str(resource_id)

    async def run_get_public_by_id_success(
        self, add_one_test_access_policy, added_resources
    ):
        """Test successful public GET by ID without authentication."""
        resources = await added_resources()
        resource_id = resources[0].id
        current_user = CurrentUserData(**current_user_data_admin)
        await add_one_test_access_policy(
            {
                "resource_id": str(resource_id),
                "action": "read",
                "public": True,
            },
            current_user=current_user,
        )

        response = await self.async_client.get(
            f"{self.router_path}public/{resource_id}"
        )

        assert response.status_code == 200
        data = response.json()

        # Validate response
        validated = self.model.Read(**data)
        assert validated is not None
        assert data["id"] == str(resource_id)

    async def run_put_success(
        self, added_resources, update_data, mocked_provide_http_token_payload
    ):
        """Test successful PUT update."""
        resources = await added_resources()
        resource_id = resources[0].id

        response = await self.async_client.put(
            f"{self.router_path}{resource_id}",
            json=update_data,
        )

        assert response.status_code == 200
        data = response.json()

        # Validate response
        validated = self.model.Read(**data)
        assert validated is not None
        assert data["id"] == str(resource_id)

        # Check updated fields
        for key, value in update_data.items():
            assert data[key] == value

    async def run_put_not_found(self, update_data, mocked_provide_http_token_payload):
        """Test PUT returns 404 for non-existent resource."""
        fake_id = uuid4()

        response = await self.async_client.put(
            f"{self.router_path}{fake_id}",
            json=update_data,
        )

        assert response.status_code == 404

    async def run_put_missing_auth(self, added_resources, update_data):
        """Test PUT fails without authentication."""
        resources = await added_resources()
        resource_id = resources[0].id
        response = await self.async_client.put(
            f"{self.router_path}{resource_id}",
            json=update_data,
        )
        assert response.status_code == 401

    async def run_put_fails_authorization(
        self, added_resources, update_data, mocked_provide_http_token_payload
    ):
        """Test PUT fails without proper authorization."""
        resources = await added_resources()
        resource_id = resources[0].id

        response = await self.async_client.put(
            f"{self.router_path}{resource_id}",
            json=update_data,
        )
        assert response.status_code == 401

    async def run_put_fails_invalid_data(
        self, added_resources, test_data_wrong, mocked_provide_http_token_payload
    ):
        """Test PUT with invalid data fails."""
        resources = await added_resources()
        resource_id = resources[0].id

        response = await self.async_client.put(
            f"{self.router_path}{resource_id}",
            json=test_data_wrong,
        )
        assert response.status_code == 422  # Unprocessable Entity

    async def run_delete_success(
        self, added_resources, mocked_provide_http_token_payload
    ):
        """Test successful DELETE."""
        resources = await added_resources()
        resource_id = resources[0].id

        response = await self.async_client.delete(f"{self.router_path}{resource_id}")

        assert response.status_code == 200

        # Verify resource is deleted
        get_response = await self.async_client.get(f"{self.router_path}{resource_id}")
        assert get_response.status_code == 404

    async def run_delete_not_found(self, mocked_provide_http_token_payload):
        """Test DELETE returns 404 for non-existent resource."""
        fake_id = uuid4()

        response = await self.async_client.delete(f"{self.router_path}{fake_id}")

        assert response.status_code == 404

    async def run_delete_missing_auth(self, added_resources):
        """Test DELETE fails without authentication."""
        resources = await added_resources()
        resource_id = resources[0].id

        response = await self.async_client.delete(f"{self.router_path}{resource_id}")

        assert response.status_code == 401

    async def run_delete_fails_authorization(
        self, added_resources, mocked_provide_http_token_payload
    ):
        """Test DELETE fails without proper authorization."""
        resources = await added_resources()
        resource_id = resources[0].id

        response = await self.async_client.delete(f"{self.router_path}{resource_id}")

        assert response.status_code == 401
