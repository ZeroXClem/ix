from copy import deepcopy

import json
import pytest

from ix.chains.artifacts import SaveArtifact
from ix.task_log.models import Artifact, TaskLogMessage
from ix.task_log.tests.fake import fake_task

ARTIFACT_FROM_ARTIFACT = {
    "class_path": "ix.chains.artifacts.SaveArtifact",
    "config": {
        "artifact_from_key": "mock_artifact",
        "artifact_type": "test",
        "artifact_storage": "mock_write_to_file",
        "content_key": "artifact_content",
        "output_key": "generated_artifact",
    },
}


STATIC_ARTIFACT = {
    "class_path": "ix.chains.artifacts.SaveArtifact",
    "config": {
        "artifact_name": "test artifact",
        "artifact_key": "test_artifact",
        "artifact_description": "This is a test artifact generated by a test",
        "artifact_type": "test",
        "artifact_storage": "mock_write_to_file",
        "content_key": "artifact_content",
        "output_key": "generated_artifact",
    },
}


MOCK_CONTENT = {"foo": "bar"}
MOCK_ARTIFACT = artifact = dict(
    name="test artifact",
    key="test_artifact",
    description="this is a test artifact",
    identifier="test_artifact_001",
)


@pytest.mark.django_db
class TestSaveArtifact:
    def test_create_from_artifact(self, load_chain):
        chain = load_chain(ARTIFACT_FROM_ARTIFACT)
        assert isinstance(chain, SaveArtifact)

        result = chain.run(artifact_content=MOCK_CONTENT, mock_artifact=MOCK_ARTIFACT)
        artifact = Artifact.objects.get()
        assert result == str(artifact.id)
        assert artifact.name == "test artifact"
        assert artifact.key == "test_artifact"
        assert artifact.description == "this is a test artifact"
        assert artifact.storage["type"] == "mock_write_to_file"
        assert artifact.storage["id"] == "test_artifact_001"

    def test_create_static_artifact(self, load_chain):
        chain = load_chain(STATIC_ARTIFACT)
        assert isinstance(chain, SaveArtifact)

        result = chain.run(artifact_content=MOCK_CONTENT)
        artifact = Artifact.objects.get()
        assert result == str(artifact.id)
        assert artifact.name == "test artifact"
        assert artifact.key == "test_artifact"
        assert artifact.description == "This is a test artifact generated by a test"
        assert artifact.storage["type"] == "mock_write_to_file"
        assert artifact.storage["id"] == f"test_artifact_{chain.callbacks.think_msg.id}"

    @pytest.mark.parametrize("config", [ARTIFACT_FROM_ARTIFACT, STATIC_ARTIFACT])
    def test_artifact_storage_for_artifact(self, config, load_chain, tmp_path):
        """Test that file is written when artifact_storage is set to write_to_file"""
        config = deepcopy(config)
        config["config"]["artifact_storage"] = "write_to_file"
        temp_file = tmp_path / "temp_file.txt"
        config["config"]["identifier"] = str(temp_file)
        config["config"]["artifact_storage"] = "write_to_file"
        config["config"]["artifact_storage_id"] = str(temp_file)

        chain = load_chain(config)

        kwargs = {}
        if "artifact_from_key" in config["config"]:
            kwargs["mock_artifact"] = MOCK_ARTIFACT
        result = chain.run(artifact_content=MOCK_CONTENT, **kwargs)

        artifact = Artifact.objects.get()
        assert result == str(artifact.id)

        # assert file is written
        assert temp_file.is_file()

        # assert file contents are correct
        with open(temp_file, "r") as file:
            file_content = file.read()
        assert json.loads(file_content) == MOCK_CONTENT

    def test_artifact_content_path(self, load_chain, tmp_path):
        """
        Test mapping content with `content_path` jsonpath. This allows a value
        within the content object to be saved.
        """
        config = deepcopy(ARTIFACT_FROM_ARTIFACT)
        config["config"]["artifact_storage"] = "write_to_file"
        temp_file = tmp_path / "temp_file.txt"
        config["config"]["identifier"] = str(temp_file)
        config["config"]["content_path"] = "artifact_content.foo"
        config["config"]["artifact_storage"] = "write_to_file"
        config["config"]["artifact_storage_id"] = str(temp_file)

        chain = load_chain(config)

        kwargs = {}
        if "artifact_from_key" in config["config"]:
            kwargs["mock_artifact"] = MOCK_ARTIFACT
        result = chain.run(artifact_content=MOCK_CONTENT, **kwargs)

        artifact = Artifact.objects.get()
        assert result == str(artifact.id)

        # assert file is written
        assert temp_file.is_file()

        # assert file contents are correct
        with open(temp_file, "r") as file:
            file_content = file.read()
        assert file_content == "bar"

    @pytest.mark.parametrize("config", [ARTIFACT_FROM_ARTIFACT, STATIC_ARTIFACT])
    def test_artifact_type(self, config, load_chain):
        """Test that artifact_type will be set to the value in the config if set in config"""
        config = deepcopy(config)
        config["config"]["artifact_type"] = "custom_mock_type"
        chain = load_chain(config)

        kwargs = {}
        if "artifact_from_key" in config["config"]:
            kwargs["mock_artifact"] = MOCK_ARTIFACT

        result = chain.run(artifact_content=MOCK_CONTENT, **kwargs)

        artifact = Artifact.objects.get()
        msg = TaskLogMessage.objects.latest("created_at")
        assert result == str(artifact.id)
        assert artifact.artifact_type == "custom_mock_type"
        assert msg.content["artifact_type"] == "custom_mock_type"

    def test_artifact_parent_for_chat_task(self, load_chain):
        """
        Test that artifact parent is set to chain's task if it does not have a parent.
        This handles the case where the artifact is created by the main task
        for a chat.
        """
        chain = load_chain(ARTIFACT_FROM_ARTIFACT)

        result = chain.run(artifact_content=MOCK_CONTENT, mock_artifact=MOCK_ARTIFACT)
        artifact = Artifact.objects.get()
        msg = TaskLogMessage.objects.latest("created_at")
        assert result == str(artifact.id)
        assert msg.content["artifact_id"] == str(artifact.id)

    def test_artifact_for_subtask(self, task, mock_callback_manager, load_chain):
        """
        Test that artifact parent is set to the root task if the task has a parent.
        This handles the case where artifact is running in a subtask of the main task.
        """

        fake_task(parent=mock_callback_manager.task)
        subtask_manager = mock_callback_manager.child("subtask")
        chain = load_chain(ARTIFACT_FROM_ARTIFACT, subtask_manager)

        # fake_task(parent=task)
        # chain.mock_callback_manager.child("subtask")

        result = chain.run(artifact_content=MOCK_CONTENT, mock_artifact=MOCK_ARTIFACT)
        artifact = Artifact.objects.get()
        msg = TaskLogMessage.objects.latest("created_at")
        assert result == str(artifact.id)
        assert msg.content["artifact_id"] == str(artifact.id)
