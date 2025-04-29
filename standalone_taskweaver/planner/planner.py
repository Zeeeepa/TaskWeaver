import json
import os
from typing import Dict, List, Optional, Set, Tuple

from injector import inject

from standalone_taskweaver.code_interpreter import CodeInterpreter
from standalone_taskweaver.llm import LLMApi
from standalone_taskweaver.llm.util import ChatMessageType, format_chat_message
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.memory import Attachment, Memory, Post, Round, RoundCompressor
from standalone_taskweaver.memory.attachment import AttachmentType
from standalone_taskweaver.memory.experience import ExperienceGenerator
from standalone_taskweaver.memory.type_vars import SharedMemoryEntryType
from standalone_taskweaver.module.event_emitter import PostEventProxy, SessionEventEmitter
from standalone_taskweaver.module.tracing import Tracing, tracing_decorator
from standalone_taskweaver.role import PostTranslator, Role
from standalone_taskweaver.role.role import RoleConfig
from standalone_taskweaver.utils import read_yaml


class PlannerConfig(RoleConfig):
    def _configure(self) -> None:
        self._set_name("planner")
        self.role_name = self._get_str("role_name", "Planner")
        self.prompt_file_path = self._get_path(
            "prompt_file_path",
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "planner_prompt.yaml",
            ),
        )
        self.prompt_compression = self._get_bool("prompt_compression", False)
        self.compression_prompt_path = self._get_path(
            "compression_prompt_path",
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "compression_prompt.yaml",
            ),
        )
        self.llm_alias = self._get_str("llm_alias", default="", required=False)


class Planner(Role):
    @inject
    def __init__(
        self,
        config: PlannerConfig,
        logger: TelemetryLogger,
        event_emitter: SessionEventEmitter,
        tracing: Tracing,
        llm_api: LLMApi,
        round_compressor: RoundCompressor,
        post_translator: PostTranslator,
        experience_generator: ExperienceGenerator,
        code_interpreter: CodeInterpreter,
    ):
        super().__init__(config, logger, tracing, event_emitter)
        self.config = config
        self.llm_api = llm_api
        self.code_interpreter = code_interpreter

        self.role_name = self.config.role_name
        self.alias = self.role_name

        self.post_translator = post_translator
        self.prompt_data = read_yaml(self.config.prompt_file_path)

        self.instruction_template = self.prompt_data["content"]
        self.conversation_head_template = self.prompt_data["conversation_head"]
        self.user_message_head_template = self.prompt_data["user_message_head"]
        self.response_json_schema = json.loads(self.prompt_data["response_json_schema"])

        self.round_compressor: RoundCompressor = round_compressor
        self.compression_template = read_yaml(self.config.compression_prompt_path)["content"]

        self.experience_generator = experience_generator

        self.logger.info("Planner initialized successfully")

    def compose_sys_prompt(self, context: str):
        return self.instruction_template.format(
            ENVIRONMENT_CONTEXT=context,
            ROLE_NAME=self.role_name,
            RESPONSE_JSON_SCHEMA=json.dumps(self.response_json_schema),
        )

    def get_env_context(self):
        return f"- Code Interpreter: {self.code_interpreter.get_intro()}"

    def compose_prompt(
        self,
        rounds: List[Round],
    ) -> List[ChatMessageType]:
        experiences = self.format_experience(
            template=self.prompt_data["experience_instruction"],
        )

        chat_history = [
            format_chat_message(
                role="system",
                message=f"{self.compose_sys_prompt(context=self.get_env_context())}" f"\\n{experiences}",
            ),
        ]

        for i, example in enumerate(self.examples):
            chat_history.extend(
                self.compose_conversation(example.rounds),
            )

        summary = None
        if self.config.prompt_compression:
            summary, rounds = self.round_compressor.compress_rounds(
                rounds,
                rounds_formatter=lambda _rounds: str(
                    self.compose_conversation(_rounds),
                ),
                prompt_template=self.compression_template,
            )

        chat_history.extend(
            self.compose_conversation(
                rounds,
                summary=summary,
            ),
        )
        return chat_history

    def format_attachment(self, attachment: Attachment):
        if attachment.type == AttachmentType.thought and "{ROLE_NAME}" in attachment.content:
            return attachment.content.format(ROLE_NAME=self.role_name)
        else:
            return attachment.content

    def compose_conversation(
        self,
        rounds: List[Round],
        summary: Optional[str] = None,
    ) -> List[ChatMessageType]:
        chat_history: List[ChatMessageType] = []
        ignored_types = [
            AttachmentType.init_plan,
            AttachmentType.plan,
            AttachmentType.current_plan_step,
        ]

        is_first_post = True
        for round_index, conversation_round in enumerate(rounds):
            for post_index, post in enumerate(conversation_round.post_list):
                # compose user query
                user_message = ""
                assistant_message = ""
                is_final_post = round_index == len(rounds) - 1 and post_index == len(conversation_round.post_list) - 1
                if is_first_post:
                    user_message = (
                        self.conversation_head_template.format(
                            SUMMARY="None" if summary is None else summary,
                            ROLE_NAME=self.role_name,
                        )
                        + "\\n"
                    )
                    is_first_post = False

                if post.send_from == "User" and post.send_to == self.alias:
                    user_message += self.user_message_head_template.format(
                        MESSAGE=post.message,
                    )
                elif post.send_from == self.alias and post.send_to == "CodeInterpreter":
                    assistant_message = self.post_translator.post_to_raw_text(
                        post=post,
                        content_formatter=self.format_attachment,
                        if_format_message=True,
                        if_format_send_to=True,
                        ignored_types=ignored_types,
                    )
                elif post.send_from == "CodeInterpreter" and post.send_to == self.alias:
                    user_message += self.user_message_head_template.format(
                        MESSAGE=post.message,
                    )
                elif post.send_from == self.alias and post.send_to == "User":
                    assistant_message = self.post_translator.post_to_raw_text(
                        post=post,
                        content_formatter=self.format_attachment,
                        if_format_message=True,
                        if_format_send_to=True,
                        ignored_types=ignored_types,
                    )
                else:
                    raise ValueError(f"Invalid post: {post}")

                if len(assistant_message) > 0:
                    chat_history.append(
                        format_chat_message(
                            role="assistant",
                            message=assistant_message,
                        ),
                    )
                if len(user_message) > 0:
                    chat_history.append(
                        format_chat_message(role="user", message=user_message),
                    )

        return chat_history

    @tracing_decorator
    def reply(
        self,
        memory: Memory,
        post_proxy: Optional[PostEventProxy] = None,
        prompt_log_path: Optional[str] = None,
        **kwargs: ...,
    ) -> Post:
        assert post_proxy is not None, "Post proxy is not provided."

        # extract all rounds from memory
        rounds = memory.get_role_rounds(
            role=self.alias,
            include_failure_rounds=False,
        )

        # obtain the query from the last round
        query = rounds[-1].post_list[-1].message

        self.tracing.set_span_attribute("query", query)
        self.tracing.set_span_attribute("use_experience", self.config.use_experience)

        self.role_load_experience(query=query, memory=memory)
        self.role_load_example(memory=memory, role_set={self.alias, "User", "CodeInterpreter"})

        prompt = self.compose_prompt(
            rounds,
        )

        self.tracing.set_span_attribute("prompt", json.dumps(prompt, indent=2))
        prompt_size = self.tracing.count_tokens(json.dumps(prompt))
        self.tracing.set_span_attribute("prompt_size", prompt_size)
        self.tracing.add_prompt_size(
            size=prompt_size,
            labels={
                "direction": "input",
            },
        )

        def early_stop(_type: AttachmentType, value: str) -> bool:
            if _type in [AttachmentType.init_plan, AttachmentType.plan, AttachmentType.current_plan_step]:
                return True
            else:
                return False

        self.post_translator.raw_text_to_post(
            llm_output=self.llm_api.chat_completion_stream(
                prompt,
                use_smoother=True,
                llm_alias=self.config.llm_alias,
                json_schema=self.response_json_schema,
            ),
            post_proxy=post_proxy,
            early_stop=early_stop,
        )

        # check if the post has a plan
        has_plan = False
        for attachment in post_proxy.post.attachment_list:
            if attachment.type == AttachmentType.plan:
                has_plan = True
                memory.add_shared_memory_entry(
                    entry_type=SharedMemoryEntryType("plan"),
                    content=attachment.content,
                )
                break

        # check if the post has a current plan step
        has_current_plan_step = False
        for attachment in post_proxy.post.attachment_list:
            if attachment.type == AttachmentType.current_plan_step:
                has_current_plan_step = True
                break

        # if the post has a plan but no current plan step, set the send_to to User
        if has_plan and not has_current_plan_step:
            post_proxy.update_send_to("User")
        # if the post has a current plan step, set the send_to to CodeInterpreter
        elif has_current_plan_step:
            post_proxy.update_send_to("CodeInterpreter")
        # otherwise, set the send_to to User
        else:
            post_proxy.update_send_to("User")

        if prompt_log_path is not None:
            self.logger.dump_prompt_file(prompt, prompt_log_path)

        return post_proxy.post

