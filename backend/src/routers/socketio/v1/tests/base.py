"""Base test class for SocketIO namespace testing."""


class BaseSocketIOTest:
    """Base class for SocketIO namespace tests with reusable test methods.

    Subclasses should define these class attributes:
        namespace_path: The namespace path (e.g., "/message")
        crud: The CRUD class for this resource
        model: The model class (with Create, Read, Update models)
        _test_data_single: Single test data dict
        _test_data_many: List of test data dicts
        _test_data_update: Update data dict
        _parent_model: Optional parent model for hierarchical resources
    """

    namespace_path = None
    crud = None
    model = None
    _test_data_single = None
    _test_data_many = None
    _test_data_update = None
    _parent_model = None

    # TBD: refactor to accept an argument if the callback on connect is configured to return all or not.
    # see below
    # TBD: reafctor to accept an argument if the connection is established
    # with query parameter "request-access-data"
    # if yes, check for returning "last_modified", "created_at", "access_right"
    # and if user is logged in also "access_policies"

    def client_config(self):
        """Returns the client configuration for this namespace."""
        return [
            {
                "namespace": self.namespace_path,
                "events": ["transferred", "deleted", "status"],
            }
        ]

    async def helper_submit_data(
        self,
        socketio_test_client,
        session_ids=None,
        access_to_one_parent=None,
    ):
        """Helper method to submit data via the submit event."""
        session_id = None
        if session_ids is not None:
            session_id = session_ids[0]

        connection = await socketio_test_client(
            client_config=self.client_config(),
            session_id=session_id,
        )
        token_payload = connection.token_payload()

        # If hierarchical, create parent
        parent_id = None
        if self._parent_model and access_to_one_parent:
            parent_id = await access_to_one_parent(self._parent_model, token_payload)

        await connection.connect()
        await connection.client.sleep(0.2)

        # Submit new resource
        test_data = {**self._test_data_single}
        submit_data = {"payload": test_data}

        if token_payload is None:
            submit_data["public"] = True
        if parent_id:
            submit_data["parent_id"] = str(parent_id)

        await connection.client.emit(
            "submit",
            submit_data,
            namespace=self.namespace_path,
        )
        await connection.client.sleep(0.5)

        return connection

    async def run_submit_create_success(
        self,
        socketio_test_client,
        session_ids=None,
        access_to_one_parent=None,
    ):
        """Test successful resource creation via submit event."""
        connection = await self.helper_submit_data(
            socketio_test_client,
            session_ids,
            access_to_one_parent,
        )

        # Check status event for creation success
        status_data = connection.responses("status", self.namespace_path)
        assert len(status_data) >= 1

        # Find the created status
        created_status = None
        for status in status_data:
            if isinstance(status, dict) and status.get("success") == "created":
                created_status = status
                break

        assert created_status is not None, f"No 'created' status found in {status_data}"
        assert "id" in created_status
        assert "submitted_id" in created_status

        # Verify the created resource exists and has correct data
        assert created_status["id"] is not None

        await connection.client.disconnect()

    async def run_submit_create_fails(
        self,
        socketio_test_client,
        session_ids=None,
        access_to_one_parent=None,
    ):
        """Test resource creation error via submit event."""
        connection = await self.helper_submit_data(
            socketio_test_client,
            session_ids,
            access_to_one_parent,
        )

        # Check status event for creation success
        status_data = connection.responses("status", self.namespace_path)
        assert len(status_data) >= 1

        # Find the created status
        created_status = None
        for status in status_data:
            if (
                isinstance(status, dict)
                and status.get("error") == f"403: {self.model.__name__} - Forbidden."
            ):
                created_status = status
                break

        assert created_status is not None, f"No 'error' status found in {status_data}"

        await connection.client.disconnect()

    async def run_submit_update_success(
        self,
        socketio_test_client,
        add_one_test_resource,
        session_ids,
        access_to_one_parent=None,
    ):
        """Test successful resource update via submit event."""
        connection = await socketio_test_client(
            client_config=self.client_config(),
            session_id=session_ids[0],
        )

        # Create parent if needed
        parent_id = None
        if self._parent_model and access_to_one_parent:
            parent_id = await access_to_one_parent(
                self._parent_model, connection.token_payload()
            )

        # Create initial resource
        current_user = await connection.current_user()
        resource = await add_one_test_resource(
            self.crud,
            self._test_data_single,
            current_user,
            parent_id=parent_id,
        )

        await connection.connect()
        await connection.client.sleep(0.2)

        # Submit update
        update_data = {**self._test_data_update, "id": str(resource.id)}
        await connection.client.emit(
            "submit",
            {"payload": update_data},
            namespace=self.namespace_path,
        )
        await connection.client.sleep(0.5)

        # TBD: refactor to accept an argument if the callback on connect is configured to return all or not.
        # Check transferred event
        transfer_data = connection.responses("transferred", self.namespace_path)
        assert (
            len(transfer_data) == 2
        )  # one for connect (get_all on connect), one for update
        assert transfer_data[0]["id"] == str(resource.id)

        # Verify original fields
        for key, value in self._test_data_single.items():
            assert transfer_data[0][key] == value

        # Verify updated fields
        assert transfer_data[1]["id"] == str(resource.id)
        for key, value in self._test_data_update.items():
            assert transfer_data[1][key] == value

        await connection.client.disconnect()

    async def run_delete_success(
        self,
        socketio_test_client,
        add_one_test_resource,
        session_ids,
        access_to_one_parent=None,
    ):
        """Test successful resource deletion via delete event."""
        connection = await socketio_test_client(
            client_config=self.client_config(),
            session_id=session_ids[0],
        )

        # Create parent if needed
        parent_id = None
        if self._parent_model and access_to_one_parent:
            parent_id = await access_to_one_parent(
                self._parent_model, connection.token_payload()
            )

        # Create initial resource
        current_user = await connection.current_user()
        resource = await add_one_test_resource(
            self.crud,
            self._test_data_single,
            current_user,
            parent_id=parent_id,
        )

        await connection.connect()
        await connection.client.sleep(0.2)

        # Delete resource
        await connection.client.emit(
            "delete",
            str(resource.id),
            namespace=self.namespace_path,
        )
        await connection.client.sleep(0.5)

        # Check status event for deletion success
        status_data = connection.responses("status", self.namespace_path)
        assert len(status_data) >= 1

        # Find the deleted status
        deleted_status = None
        for status in status_data:
            if isinstance(status, dict) and status.get("success") == "deleted":
                deleted_status = status
                break

        assert deleted_status is not None, f"No 'deleted' status found in {status_data}"
        assert deleted_status["id"] == str(resource.id)

        # Check deleted event
        deleted_data = connection.responses("deleted", self.namespace_path)
        assert len(deleted_data) == 1
        assert deleted_data[0] == str(resource.id)

        await connection.client.disconnect()

    async def run_share_success(
        self,
        socketio_test_client,
        add_one_test_resource,
        add_one_test_group,
        register_one_identity,
        session_ids,
        access_to_one_parent=None,
    ):
        """Test successful resource sharing via share event."""
        from models.identity import Group

        connection = await socketio_test_client(
            client_config=self.client_config(),
            session_id=session_ids[0],
        )

        # Create parent if needed
        parent_id = None
        if self._parent_model and access_to_one_parent:
            parent_id = await access_to_one_parent(
                self._parent_model, connection.token_payload()
            )

        # Create resource
        current_user = await connection.current_user()
        resource = await add_one_test_resource(
            self.crud,
            self._test_data_single,
            current_user,
            parent_id=parent_id,
        )

        # Create group to share with
        group = await add_one_test_group(
            {"name": "Test Group", "description": "Test"},
            current_user,
        )
        await register_one_identity(group.id, Group)

        await connection.connect()
        await connection.client.sleep(0.2)

        # Share resource
        await connection.client.emit(
            "share",
            {
                "resource_id": str(resource.id),
                "identity_id": str(group.id),
                "action": "read",
            },
            namespace=self.namespace_path,
        )
        await connection.client.sleep(0.5)

        # Check status event (sharing confirmation)
        status_data = connection.responses("status", self.namespace_path)
        assert len(status_data) >= 1
        # Check for success or shared message in status
        assert any(
            "success" in str(s).lower() or "shared" in str(s).lower()
            for s in status_data
        )

        await connection.client.disconnect()
