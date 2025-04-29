from injector import Binder, Module, inject, singleton

from standalone_taskweaver.code_interpreter.code_executor import CodeExecutor
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.module.tracing import Tracing
from standalone_taskweaver.session.session import SessionMetadata


class ExecutionServiceModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(CodeExecutor, to=CodeExecutor, scope=singleton)


class ExecutionService:
    @inject
    def __init__(
        self,
        session_metadata: SessionMetadata,
        logger: TelemetryLogger,
        tracing: Tracing,
    ) -> None:
        self.session_metadata = session_metadata
        self.logger = logger
        self.tracing = tracing

